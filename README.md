
# ZUS Coffee AI Assistant – Project Overview & Documentation

## Table of Contents
- [Project Overview](#project-overview)
- [Architecture Overview](#architecture-overview)
- [Key Trade-offs](#key-trade-offs)
- [Setup & Run Instructions](#setup--run-instructions)
- [API Specification](#api-specification)
  - [Chat Endpoint](#chat-endpoint)
  - [RAG Endpoint](#rag-endpoint)
  - [Text2SQL Endpoint](#text2sql-endpoint)
- [Flow Diagrams & Screenshots](#flow-diagrams--screenshots)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview
ZUS Coffee AI Assistant is a full-stack conversational AI system for ZUS Coffee, supporting:
- Product and outlet search (with advanced filters)
- Calculator for prices, discounts, and taxes
- Context-aware follow-ups
- RAG (Retrieval-Augmented Generation) and Text2SQL for advanced queries
- Modern, mobile-friendly frontend (Next.js + Tailwind CSS)

---

## Architecture Overview

**Backend (Python, FastAPI):**
- `enhanced_minimal_agent.py`: Main agent logic (intent detection, product/outlet/calculator)
- Data sources: SQLite DB (`outlets.db`), JSON (`products.json`), fallback hardcoded data
- RAG & Text2SQL endpoints for advanced queries
- Robust error handling, context/memory, and debug logging

**Frontend (Next.js, TypeScript, Tailwind):**
- Chat UI: `ChatWindow.tsx`, `MessageInput.tsx`, `useChat.ts`
- Mobile-first design, keyboard handling, and UX optimizations
- API integration with backend endpoints

**Key Trade-offs:**
- Hybrid search (semantic, fuzzy, keyword) for best recall/precision
- Fallbacks for data loading (DB, file, hardcoded)
- Context/memory for better follow-up handling
- Simplicity vs. extensibility: modular agent, but not over-engineered

---

## Setup & Run Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- (Windows) MSYS2/MinGW for C++ build (if needed)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
# (Optional) Set up SQLite DB: outlets.db
python main.py  # Starts FastAPI server (default: http://localhost:8000)
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev  # Starts Next.js dev server (default: http://localhost:3000)
```

### Testing
- Backend: `python backend/test_similar_pattern_prompts.py`, `python backend/test_specific_calculator.py`, or manual: `python backend/chatbot/manual_agent_test.py`
- Frontend: Open http://localhost:3000 and interact with the chat UI

---

## API Specification

### Chat Endpoint
- **POST** `/api/chat`
- **Request:**
  ```json
  {
    "message": "Show me the cheapest tumbler",
    "session_id": "user-session-uuid"
  }
  ```
- **Response:**
  ```json
  {
    "intent": "product_search",
    "results": [ ...products... ],
    "context": { ... },
    "reply": "Here are the cheapest tumblers..."
  }
  ```

### RAG Endpoint
- **POST** `/api/rag`
- **Request:**
  ```json
  {
    "query": "What is the SST for all products?",
    "session_id": "user-session-uuid"
  }
  ```
- **Response:**
  ```json
  {
    "results": [ ... ],
    "sources": [ ... ],
    "reply": "Here is the SST breakdown for all products..."
  }
  ```

### Text2SQL Endpoint
- **POST** `/api/text2sql`
- **Request:**
  ```json
  {
    "query": "List all outlets in KL",
    "session_id": "user-session-uuid"
  }
  ```
- **Response:**
  ```json
  {
    "sql": "SELECT * FROM outlets WHERE city = 'KL'",
    "results": [ ... ],
    "reply": "Here are all outlets in KL..."
  }
  ```

---

## Flow Diagrams & Screenshots

### System Architecture
```
User
  │
  ▼
Frontend (Next.js/React)
  │  REST API
  ▼
Backend (FastAPI, enhanced_minimal_agent.py)
  │
  ├─> Data: products.json, outlets.db
  ├─> RAG/Text2SQL modules
  ▼
Response
```

### Chatbot UI Example
![Chat UI Screenshot](public/assets/logos/zus-logo.svg)

---

## File Structure
```
backend/
  main.py                # FastAPI app
  models.py              # DB models
  chatbot/
    enhanced_minimal_agent.py  # Main agent logic
    manual_agent_test.py       # Manual backend test script
    ...
  data/
    products.json
    outlets.db
    ...
frontend/
  components/
    ChatWindow.tsx
    MessageInput.tsx
    ...
  hooks/
    useChat.ts
    ...
  pages/
    api/
      chat.ts
    ...
README.md
```

---

## Contributing
- Fork, branch, and PR as usual
- Please add/maintain docstrings and update this README for major changes

## License
MIT License (c) ZUS Coffee, 2025
