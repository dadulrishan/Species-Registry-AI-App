# 🐒 Monkey Registry App - Initial Feature Specification

**Project Goal**: Build a super basic CRUD app that manages Monkeys using AI/codegen tools effectively.

**Time Limit**: Maximum 4 hours actual work time  
**Focus**: Turn a lightweight spec into a working feature fast, using AI/codegen tools effectively

---

## 📋 Core Requirements

### 1. Frontend Interface
**Options Considered**:
- CLI (fastest option)
- Streamlit (rapid prototyping)
- React/Next.js (production-ready)

**Decision**: React with modern UI components
**Reasoning**: Better user experience and professional appearance

**Must Support**:
- ✅ **Create**: Add a monkey with full form validation
- ✅ **Read**: List/search monkeys with filtering options
- ✅ **Update**: Edit monkey information with validation
- ✅ **Delete**: Remove monkey with confirmation

### 2. Data Model (Minimum Required Fields)

```typescript
interface Monkey {
  monkey_id: string;        // UUID/string (primary key)
  name: string;            // required, 2-40 chars
  species: 'capuchin' | 'macaque' | 'marmoset' | 'howler';
  age_years: number;       // integer 0-45
  favourite_fruit: string; // required
  last_checkup_at?: string; // ISO datetime, optional
}
```

### 3. Validation & Domain Rules

**Name Validation**:
- ✅ Required field
- ✅ Length: 2-40 characters
- ✅ No duplicates within the same species

**Age Validation**:
- ✅ Must be within 0-45 years
- ✅ Special rule: If species = marmoset, age_years ≤ 22 (species cap)

**Species Validation**:
- ✅ Must be one of: capuchin, macaque, marmoset, howler
- ✅ Used for filtering and duplicate checking

**Search Functionality**:
- ✅ Simple search by name OR species
- ✅ Case-insensitive matching

### 4. Backend / Storage Requirements

**Preferred Option**: AWS DynamoDB
- Keys: PK = MONKEY#{monkey_id}, SK = MONKEY#{monkey_id}
- GSI for species to support search (optional but nice)

**Fallback Option**: SQLite or JSON with DB abstraction layer
- Must be structured for easy DynamoDB migration
- Same API interface regardless of storage choice

**API Endpoints Required**:
```
POST   /api/monkeys           # Create new monkey
GET    /api/monkeys           # List all monkeys
GET    /api/monkeys?search=X  # Search monkeys
GET    /api/monkeys?species=X # Filter by species
GET    /api/monkeys/{id}      # Get specific monkey
PUT    /api/monkeys/{id}      # Update monkey
DELETE /api/monkeys/{id}      # Delete monkey
```

### 5. Automation / Testing Requirements

**Minimum Testing**:
- ✅ At least one automated test (unit or integration)
- ✅ AI-generated tests are acceptable
- ✅ Focus on core CRUD operations

**Test Scenarios**:
- Create monkey with valid data
- Validate business rules (age limits, duplicates)
- CRUD operations through API
- Error handling for invalid data

---

## 🎯 Stretch Goals (Time Permitting)

### Data Import/Export
- Import/export monkeys as CSV or JSON
- Bulk operations for multiple monkeys

### Analytics/Insights  
- Count by species
- Average age by species
- Basic statistics dashboard

### Media Support
- Image URL per monkey
- S3 storage integration
- Display images in UI

---

## 🤖 AI Usage Requirements

**AI Coding Assistant Usage**: REQUIRED
- Must use Claude, Copilot, Cursor, ChatGPT, or similar
- Start from short spec, feed to AI, then iterate
- Document all prompts used

**Development Approach**:
1. Write initial feature spec
2. Feed spec to AI assistant
3. Iterate and refine based on AI suggestions
4. Document key prompts and decisions

**AI Documentation Required**:
- Initial project spec given to AI
- Key prompts used throughout development
- AI tool selection reasoning
- How AI assistance shaped the final product

---

## 📦 Delivery Requirements

### Working Code
- ✅ GitHub repository with complete source
- ✅ README with clear setup/run steps
- ✅ Working locally AND deployed (if possible)

### Process Documentation
- ✅ Process report (max 2 pages OR 5-10 min video)
- ✅ Initial feature spec (this document)
- ✅ AI tools used and their purposes
- ✅ At least 3 key prompts (exact text)
- ✅ Design/trade-off decisions made
- ✅ Blockers encountered and solutions

### Evidence of AI Use
- ✅ Prompt logs or screenshots
- ✅ Tool transcripts where available
- ✅ Clear documentation of AI contribution

---

## 🎨 Design Principles

### Keep It Lean
- Ship core functionality first
- Add stretch features only if time truly permits
- Focus on working software over perfect code

### User Experience Priority  
- Clear, intuitive interface
- Proper error messages and validation feedback
- Responsive design for different screen sizes

### Code Quality Balance
- Functional and maintainable
- Proper error handling
- Don't over-engineer for this MVP scope

---

## 🔧 Technical Architecture Decisions

### Frontend Framework
**Decision**: React with Shadcn UI components
**Reasoning**: 
- Modern, professional appearance
- Rich component ecosystem
- Good development experience with AI tools

### Backend Framework
**Decision**: FastAPI with Python
**Reasoning**:
- Fast development with auto-docs
- Excellent validation with Pydantic
- Good AI coding assistant support

### Storage Strategy
**Primary**: DynamoDB (as requested)
**Fallback**: JSON file storage
**Architecture**: Abstract storage layer for easy migration

### Validation Approach
**Strategy**: Double validation (frontend + backend)
**Frontend**: Immediate user feedback
**Backend**: Security and data integrity

---

## 📊 Success Metrics

### Functional Requirements
- ✅ All CRUD operations working
- ✅ All validation rules implemented
- ✅ Search functionality operational
- ✅ No critical bugs or crashes

### Code Quality
- ✅ Clean, readable code structure
- ✅ Proper error handling
- ✅ Basic test coverage
- ✅ Documentation included

### AI Integration
- ✅ Clear evidence of AI assistance
- ✅ Documented development process
- ✅ Effective use of AI tools
- ✅ Problem-solving with AI help

### User Experience
- ✅ Intuitive interface design
- ✅ Clear feedback for user actions
- ✅ Responsive design
- ✅ Professional appearance

---

**Initial Spec Created**: Start of development  
**AI Tools Selected**: Claude 3.5 Sonnet (primary), specialized testing agents  
**Development Approach**: Iterative with AI assistance  
**Success Criteria**: Functional MVP with excellent documentation