# ZUS Chatbot API Specification

## Overview
The ZUS Chatbot Backend provides a comprehensive API for AI-powered conversations, product search, outlet information, and mathematical calculations for ZUS Coffee services.

**Base URL:** `http://localhost:8000`  
**API Version:** 1.0.0  
**Content-Type:** `application/json`

## Authentication
Currently, no authentication is required for API endpoints.

---

## Endpoints

### 🏥 Health Check

#### GET `/health`
Check if the API service is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "message": "ZUS Chatbot Backend is running",
  "version": "1.0.0"
}
```

**cURL Example (Linux/Mac/WSL):**
```bash
curl -X GET "http://localhost:8000/health"
```

**PowerShell Example (Windows):**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
```

---

### 💬 Chat Endpoint

#### POST `/chat`
Main conversational AI endpoint that handles natural language queries about products, outlets, calculations, and general questions.

**Request Body:**
```json
{
  "message": "string (required)",
  "session_id": "string (optional)",
  "context": {
    "location": "string (optional)",
    "preferences": "object (optional)"
  }
}
```

**Response:**
```json
{
  "message": "string",
  "session_id": "string",
  "intent": "product_search|outlet_search|calculation|general_chat|greeting|goodbye|help|unknown",
  "action": "string",
  "context": {},
  "products": [
    {
      "name": "string",
      "description": "string",
      "price": "string",
      "category": "string",
      "availability": "string",
      "tags": ["string"]
    }
  ],
  "outlets": [
    {
      "name": "string",
      "address": "string",
      "phone": "string",
      "hours": "string",
      "location": "string",
      "services": ["string"]
    }
  ],
  "calculation_result": "number|string",
  "suggestions": ["string"],
  "confidence": 0.95
}
```

**Examples:**

1. **Product Query:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What coffee drinks do you have?",
    "session_id": "user123"
  }'
```

```powershell
$body = @{
    message = "What coffee drinks do you have?"
    session_id = "user123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -Body $body -ContentType "application/json"
```

2. **Outlet Query:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find ZUS outlets in Kuala Lumpur",
    "session_id": "user123"
  }'
```

```powershell
$body = @{
    message = "Find ZUS outlets in Kuala Lumpur"
    session_id = "user123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -Body $body -ContentType "application/json"
```

3. **Calculation Query:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Calculate 15 * 2 + 5",
    "session_id": "user123"
  }'
```

```powershell
$body = @{
    message = "Calculate 15 * 2 + 5"
    session_id = "user123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -Body $body -ContentType "application/json"
```

**Expected Response Examples:**

```json
{
  "message": "Here are our coffee drinks available...",
  "session_id": "user123",
  "intent": "product_search",
  "action": "search_products",
  "products": [
    {
      "name": "Iced Americano",
      "description": "Rich espresso with cold water",
      "price": "RM 8.50",
      "category": "coffee",
      "availability": "available",
      "tags": ["iced", "espresso", "coffee"]
    }
  ],
  "suggestions": ["Would you like to know about our pastries?"],
  "confidence": 0.92
}
```

---

### 🔍 Product Search (RAG Engine)

#### GET `/products`
Search for products using vector similarity matching powered by RAG (Retrieval-Augmented Generation).

**RAG Implementation:**
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Store**: FAISS with cosine similarity
- **Dimensions**: 384
- **Index Type**: IndexFlatIP (Inner Product)

**Query Parameters:**
- `query` (string, required): Search query for semantic matching
- `top_k` (integer, optional): Number of results (1-20, default: 5)

**RAG Process Flow:**
1. Query embedding generation (384-dimensional vector)
2. Vector similarity search using FAISS
3. Product retrieval based on semantic similarity
4. Response generation with relevance scoring

**Response:**
```json
{
  "products": [
    {
      "name": "string",
      "description": "string",
      "price": "string",
      "category": "string",
      "availability": "string",
      "tags": ["string"],
      "similarity_score": 0.89
    }
  ],
  "summary": "string (generated summary of results)",
  "total_found": 5
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/products?query=iced%20coffee&top_k=10"
```

**Response:**
```json
{
  "products": [
    {
      "name": "Iced Americano",
      "description": "Rich espresso with cold water over ice",
      "price": "RM 8.50",
      "category": "coffee",
      "availability": "available",
      "tags": ["iced", "espresso", "coffee"]
    },
    {
      "name": "Iced Latte",
      "description": "Espresso with steamed milk over ice",
      "price": "RM 9.50",
      "category": "coffee",
      "availability": "available",
      "tags": ["iced", "latte", "milk"]
    }
  ],
  "summary": "Found 10 iced coffee products including Americano, Latte, and Cappuccino variations.",
  "total_found": 10
}
```

---

### 🏪 Outlet Search (Text2SQL Engine)

#### GET `/outlets`
Search for ZUS Coffee outlets using natural language processing converted to SQL queries.

**Text2SQL Implementation:**
- **NLP Engine**: Pattern-based natural language understanding
- **Database**: SQLite with 212 real outlet records
- **Query Generation**: Dynamic SQL building with safety validation
- **Location Coverage**: KL (80 outlets), Selangor (132 outlets)

**Query Parameters:**
- `query` (string, required): Natural language query for outlet search
- `location` (string, optional): Location filter (deprecated - use query parameter)

**Text2SQL Process Flow:**
1. Natural language query analysis
2. Location, service, and landmark extraction
3. Dynamic SQL query generation with safety checks
4. Database execution with result limiting
5. Response formatting with user-friendly output

**Supported Query Patterns:**
- **Locations**: "Kuala Lumpur", "KL", "Selangor", "Shah Alam"
- **Services**: "drive-thru", "WiFi", "24-hour", "delivery", "dine-in"
- **Landmarks**: "Mid Valley", "KLCC", "Pavilion", "AEON"

**Response:**
```json
{
  "outlets": [
    {
      "id": 1,
      "name": "string",
      "address": "string", 
      "opening_hours": "string",
      "services": "string"
    }
  ],
  "sql_query": "string (generated SQL for transparency)",
  "total_found": 80
}
```

**Examples:**

1. **Location-based search:**
```bash
curl -X GET "http://localhost:8000/outlets?query=outlets%20in%20kuala%20lumpur"
```

2. **Service-based search:**
```bash
curl -X GET "http://localhost:8000/outlets?query=drive%20thru%20outlets"
```

3. **Landmark search:**
```bash
curl -X GET "http://localhost:8000/outlets?query=outlets%20near%20mid%20valley"
```

**Expected Response:**
```json
{
  "outlets": [
    {
      "id": 1,
      "name": "ZUS Coffee KLCC",
      "address": "Lot OS301, Level 3, Suria KLCC, Kuala Lumpur City Centre, 50088 Kuala Lumpur",
      "opening_hours": "8:00 AM - 10:00 PM",
      "services": "Dine-in, Takeaway, Delivery, WiFi"
    },
    {
      "id": 2,
      "name": "ZUS Coffee Mid Valley",
      "address": "Level 3, Mid Valley Megamall, Lingkaran Syed Putra, Mid Valley City, 59200 Kuala Lumpur",
      "opening_hours": "10:00 AM - 10:00 PM",
      "services": "Dine-in, Takeaway, Delivery"
    }
  ],
  "total_found": 80
}
```

---

### 🧮 Calculator

#### POST `/calculate`
Perform mathematical calculations.

**Request Body:**
```json
{
  "expression": "string (required, max 200 chars)"
}
```

**Response:**
```json
{
  "result": "number|string",
  "expression": "string",
  "is_valid": "boolean",
  "error_message": "string (optional)"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "expression": "15 * 2 + 5"
  }'
```

**Response:**
```json
{
  "result": 35.0,
  "expression": "15 * 2 + 5",
  "is_valid": true,
  "error_message": null
}
```

---

### 🔧 Admin Endpoints

#### POST `/admin/rebuild-vector-store`
Rebuild the product vector store index (admin only).

**Response:**
```json
{
  "message": "Vector store rebuilt successfully"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/admin/rebuild-vector-store"
```

---

### 🐛 Debug Endpoints

#### GET `/debug/sessions`
Get information about active chat sessions.

**Response:**
```json
{
  "total_sessions": 5,
  "session_ids": ["user123", "user456", "user789"]
}
```

#### GET `/debug/vector-store-status`
Get vector store status and statistics.

**Response:**
```json
{
  "index_loaded": true,
  "total_products": 150,
  "index_size": 150,
  "model": "all-MiniLM-L6-v2",
  "dimension": 384
}
```

---

## Error Responses

All endpoints return standardized error responses:

```json
{
  "error": "string",
  "error_type": "string",
  "message": "string",
  "status_code": 400
}
```

### Common HTTP Status Codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

---

## Data Models

### Key Statistics (Real Data):
- **Total KL Outlets**: 80
- **Total Selangor Outlets**: 132  
- **Total Products**: ~150 items
- **Supported Services**: Dine-in, Takeaway, Delivery, Drive-thru, WiFi, 24-hour

### Supported Intent Types:
- `product_search`: Product and menu queries
- `outlet_search`: Store location and information
- `calculation`: Mathematical calculations
- `general_chat`: General questions about ZUS Coffee
- `greeting`: Welcome messages
- `goodbye`: Farewell messages
- `help`: Assistance requests

### Agent Actions:
- `search_products`: Vector-based product search
- `search_outlets`: SQL-based outlet search
- `calculate`: Mathematical operations
- `answer_question`: General knowledge responses
- `ask_followup`: Conversation continuation

---

## Rate Limits
Currently no rate limits are enforced, but recommended limits for production:
- Chat endpoint: 60 requests/minute per session
- Search endpoints: 100 requests/minute per IP
- Calculator: 30 requests/minute per IP

---

## Testing Examples

### Postman Collection
```json
{
  "info": {
    "name": "ZUS Chatbot API",
    "description": "Complete API testing collection for ZUS Chatbot Backend"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/health",
          "host": ["{{base_url}}"],
          "path": ["health"]
        }
      }
    },
    {
      "name": "Chat - Product Query",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"message\": \"What coffee drinks do you have?\",\n  \"session_id\": \"test_user_123\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/chat",
          "host": ["{{base_url}}"],
          "path": ["chat"]
        }
      }
    },
    {
      "name": "Chat - Outlet Query KL",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"message\": \"How many outlets in Kuala Lumpur?\",\n  \"session_id\": \"test_user_123\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/chat",
          "host": ["{{base_url}}"],
          "path": ["chat"]
        }
      }
    },
    {
      "name": "Chat - Outlet Query Selangor",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"message\": \"Find ZUS outlets in Selangor\",\n  \"session_id\": \"test_user_123\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/chat",
          "host": ["{{base_url}}"],
          "path": ["chat"]
        }
      }
    },
    {
      "name": "Product Search",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/products?query=iced coffee&top_k=5",
          "host": ["{{base_url}}"],
          "path": ["products"],
          "query": [
            {
              "key": "query",
              "value": "iced coffee"
            },
            {
              "key": "top_k",
              "value": "5"
            }
          ]
        }
      }
    },
    {
      "name": "Outlet Search",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/outlets?query=outlets in kuala lumpur",
          "host": ["{{base_url}}"],
          "path": ["outlets"],
          "query": [
            {
              "key": "query",
              "value": "outlets in kuala lumpur"
            }
          ]
        }
      }
    },
    {
      "name": "Calculator",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"expression\": \"15 * 2 + 5\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/chat",
          "host": ["{{base_url}}"],
          "path": ["calculate"]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    }
  ]
}
```

### Quick Test Script (bash/curl)
```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

echo "Testing ZUS Chatbot API..."

# Health check
echo "1. Health Check:"
curl -s "$BASE_URL/health" | jq '.'

# Chat - Product query
echo -e "\n2. Chat - Product Query:"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What coffee drinks do you have?", "session_id": "test123"}' | jq '.'

# Chat - KL outlets
echo -e "\n3. Chat - KL Outlets:"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How many outlets in Kuala Lumpur?", "session_id": "test123"}' | jq '.'

# Chat - Selangor outlets  
echo -e "\n4. Chat - Selangor Outlets:"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Find outlets in Selangor", "session_id": "test123"}' | jq '.'

# Direct product search
echo -e "\n5. Direct Product Search:"
curl -s "$BASE_URL/products?query=iced%20coffee&top_k=3" | jq '.'

# Direct outlet search
echo -e "\n6. Direct Outlet Search:"
curl -s "$BASE_URL/outlets?query=kuala%20lumpur" | jq '.'

# Calculator
echo -e "\n7. Calculator:"
curl -s -X POST "$BASE_URL/calculate" \
  -H "Content-Type: application/json" \
  -d '{"expression": "15 * 2 + 5"}' | jq '.'

echo -e "\nAPI testing completed!"
```

---

## Development Notes

### OpenAPI/Swagger Documentation
The API automatically generates interactive documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### Environment Setup
```bash
# Start the backend server
cd backend
python -m uvicorn main:app --reload --port 8000

# The API will be available at http://localhost:8000
```

### Key Features
- ✅ **Smart Intent Detection**: Automatically classifies user queries
- ✅ **Real Data Only**: All responses use actual ZUS Coffee data (80 KL outlets, 132 Selangor outlets)
- ✅ **Vector Search**: Semantic similarity search for products
- ✅ **SQL Generation**: Natural language to SQL for outlet queries
- ✅ **Session Management**: Conversation continuity with session IDs
- ✅ **Error Handling**: Comprehensive error responses and validation
- ✅ **CORS Support**: Cross-origin requests enabled
- ✅ **Production Ready**: Proper logging, exception handling, and data validation
