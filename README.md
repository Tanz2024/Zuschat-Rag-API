# ZUS Coffee AI Chatbot

A comprehensive full-stack AI chatbot application for ZUS Coffee with RAG (Retrieval-Augmented Generation) capabilities, product search, outlet finder, and intelligent conversation management.

##  Features

### Backend (FastAPI)
- **Conversational AI**: Advanced state management with memory and context
- **RAG Integration**: Vector-based product knowledge base using FAISS
- **Tool Integration**: Calculator, Product search, Outlet finder with Text2SQL
- **Web Scraping**: Automated ZUS product and outlet data collection
- **Security**: SQL injection protection and comprehensive error handling
- **Real-time Chat**: WebSocket support for instant messaging

### Frontend (Next.js)
- **Modern UI**: Responsive design with dark/light mode support
- **Real-time Chat**: Seamless integration with backend API
- **Product Discovery**: Interactive product browsing and search
- **Outlet Finder**: Location-based outlet discovery
- **Smart Suggestions**: Context-aware prompt suggestions
- **Mobile-First**: Optimized for all device sizes

##  Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install spaCy model:**
```bash
python -m spacy download en_core_web_sm
```

4. **Install Playwright browsers:**
```bash
playwright install
```

5. **Start the backend server:**
```bash
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start the development server:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

##  Project Structure

```
zuschat-rag-api/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── agents/
│   │   └── controller.py       # Main agent logic and orchestration
│   ├── chatbot/
│   │   └── agent.py           # Core chatbot functionality
│   ├── data/
│   │   ├── database.py        # Database configuration
│   │   ├── outlets.db         # SQLite database for outlets
│   │   ├── products.json      # Product data
│   │   ├── products.faiss     # FAISS vector index
│   │   └── products_meta.pkl  # Product metadata
│   ├── scrapers/
│   │   ├── outlet_scraper.py  # Outlet data scraping
│   │   └── product_scraper.py # Product data scraping
│   ├── services/
│   │   ├── product_search_service.py    # Product search logic
│   │   └── real_data_outlet_filter.py   # Outlet filtering
│   ├── tools/
│   │   └── calculator.py      # Calculator functionality
│   ├── requirements.txt       # Python dependencies
│   └── start_backend.bat     # Windows startup script
├── frontend/
│   ├── components/
│   │   ├── ChatWindow.tsx     # Main chat interface
│   │   ├── Header.tsx         # App header with branding
│   │   ├── MessageBubble.tsx  # Individual message display
│   │   ├── MessageInput.tsx   # Message input component
│   │   ├── ProductCard.tsx    # Product display card
│   │   ├── Sidebar.tsx        # Navigation and suggestions
│   │   ├── SuggestedPrompts.tsx # Smart prompt suggestions
│   │   ├── ThemeProvider.tsx  # Dark/light mode provider
│   │   ├── Toast.tsx          # Notification system
│   │   └── TypingIndicator.tsx # Typing animation
│   ├── hooks/
│   │   ├── useChat.ts         # Chat state management
│   │   └── useTheme.ts        # Theme management
│   ├── lib/
│   │   └── suggestedPrompts.ts # Prompt suggestion logic
│   ├── pages/
│   │   ├── api/
│   │   │   └── chat.ts        # Next.js API route
│   │   ├── _app.tsx           # App wrapper
│   │   ├── _document.tsx      # HTML document structure
│   │   └── index.tsx          # Main page
│   ├── public/
│   │   └── assets/            # Static assets and logos
│   ├── styles/
│   │   └── globals.css        # Global styles with Tailwind
│   ├── package.json           # Node.js dependencies
│   ├── next.config.js         # Next.js configuration
│   ├── tailwind.config.js     # Tailwind CSS configuration
│   └── tsconfig.json          # TypeScript configuration
└── README.md                  # This file
```

##  API Documentation

###  Complete API Specification
For comprehensive API documentation, testing examples, and Postman collections, see:

**[ Full API Specification](./docs/API_SPECIFICATION.md)**

### Quick API Overview

#### Backend Endpoints
- `POST /chat` - Main chatbot conversation interface
- `GET /products` - Product knowledge base search  
- `GET /outlets` - Outlet information retrieval
- `POST /calculate` - Calculator tool functionality
- `GET /health` - Service health check
- `GET /docs` - Interactive Swagger documentation
- `GET /redoc` - ReDoc API documentation

#### Key Statistics (Real Data)
- **Total KL Outlets**: 80
- **Total Selangor Outlets**: 132  
- **Total Products**: ~150 items
- **Supported Services**: Dine-in, Takeaway, Delivery, Drive-thru, WiFi, 24-hour

#### Quick Test Examples

**Health Check:**
```bash
curl -X GET "http://localhost:8000/health"
```

**Chat with the Bot:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How many outlets in Kuala Lumpur?", "session_id": "test123"}'
```

**Search Products:**
```bash
curl -X GET "http://localhost:8000/products?query=iced%20coffee&top_k=5"
```

**Find Outlets:**
```bash
curl -X GET "http://localhost:8000/outlets?query=outlets%20in%20kuala%20lumpur"
```

### Interactive Documentation
When the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Frontend API Routes
- `POST /api/chat` - Next.js API proxy to backend

###  Complete Documentation Suite

####  Architecture & Technical Documentation
- **[System Architecture](./docs/ARCHITECTURE.md)** - Complete system design, flow diagrams, and component details
- **[RAG & Text2SQL Implementation](./docs/RAG_TEXT2SQL_IMPLEMENTATION.md)** - Deep dive into AI engines and implementation details

####  Testing & Quality Assurance  
- **[Production Testing Guide](./docs/PRODUCTION_TESTING.md)** - Comprehensive testing scenarios and validation
- **[PowerShell Testing Commands](./docs/POWERSHELL_API_TESTING.md)** - Windows-specific API testing examples
- **[Automated Test Suite](./docs/run_production_tests.ps1)** - Production-ready automated testing script

####  Quick Testing Commands
```powershell
# Run complete production test suite
.\docs\run_production_tests.ps1

# Health check
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get

# Test KL outlets (should return 80)
Invoke-RestMethod -Uri "http://localhost:8000/outlets?query=kuala%20lumpur" -Method Get

# Test Selangor outlets (should return 132)  
Invoke-RestMethod -Uri "http://localhost:8000/outlets?query=selangor" -Method Get
```

##  Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQLite with SQLAlchemy
- **Vector Search**: FAISS
- **Web Scraping**: Playwright, BeautifulSoup4
- **NLP**: spaCy
- **HTTP Client**: httpx

### Frontend
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **State Management**: React Hooks

##  Environment Configuration

### Backend (.env)
```env
# Database
DATABASE_URL=sqlite:///./data/outlets.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Frontend (.env.local)
```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

##  Production Deployment

### Backend Production
```bash
cd backend
pip install -r requirements.txt
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Production
```bash
cd frontend
npm run build
npm start
```

##  Development Features

- **Hot Reload**: Automatic reloading for both frontend and backend
- **Type Safety**: Full TypeScript support
- **Error Handling**: Comprehensive error boundaries and logging
- **Responsive Design**: Mobile-first approach
- **Accessibility**: ARIA labels and keyboard navigation
- **Performance**: Optimized bundle sizes and lazy loading

##  Core Functionality

### 1. Intelligent Conversations
- Context-aware responses based on ZUS Coffee data
- Memory management for conversation continuity
- Multi-turn conversation support

### 2. Product Discovery
- Vector-based product search
- Product recommendations
- Real-time inventory information

### 3. Outlet Finding
- Location-based outlet search
- Operating hours and services information
- Directions and contact details

### 4. Smart Tools
- Price calculator for custom orders
- Nutritional information lookup
- Menu customization assistance

##  Design System

- **Brand Colors**: ZUS Coffee blue (#0057FF) as primary
- **Typography**: Modern, readable fonts
- **Spacing**: Consistent 8px grid system
- **Components**: Reusable, accessible components
- **Animations**: Smooth transitions and micro-interactions

##  Getting Started for Development

1. **Clone the repository**
2. **Set up backend** (see Backend Setup above)
3. **Set up frontend** (see Frontend Setup above)
4. **Open `http://localhost:3000`** in your browser
5. **Start chatting** with the ZUS Coffee AI assistant!

##  License

This project is developed for ZUS Coffee and contains proprietary business logic and branding.

---

**Built with ❤ for ZUS Coffee - Brew With Love**
