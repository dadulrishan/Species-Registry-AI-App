from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
import json
from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import uuid
from datetime import datetime
from enum import Enum


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# JSON file storage setup (fallback from DynamoDB due to permission issues)
DATA_FILE = ROOT_DIR / 'monkeys_data.json'

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Species Enum
class Species(str, Enum):
    CAPUCHIN = "capuchin"
    MACAQUE = "macaque"
    MARMOSET = "marmoset"
    HOWLER = "howler"


# Pydantic Models
class MonkeyCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=40)
    species: Species
    age_years: int = Field(..., ge=0, le=45)
    favourite_fruit: str
    last_checkup_at: Optional[str] = None

    @validator('age_years')
    def validate_marmoset_age(cls, v, values):
        if values.get('species') == Species.MARMOSET and v > 22:
            raise ValueError('Marmoset age cannot exceed 22 years')
        return v


class MonkeyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=40)
    species: Optional[Species] = None
    age_years: Optional[int] = Field(None, ge=0, le=45)
    favourite_fruit: Optional[str] = None
    last_checkup_at: Optional[str] = None

    @validator('age_years')
    def validate_marmoset_age(cls, v, values):
        if values.get('species') == Species.MARMOSET and v and v > 22:
            raise ValueError('Marmoset age cannot exceed 22 years')
        return v


class Monkey(BaseModel):
    monkey_id: str
    name: str
    species: Species
    age_years: int
    favourite_fruit: str
    last_checkup_at: Optional[str] = None
    created_at: str
    updated_at: str


# JSON Storage Functions
def load_monkeys_data():
    """Load monkeys data from JSON file"""
    if not DATA_FILE.exists():
        return {}
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return {}


def save_monkeys_data(data):
    """Save monkeys data to JSON file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        raise HTTPException(status_code=500, detail="Error saving data")


# Helper functions
async def check_name_duplicate(name: str, species: str, exclude_monkey_id: str = None):
    """Check if a monkey with the same name and species already exists"""
    try:
        data = load_monkeys_data()
        for monkey_id, monkey in data.items():
            if (monkey['name'].lower() == name.lower() and 
                monkey['species'] == species and 
                (exclude_monkey_id is None or monkey_id != exclude_monkey_id)):
                return True
        return False
    except Exception as e:
        logger.error(f"Error checking duplicates: {e}")
        return False


# API Routes
@api_router.get("/")
async def root():
    return {"message": "Monkey Registry API"}


@api_router.post("/monkeys", response_model=Monkey, status_code=201)
async def create_monkey(monkey_data: MonkeyCreate):
    """Create a new monkey"""
    # Check for duplicate name within species
    if await check_name_duplicate(monkey_data.name, monkey_data.species.value):
        raise HTTPException(
            status_code=400, 
            detail=f"A monkey named '{monkey_data.name}' already exists in species '{monkey_data.species.value}'"
        )

    # Generate unique ID
    monkey_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    # Create monkey record
    monkey_record = {
        'monkey_id': monkey_id,
        'name': monkey_data.name,
        'species': monkey_data.species.value,
        'age_years': monkey_data.age_years,
        'favourite_fruit': monkey_data.favourite_fruit,
        'last_checkup_at': monkey_data.last_checkup_at,
        'created_at': now,
        'updated_at': now
    }

    try:
        # Load existing data
        data = load_monkeys_data()
        data[monkey_id] = monkey_record
        save_monkeys_data(data)
        
        return Monkey(**monkey_record)
    except Exception as e:
        logger.error(f"Error creating monkey: {e}")
        raise HTTPException(status_code=500, detail="Error creating monkey")


@api_router.get("/monkeys", response_model=List[Monkey])
async def list_monkeys(species: Optional[str] = None, search: Optional[str] = None):
    """List all monkeys with optional filtering"""
    try:
        data = load_monkeys_data()
        monkeys = []
        
        for monkey_record in data.values():
            # Species filtering
            if species and monkey_record['species'] != species:
                continue
                
            # Search filtering
            if search:
                search_lower = search.lower()
                if (search_lower not in monkey_record['name'].lower() and 
                    search_lower not in monkey_record['species'].lower()):
                    continue
            
            monkeys.append(Monkey(**monkey_record))

        return monkeys
    except Exception as e:
        logger.error(f"Error listing monkeys: {e}")
        raise HTTPException(status_code=500, detail="Error fetching monkeys")


@api_router.get("/monkeys/{monkey_id}", response_model=Monkey)
async def get_monkey(monkey_id: str):
    """Get a specific monkey by ID"""
    try:
        data = load_monkeys_data()
        if monkey_id not in data:
            raise HTTPException(status_code=404, detail="Monkey not found")
        
        return Monkey(**data[monkey_id])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting monkey: {e}")
        raise HTTPException(status_code=500, detail="Error fetching monkey")


@api_router.put("/monkeys/{monkey_id}", response_model=Monkey)
async def update_monkey(monkey_id: str, updates: MonkeyUpdate):
    """Update an existing monkey"""
    try:
        data = load_monkeys_data()
        if monkey_id not in data:
            raise HTTPException(status_code=404, detail="Monkey not found")
        
        existing_monkey = data[monkey_id]
        
        # Check for name duplicate if name or species is being updated
        update_dict = updates.dict(exclude_unset=True)
        if 'name' in update_dict or 'species' in update_dict:
            new_name = update_dict.get('name', existing_monkey['name'])
            new_species = update_dict.get('species', existing_monkey['species'])
            if await check_name_duplicate(new_name, new_species, monkey_id):
                raise HTTPException(
                    status_code=400, 
                    detail=f"A monkey named '{new_name}' already exists in species '{new_species}'"
                )

        # Update the monkey
        for key, value in update_dict.items():
            if value is not None:
                existing_monkey[key] = value
        
        existing_monkey['updated_at'] = datetime.utcnow().isoformat()
        
        # Save updated data
        data[monkey_id] = existing_monkey
        save_monkeys_data(data)
        
        return Monkey(**existing_monkey)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating monkey: {e}")
        raise HTTPException(status_code=500, detail="Error updating monkey")


@api_router.delete("/monkeys/{monkey_id}")
async def delete_monkey(monkey_id: str):
    """Delete a monkey by ID"""
    try:
        data = load_monkeys_data()
        if monkey_id not in data:
            raise HTTPException(status_code=404, detail="Monkey not found")

        # Delete the monkey
        del data[monkey_id]
        save_monkeys_data(data)
        
        return {"message": "Monkey deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting monkey: {e}")
        raise HTTPException(status_code=500, detail="Error deleting monkey")


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)