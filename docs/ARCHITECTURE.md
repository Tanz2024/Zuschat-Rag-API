# ZUS Chatbot Architecture Documentation

## 🏗️ System Architecture Overview

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           ZUS Coffee AI Chatbot System                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Frontend (Next.js)           │           Backend (FastAPI)                    │
│  ┌─────────────────────────┐   │   ┌─────────────────────────────────────────┐   │
│  │ React Components        │   │   │ API Endpoints                           │   │
│  │ • ChatWindow           │   │   │ • /chat (Main conversation)            │   │
│  │ • MessageBubble        │   │   │ • /products (Vector search)            │   │
│  │ • ThemeProvider        │   │   │ • /outlets (Text2SQL)                  │   │
│  │ • Toast Notifications  │◄──┼──►│ • /calculate (Math operations)          │   │
│  │                        │   │   │ • /health (System status)              │   │
│  └─────────────────────────┘   │   └─────────────────────────────────────────┘   │
│           │                    │                      │                         │
│           │ HTTP/API Calls     │                      │                         │
│           │                    │                      ▼                         │
│  ┌─────────────────────────┐   │   ┌─────────────────────────────────────────┐   │
│  │ API Routes (/api)       │   │   │ Agent Controller                        │   │
│  │ • chat.ts (Proxy)      │   │   │ • Intent Classification                │   │
│  │                        │   │   │ • Context Management                   │   │
│  └─────────────────────────┘   │   │ • Tool Orchestration                  │   │
│                                │   │ • Response Generation                  │   │
│                                │   └─────────────────────────────────────────┘   │
│                                │                      │                         │
│                                │                      ▼                         │
│                                │   ┌─────────────────────────────────────────┐   │
│                                │   │ AI Services & Tools                     │   │
│                                │   │ ┌─────────────┬─────────────┬─────────┐ │   │
│                                │   │ │RAG Engine   │Text2SQL     │Calculator│ │   │
│                                │   │ │             │             │         │ │   │
│                                │   │ │• Vector DB  │• SQL Query  │• SymPy  │ │   │
│                                │   │ │• FAISS      │• Generation │• Math   │ │   │
│                                │   │ │• Embeddings │• Validation │• Logic  │ │   │
│                                │   │ └─────────────┴─────────────┴─────────┘ │   │
│                                │   └─────────────────────────────────────────┘   │
│                                │                      │                         │
│                                │                      ▼                         │
│                                │   ┌─────────────────────────────────────────┐   │
│                                │   │ Data Layer                              │   │
│                                │   │ ┌─────────────┬─────────────┬─────────┐ │   │
│                                │   │ │Products     │Outlets DB   │Sessions │ │   │
│                                │   │ │Vector Store │(SQLite)     │Memory   │ │   │
│                                │   │ │(FAISS)      │• 80 KL      │Manager  │ │   │
│                                │   │ │• 150 items  │• 132 Selangor│        │ │   │
│                                │   │ └─────────────┴─────────────┴─────────┘ │   │
│                                │   └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 Conversation Flow Diagram

```
┌─────────────┐
│ User Input  │
└─────┬───────┘
      │
      ▼
┌─────────────────────────┐
│ Intent Classification   │
│ • Product Search        │
│ • Outlet Search         │
│ • Calculation          │
│ • General Chat         │
└─────┬───────────────────┘
      │
      ▼
┌─────────────────────────┐
│ Context Enrichment      │
│ • Session History       │
│ • User Preferences      │
│ • Location Context      │
└─────┬───────────────────┘
      │
      ▼
┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐
│ RAG Engine              │    │ Text2SQL Engine         │    │ Calculator Tool         │
│ • Query Embedding       │    │ • NL to SQL             │    │ • Expression Parsing    │
│ • Vector Search         │    │ • Query Validation      │    │ • Math Operations       │
│ • Product Retrieval     │    │ • DB Execution          │    │ • Result Formatting     │
└─────┬───────────────────┘    └─────┬───────────────────┘    └─────┬───────────────────┘
      │                              │                              │
      ▼                              ▼                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ Response Generation                                                             │
│ • Combine Retrieved Data                                                        │
│ • Format User-Friendly Response                                                 │
│ • Add Suggestions & Follow-ups                                                  │
│ • Update Conversation Context                                                   │
└─────┬───────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────┐
│ User Output │
└─────────────┘
```

## 🤖 RAG (Retrieval-Augmented Generation) Flow

```
┌─────────────────────────┐
│ User Query              │
│ "What coffee drinks     │
│  do you have?"          │
└─────┬───────────────────┘
      │
      ▼
┌─────────────────────────┐
│ Query Processing        │
│ • Tokenization          │
│ • Normalization         │
│ • Intent Detection      │
└─────┬───────────────────┘
      │
      ▼
┌─────────────────────────┐
│ Embedding Generation    │
│ Model: all-MiniLM-L6-v2 │
│ Dimension: 384          │
└─────┬───────────────────┘
      │
      ▼
┌─────────────────────────┐
│ Vector Search (FAISS)   │
│ • Cosine Similarity     │
│ • Top-K Retrieval       │
│ • Relevance Scoring     │
└─────┬───────────────────┘
      │
      ▼
┌─────────────────────────┐
│ Product Retrieval       │
│ From 150+ Products:     │
│ • Coffee drinks         │
│ • Tea & beverages       │
│ • Food items            │
│ • Pastries & snacks     │
└─────┬───────────────────┘
      │
      ▼
┌─────────────────────────┐
│ Response Generation     │
│ • Format product info   │
│ • Add prices & details  │
│ • Generate suggestions  │
└─────┬───────────────────┘
      │
      ▼
┌─────────────────────────┐
│ Structured Response     │
│ {                       │
│   "products": [...],    │
│   "message": "...",     │
│   "suggestions": [...]  │
│ }                       │
└─────────────────────────┘
```

## 🗃️ Text2SQL Flow for Outlet Queries

```
┌─────────────────────────┐
│ User Query              │
│ "Find outlets in        │
│  Kuala Lumpur"          │
└─────┬───────────────────┘
      │
      ▼
┌─────────────────────────┐
│ Query Analysis          │
│ • Location extraction   │
│ • Service filtering     │
│ • Landmark detection    │
└─────┬───────────────────┘
      │
      ▼
┌─────────────────────────┐
│ SQL Generation          │
│ Pattern Matching:       │
│ • kuala lumpur → LIKE   │
│ • drive-thru → services │
│ • mid valley → name     │
└─────┬───────────────────┘
      │
      ▼
┌─────────────────────────┐
│ Query Validation        │
│ • SQL injection check   │
│ • Parameter validation  │
│ • Result limit (50)     │
└─────┬───────────────────┘
      │
      ▼
┌─────────────────────────┐
│ Database Execution      │
│ SQLite Query:           │
│ SELECT * FROM outlets   │
│ WHERE address LIKE      │
│ '%kuala lumpur%'        │
│ ORDER BY name LIMIT 50  │
└─────┬───────────────────┘
      │
      ▼
┌─────────────────────────┐
│ Result Processing       │
│ • Format outlet data    │
│ • Show top 10 + count   │
│ • Total: 80 KL outlets  │
└─────┬───────────────────┘
      │
      ▼
┌─────────────────────────┐
│ Response Formatting     │
│ "🏪 Found 80 outlets    │
│  in Kuala Lumpur:       │
│  1. ZUS Coffee KLCC..." │
└─────────────────────────┘
```

## 📊 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                Data Sources                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│ │ Product Data    │  │ Outlet Data     │  │ Conversation    │  │ User Session│ │
│ │ • JSON Format   │  │ • SQLite DB     │  │ • Memory Store  │  │ • Context   │ │
│ │ • 150+ items    │  │ • 212 outlets   │  │ • Chat History  │  │ • State     │ │
│ │ • Categories    │  │ • Real addresses│  │ • Intent Track  │  │ • Prefs     │ │
│ └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            Processing Layer                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│ │ Vector Store    │  │ SQL Engine      │  │ Session Manager │  │ Calculator  │ │
│ │ • FAISS Index   │  │ • Query Builder │  │ • Memory Mgmt   │  │ • SymPy     │ │
│ │ • Embeddings    │  │ • Validation    │  │ • Context Track │  │ • Expression│ │
│ │ • Similarity    │  │ • Execution     │  │ • Cleanup       │  │ • Parser    │ │
│ └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              API Layer                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│ │ Chat Endpoint   │  │ Product Search  │  │ Outlet Search   │  │ Calculator  │ │
│ │ • /chat         │  │ • /products     │  │ • /outlets      │  │ • /calculate│ │
│ │ • Orchestration │  │ • Vector Query  │  │ • SQL Query     │  │ • Math Ops  │ │
│ │ • Response Gen  │  │ • RAG Results   │  │ • Location Data │  │ • Results   │ │
│ └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            Frontend UI                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│ │ Chat Interface  │  │ Product Display │  │ Outlet Results  │  │ UI Controls │ │
│ │ • Message Bubbles│  │ • Product Cards │  │ • Location Info │  │ • Theme     │ │
│ │ • Typing Indicator│ │ • Price Display │  │ • Contact Details│ │ • Settings  │ │
│ │ • Suggestions   │  │ • Categories    │  │ • Maps/Directions│ │ • History   │ │
│ └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🎯 Intent Classification Flow

```
┌─────────────────────────┐
│ User Message            │
│ "Calculate 15 * 2 + 5"  │
└─────┬───────────────────┘
      │
      ▼
┌─────────────────────────┐
│ Pattern Analysis        │
│ • Keyword Detection     │
│ • Regular Expressions   │
│ • Context Evaluation    │
└─────┬───────────────────┘
      │
      ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│ Intent Patterns         │     │ Confidence Scoring      │
│ • "calculate" →         │     │ • Mathematical: 0.95    │
│   CALCULATION          │     │ • Product: 0.05         │
│ • "outlets" →          │     │ • Outlet: 0.02          │
│   OUTLET_SEARCH        │     │ • General: 0.08         │
│ • "coffee" →           │     │                         │
│   PRODUCT_SEARCH       │     │                         │
└─────┬───────────────────┘     └─────┬───────────────────┘
      │                               │
      └───────────────┬───────────────┘
                      │
                      ▼
┌─────────────────────────┐
│ Action Selection        │
│ Intent: CALCULATION     │
│ Action: CALL_CALCULATOR │
│ Confidence: 0.95        │
└─────┬───────────────────┘
      │
      ▼
┌─────────────────────────┐
│ Tool Execution          │
│ Calculator.calculate()  │
│ Expression: "15*2+5"    │
│ Result: 35              │
└─────┬───────────────────┘
      │
      ▼
┌─────────────────────────┐
│ Response Generation     │
│ "The result is 35"      │
└─────────────────────────┘
```

## 🔧 System Components Detail

### 1. Frontend Components (Next.js)
```
components/
├── ChatWindow.tsx          # Main chat interface container
├── MessageBubble.tsx       # Individual message rendering
├── MessageInput.tsx        # User input with suggestions
├── ProductCard.tsx         # Product information display
├── Sidebar.tsx            # Navigation and quick actions
├── ThemeProvider.tsx      # Dark/light mode management
├── Toast.tsx              # Success/error notifications
└── TypingIndicator.tsx    # AI thinking animation
```

### 2. Backend Services (FastAPI)
```
services/
├── product_search_service.py    # RAG engine with FAISS
├── real_data_outlet_filter.py   # Text2SQL for outlets
└── calculator.py               # Mathematical operations

agents/
└── controller.py               # Main orchestration logic

tools/
└── calculator.py              # SymPy-based calculator
```

### 3. Data Models
```
models.py:
├── ChatRequest/Response       # API contracts
├── ProductInfo/SearchResponse # Product data structures
├── OutletInfo/QueryResponse   # Outlet data structures
├── ConversationState         # Session management
└── Intent/AgentAction        # AI behavior enums
```

## 📈 Performance Metrics

### Response Times (Target)
- **Health Check**: < 50ms
- **Chat Response**: < 2000ms
- **Product Search**: < 1000ms
- **Outlet Query**: < 800ms
- **Calculator**: < 100ms

### Data Statistics (Real Production Data)
- **Products**: 150+ items across categories
- **KL Outlets**: 80 locations
- **Selangor Outlets**: 132 locations
- **Total Outlets**: 212 nationwide
- **Vector Dimensions**: 384 (all-MiniLM-L6-v2)
- **Max Conversation Memory**: 2 hours

### Supported Features
- ✅ **Multi-turn Conversations**: Context-aware responses
- ✅ **Intent Classification**: 8 intent types
- ✅ **Vector Search**: Semantic product matching
- ✅ **Text2SQL**: Natural language outlet queries
- ✅ **Session Management**: Persistent conversation state
- ✅ **Real-time Chat**: WebSocket-ready architecture
- ✅ **Error Handling**: Comprehensive exception management
- ✅ **Data Validation**: Input sanitization and validation

## 🛠️ Technical Stack Summary

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Next.js 14 + TypeScript | React-based UI with SSR |
| **Backend** | FastAPI + Python | High-performance async API |
| **Vector DB** | FAISS + SentenceTransformers | Product similarity search |
| **Database** | SQLite | Outlet location data |
| **ML Model** | all-MiniLM-L6-v2 | Text embeddings |
| **Calculator** | SymPy | Mathematical expressions |
| **Session** | In-memory + Redis-ready | Conversation persistence |
| **Validation** | Pydantic | Data models and validation |
| **Testing** | pytest + httpx | Automated testing |
| **Docs** | OpenAPI/Swagger | Interactive API documentation |

This architecture provides a production-ready, scalable AI chatbot system specifically designed for ZUS Coffee's customer service needs with accurate real-world data integration.
