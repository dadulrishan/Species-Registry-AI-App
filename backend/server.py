from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import boto3
from boto3.dynamodb.conditions import Key, Attr
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import uuid
from datetime import datetime
from enum import Enum


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# AWS DynamoDB setup
aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
aws_region = os.environ['AWS_REGION']
table_name = os.environ['DYNAMODB_TABLE_NAME']

# Initialize DynamoDB client
dynamodb = boto3.resource(
    'dynamodb',
    region_name=aws_region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

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


# Initialize DynamoDB table
def get_table():
    try:
        table = dynamodb.Table(table_name)
        # Check if table exists, create if it doesn't
        table.load()
        return table
    except Exception as e:
        logger.error(f"Error accessing table: {e}")
        # Create table if it doesn't exist
        try:
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': 'PK',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'SK',
                        'KeyType': 'RANGE'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'PK',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'SK',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'species',
                        'AttributeType': 'S'
                    }
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'species-index',
                        'KeySchema': [
                            {
                                'AttributeName': 'species',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'BillingMode': 'PAY_PER_REQUEST'
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            table.wait_until_exists()
            return table
        except Exception as create_error:
            logger.error(f"Error creating table: {create_error}")
            raise HTTPException(status_code=500, detail="Database setup error")


# Helper functions
async def check_name_duplicate(name: str, species: str, exclude_monkey_id: str = None):
    """Check if a monkey with the same name and species already exists"""
    table = get_table()
    try:
        response = table.scan(
            FilterExpression=Attr('name').eq(name) & Attr('species').eq(species)
        )
        for item in response['Items']:
            if exclude_monkey_id is None or item['monkey_id'] != exclude_monkey_id:
                return True
        return False
    except Exception as e:
        logger.error(f"Error checking duplicates: {e}")
        return False


# API Routes
@api_router.get("/")
async def root():
    return {"message": "Monkey Registry API"}


@api_router.post("/monkeys", response_model=Monkey)
async def create_monkey(monkey_data: MonkeyCreate):
    """Create a new monkey"""
    table = get_table()

    # Check for duplicate name within species
    if await check_name_duplicate(monkey_data.name, monkey_data.species.value):
        raise HTTPException(
            status_code=400, 
            detail=f"A monkey named '{monkey_data.name}' already exists in species '{monkey_data.species.value}'"
        )

    # Generate unique ID
    monkey_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    # Prepare item for DynamoDB
    item = {
        'PK': f'MONKEY#{monkey_id}',
        'SK': f'MONKEY#{monkey_id}',
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
        table.put_item(Item=item)
        return Monkey(**item)
    except Exception as e:
        logger.error(f"Error creating monkey: {e}")
        raise HTTPException(status_code=500, detail="Error creating monkey")


@api_router.get("/monkeys", response_model=List[Monkey])
async def list_monkeys(species: Optional[str] = None, search: Optional[str] = None):
    """List all monkeys with optional filtering"""
    table = get_table()

    try:
        if species:
            # Use GSI to filter by species
            response = table.query(
                IndexName='species-index',
                KeyConditionExpression=Key('species').eq(species)
            )
        else:
            # Scan all items
            response = table.scan(
                FilterExpression=Attr('PK').begins_with('MONKEY#')
            )

        monkeys = []
        for item in response['Items']:
            # Additional search filtering if provided
            if search:
                search_lower = search.lower()
                if (search_lower not in item['name'].lower() and 
                    search_lower not in item['species'].lower()):
                    continue
            
            monkeys.append(Monkey(**item))

        return monkeys
    except Exception as e:
        logger.error(f"Error listing monkeys: {e}")
        raise HTTPException(status_code=500, detail="Error fetching monkeys")


@api_router.get("/monkeys/{monkey_id}", response_model=Monkey)
async def get_monkey(monkey_id: str):
    """Get a specific monkey by ID"""
    table = get_table()

    try:
        response = table.get_item(
            Key={
                'PK': f'MONKEY#{monkey_id}',
                'SK': f'MONKEY#{monkey_id}'
            }
        )
        
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Monkey not found")
        
        return Monkey(**response['Item'])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting monkey: {e}")
        raise HTTPException(status_code=500, detail="Error fetching monkey")


@api_router.put("/monkeys/{monkey_id}", response_model=Monkey)
async def update_monkey(monkey_id: str, updates: MonkeyUpdate):
    """Update an existing monkey"""
    table = get_table()

    # First, get the existing monkey
    try:
        response = table.get_item(
            Key={
                'PK': f'MONKEY#{monkey_id}',
                'SK': f'MONKEY#{monkey_id}'
            }
        )
        
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Monkey not found")
        
        existing_monkey = response['Item']
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting existing monkey: {e}")
        raise HTTPException(status_code=500, detail="Error updating monkey")

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
    try:
        # Prepare update expression
        update_expression = "SET updated_at = :updated_at"
        expression_values = {':updated_at': datetime.utcnow().isoformat()}
        
        for key, value in update_dict.items():
            if value is not None:
                update_expression += f", {key} = :{key}"
                expression_values[f':{key}'] = value

        table.update_item(
            Key={
                'PK': f'MONKEY#{monkey_id}',
                'SK': f'MONKEY#{monkey_id}'
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )

        # Get updated monkey
        response = table.get_item(
            Key={
                'PK': f'MONKEY#{monkey_id}',
                'SK': f'MONKEY#{monkey_id}'
            }
        )
        
        return Monkey(**response['Item'])
    except Exception as e:
        logger.error(f"Error updating monkey: {e}")
        raise HTTPException(status_code=500, detail="Error updating monkey")


@api_router.delete("/monkeys/{monkey_id}")
async def delete_monkey(monkey_id: str):
    """Delete a monkey by ID"""
    table = get_table()

    try:
        # Check if monkey exists first
        response = table.get_item(
            Key={
                'PK': f'MONKEY#{monkey_id}',
                'SK': f'MONKEY#{monkey_id}'
            }
        )
        
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Monkey not found")

        # Delete the monkey
        table.delete_item(
            Key={
                'PK': f'MONKEY#{monkey_id}',
                'SK': f'MONKEY#{monkey_id}'
            }
        )
        
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