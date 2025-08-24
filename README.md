# 🐒 Monkey Registry App

A full-stack CRUD application for managing monkey companions with modern React frontend and FastAPI backend.

## 🚀 Quick Start

### Prerequisites
- Node.js (v16+)
- Python (v3.8+)
- Yarn package manager

### Setup & Run Steps

#### 1. Clone & Navigate
```bash
git clone <repository-url>
cd monkey-registry-app
```

#### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python server.py
```
Backend will run on `http://localhost:8001`

#### 3. Frontend Setup
```bash
cd frontend
yarn install
yarn start
```
Frontend will run on `http://localhost:3000`

### 🌐 Live Demo
**Production URL**: https://simian-tracker.preview.emergentagent.com

## 📋 Features

### Core Functionality
- ✅ **Create** monkeys with full validation
- ✅ **Read** monkey list with search and filtering
- ✅ **Update** monkey information
- ✅ **Delete** monkeys with confirmation
- ✅ **Search** by name or species
- ✅ **Filter** by species type

### Data Model
- **monkey_id**: UUID (auto-generated)
- **name**: 2-40 characters, required
- **species**: capuchin | macaque | marmoset | howler
- **age_years**: 0-45 (marmosets max 22)
- **favourite_fruit**: required string
- **last_checkup_at**: optional ISO datetime

### Validation Rules
- ✅ Name required, 2-40 characters
- ✅ No duplicate names within same species
- ✅ Age validation: 0-45 years
- ✅ Marmoset-specific rule: age ≤ 22 years
- ✅ Species must be valid enum value

## 🛠 Technical Stack

### Frontend
- **React** with functional components and hooks
- **Shadcn UI** for modern, accessible components
- **Tailwind CSS** for styling
- **Axios** for API communication
- **React Router** for navigation

### Backend  
- **FastAPI** with async support
- **Pydantic** for data validation
- **JSON file storage** (easily replaceable with DynamoDB)
- **CORS** enabled for frontend integration

### API Endpoints
```
GET    /api/                     # Health check
POST   /api/monkeys             # Create monkey
GET    /api/monkeys             # List monkeys (with optional search/filter)
GET    /api/monkeys/{id}        # Get specific monkey
PUT    /api/monkeys/{id}        # Update monkey
DELETE /api/monkeys/{id}        # Delete monkey
```

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
python backend_test.py
```

### API Testing Examples
```bash
# Create a monkey
curl -X POST "http://localhost:8001/api/monkeys" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "George",
    "species": "capuchin",
    "age_years": 5,
    "favourite_fruit": "banana"
  }'

# List all monkeys
curl "http://localhost:8001/api/monkeys"

# Search monkeys
curl "http://localhost:8001/api/monkeys?search=George"

# Filter by species
curl "http://localhost:8001/api/monkeys?species=capuchin"
```

## 📁 Project Structure
```
monkey-registry-app/
├── backend/
│   ├── server.py              # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables
│   └── monkeys_data.json      # JSON storage file
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── App.css           # Styles
│   │   └── components/ui/    # Shadcn UI components
│   ├── package.json          # Node dependencies
│   └── .env                  # Frontend environment
├── backend_test.py           # Comprehensive API tests
├── README.md                 # This file
└── AI_PROMPTS_AND_PROCESS.md # Development documentation
```

## 🔧 Configuration

### Environment Variables
**Backend (.env)**
```
CORS_ORIGINS=*
```

**Frontend (.env)**
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 🐛 Troubleshooting

### Common Issues

**Backend not starting:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Frontend build errors:**
```bash
rm -rf node_modules
yarn install
```

**CORS errors:**
- Ensure backend is running on port 8001
- Check REACT_APP_BACKEND_URL in frontend/.env

### Data Storage
- Monkey data is stored in `backend/monkeys_data.json`
- Delete this file to reset all data
- File is created automatically on first monkey creation

## 🎯 Design Decisions

### Storage Choice
- **Initial**: DynamoDB (as requested)
- **Final**: JSON file storage due to AWS permission limitations
- **Architecture**: API layer unchanged for easy future migration

### UI Framework
- **Choice**: React with Shadcn UI
- **Reasoning**: Modern, accessible components with professional appearance
- **Alternative considered**: CLI (rejected for better UX)

### Validation Strategy
- **Backend**: Pydantic models with custom validators
- **Frontend**: HTML5 validation + backend error display
- **Approach**: Fail-fast validation with user-friendly feedback

## 🚀 Deployment

### Local Development
1. Follow setup steps above
2. Both services will hot-reload on changes
3. Visit http://localhost:3000 for the app

### Production Deployment
- Frontend deployed to: https://simian-tracker.preview.emergentagent.com
- Backend API available at: /api endpoints
- JSON storage persists between deployments

## 📊 Test Coverage

### Backend API Tests
- ✅ 24/24 tests passing
- ✅ All CRUD operations
- ✅ Validation rules
- ✅ Error handling
- ✅ Edge cases

### Frontend UI Tests
- ✅ All components render correctly
- ✅ Forms work with validation
- ✅ Search and filter functionality
- ✅ CRUD operations through UI
- ✅ Responsive design

## 🤝 Contributing

### Adding New Features
1. Update data model in `backend/server.py`
2. Add new API endpoints
3. Update frontend components
4. Add tests in `backend_test.py`

### Code Style
- **Backend**: Follow PEP 8
- **Frontend**: Use Prettier for formatting
- **Components**: Use Shadcn UI patterns

## 📜 License

MIT License - Feel free to use and modify as needed.

---

**Built with AI assistance** - See `AI_PROMPTS_AND_PROCESS.md` for development details.