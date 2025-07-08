# 🔌 ZUS Coffee AI Assistant - API Documentation

## 📖 **Overview**

The ZUS Coffee AI Assistant API is a RESTful service built with FastAPI that provides intelligent conversational AI, product search, outlet finder, and mathematical calculation capabilities. This document provides comprehensive API reference for developers.

---

## 🏗️ **Base Configuration**

### **Base URL**
- **Development**: `http://localhost:8000`
- **Production**: `https://your-api-domain.com`

### **Authentication**
Currently, the API is open and does not require authentication. Future versions will include JWT-based authentication.

### **Content Type**
All requests should use `Content-Type: application/json`

### **Rate Limiting**
- **Development**: No limits
- **Production**: 100 requests per minute per IP

---

## 🤖 **Chat API**

### **POST /chat**

The main endpoint for conversational AI interactions.

#### **Request**

```http
POST /chat
Content-Type: application/json

{
  "message": "Find me coffee shops near KLCC",
  "context": ["previous", "conversation", "context"],
  "user_id": "optional-user-identifier"
}
```

#### **Request Schema**

```typescript
interface ChatRequest {
  message: string;           // User's message (required)
  context?: string[];        // Previous conversation context (optional)
  user_id?: string;         // User identifier for session tracking (optional)
  language?: "en" | "ms";   // Language preference (optional, default: "en")
  max_tokens?: number;      // Maximum response length (optional, default: 500)
}
```

#### **Response**

```json
{
  "response": "Here are ZUS Coffee outlets near KLCC:\n\n🏢 **ZUS Coffee KLCC**\n📍 Suria KLCC, Level G, Kuala Lumpur\n⏰ 8:00 AM - 10:00 PM\n📞 +603-2166-8888\n\n🏢 **ZUS Coffee Pavilion**\n📍 Pavilion KL, Level 4, Kuala Lumpur\n⏰ 10:00 AM - 10:00 PM\n📞 +603-2118-8833",
  "intent": "outlet_inquiry",
  "confidence": 0.95,
  "context": ["outlet_search", "location_klcc"],
  "entities": {
    "location": "KLCC",
    "business_type": "coffee_shop"
  },
  "products": [],
  "outlets": [
    {
      "id": 1,
      "name": "ZUS Coffee KLCC",
      "address": "Suria KLCC, Level G, Kuala Lumpur",
      "operating_hours": "8:00 AM - 10:00 PM",
      "phone": "+603-2166-8888",
      "latitude": 3.1578,
      "longitude": 101.7119
    }
  ],
  "calculation_result": null,
  "response_time": 0.234,
  "timestamp": "2025-07-09T10:30:00Z"
}
```

#### **Response Schema**

```typescript
interface ChatResponse {
  response: string;                    // AI-generated response text
  intent: IntentType;                 // Detected user intent
  confidence: number;                 // Confidence score (0-1)
  context: string[];                  // Updated conversation context
  entities: Record<string, any>;      // Extracted entities from user message
  products: Product[];                // Related products (if any)
  outlets: Outlet[];                  // Related outlets (if any)
  calculation_result?: number;        // Math calculation result (if applicable)
  response_time: number;              // Processing time in seconds
  timestamp: string;                  // Response timestamp (ISO 8601)
}
```

#### **Intent Types**

```typescript
enum IntentType {
  "greeting" = "greeting",
  "product_inquiry" = "product_inquiry", 
  "product_recommendation" = "product_recommendation",
  "outlet_inquiry" = "outlet_inquiry",
  "outlet_hours" = "outlet_hours",
  "menu_question" = "menu_question",
  "order_assistance" = "order_assistance",
  "calculation" = "calculation",
  "general_question" = "general_question",
  "complaint" = "complaint",
  "compliment" = "compliment",
  "goodbye" = "goodbye",
  "unknown" = "unknown"
}
```

#### **Example Requests**

**Product Search:**
```json
{
  "message": "What coffee drinks do you have with chocolate?",
  "context": []
}
```

**Outlet Finder:**
```json
{
  "message": "Find ZUS Coffee outlets in Petaling Jaya",
  "context": ["greeting"]
}
```

**Mathematical Calculation:**
```json
{
  "message": "Calculate 25% tip for RM 48.50",
  "context": ["order_assistance"]
}
```

---

## 🛍️ **Product Search API**

### **GET /products/search**

Search for products using semantic vector search.

#### **Request**

```http
GET /products/search?query=latte&limit=5&category=coffee&min_price=10&max_price=25
```

#### **Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query for products |
| `limit` | integer | No | Maximum results (default: 10, max: 50) |
| `category` | string | No | Filter by product category |
| `min_price` | float | No | Minimum price filter |
| `max_price` | float | No | Maximum price filter |
| `sort_by` | string | No | Sort by: `relevance`, `price`, `name` |

#### **Response**

```json
{
  "products": [
    {
      "id": "prod_001",
      "name": "Caffe Latte",
      "description": "Smooth espresso with steamed milk and a light layer of foam",
      "category": "coffee",
      "price": 12.90,
      "image_url": "https://example.com/images/latte.jpg",
      "ingredients": ["espresso", "steamed milk", "milk foam"],
      "nutritional_info": {
        "calories": 150,
        "caffeine_mg": 75,
        "fat_g": 8,
        "sugar_g": 12
      },
      "availability": true,
      "sizes": ["Regular", "Large"],
      "customizations": ["Extra shot", "Decaf", "Oat milk", "Almond milk"],
      "similarity_score": 0.92
    }
  ],
  "total_results": 1,
  "query_time": 0.045,
  "suggestions": ["cappuccino", "macchiato", "flat white"]
}
```

### **GET /products/{product_id}**

Get detailed information about a specific product.

#### **Response**

```json
{
  "id": "prod_001",
  "name": "Caffe Latte",
  "description": "Smooth espresso with steamed milk and a light layer of foam",
  "category": "coffee",
  "price": 12.90,
  "image_url": "https://example.com/images/latte.jpg",
  "ingredients": ["espresso", "steamed milk", "milk foam"],
  "nutritional_info": {
    "calories": 150,
    "caffeine_mg": 75,
    "fat_g": 8,
    "sugar_g": 12,
    "protein_g": 8,
    "carbs_g": 14
  },
  "allergens": ["milk"],
  "availability": true,
  "sizes": [
    {
      "name": "Regular",
      "volume_ml": 355,
      "price": 12.90
    },
    {
      "name": "Large", 
      "volume_ml": 473,
      "price": 15.90
    }
  ],
  "customizations": [
    {
      "name": "Extra shot",
      "price": 3.00,
      "category": "espresso"
    },
    {
      "name": "Oat milk",
      "price": 2.00,
      "category": "milk_alternative"
    }
  ],
  "reviews": {
    "average_rating": 4.5,
    "total_reviews": 1247
  }
}
```

---

## 🏪 **Outlet Finder API**

### **GET /outlets**

Find ZUS Coffee outlets based on location and filters.

#### **Request**

```http
GET /outlets?location=KLCC&radius=5&services=wifi,parking&limit=10
```

#### **Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `location` | string | No | Location name or coordinates |
| `latitude` | float | No | Latitude coordinate |
| `longitude` | float | No | Longitude coordinate |
| `radius` | float | No | Search radius in kilometers (default: 10) |
| `services` | string | No | Comma-separated services (wifi, parking, drive_thru) |
| `limit` | integer | No | Maximum results (default: 20, max: 100) |
| `open_now` | boolean | No | Filter for currently open outlets |

#### **Response**

```json
{
  "outlets": [
    {
      "id": 1,
      "name": "ZUS Coffee KLCC",
      "address": "Suria KLCC, Level G, Kuala Lumpur",
      "city": "Kuala Lumpur",
      "state": "Selangor", 
      "postcode": "50088",
      "country": "Malaysia",
      "latitude": 3.1578,
      "longitude": 101.7119,
      "phone": "+603-2166-8888",
      "email": "klcc@zuscoffee.com",
      "operating_hours": {
        "monday": "8:00 AM - 10:00 PM",
        "tuesday": "8:00 AM - 10:00 PM",
        "wednesday": "8:00 AM - 10:00 PM", 
        "thursday": "8:00 AM - 10:00 PM",
        "friday": "8:00 AM - 11:00 PM",
        "saturday": "8:00 AM - 11:00 PM",
        "sunday": "9:00 AM - 10:00 PM"
      },
      "services": ["wifi", "parking", "outdoor_seating"],
      "facilities": ["restroom", "charging_stations", "meeting_room"],
      "is_open_now": true,
      "distance_km": 2.3,
      "images": [
        "https://example.com/images/outlets/klcc-exterior.jpg",
        "https://example.com/images/outlets/klcc-interior.jpg"
      ],
      "social_media": {
        "instagram": "@zuscoffee_klcc",
        "facebook": "ZUSCoffeeKLCC"
      }
    }
  ],
  "total_results": 1,
  "search_center": {
    "latitude": 3.1578,
    "longitude": 101.7119,
    "address": "KLCC, Kuala Lumpur"
  },
  "query_time": 0.023
}
```

### **GET /outlets/{outlet_id}**

Get detailed information about a specific outlet.

### **GET /outlets/{outlet_id}/hours**

Get current operating hours and status for a specific outlet.

#### **Response**

```json
{
  "outlet_id": 1,
  "name": "ZUS Coffee KLCC",
  "current_status": "open",
  "current_time": "2025-07-09T14:30:00+08:00",
  "timezone": "Asia/Kuala_Lumpur",
  "today_hours": {
    "open": "8:00 AM",
    "close": "10:00 PM",
    "is_24_hours": false
  },
  "week_schedule": {
    "monday": { "open": "08:00", "close": "22:00" },
    "tuesday": { "open": "08:00", "close": "22:00" },
    "wednesday": { "open": "08:00", "close": "22:00" },
    "thursday": { "open": "08:00", "close": "22:00" },
    "friday": { "open": "08:00", "close": "23:00" },
    "saturday": { "open": "08:00", "close": "23:00" },
    "sunday": { "open": "09:00", "close": "22:00" }
  },
  "special_hours": [
    {
      "date": "2025-08-31",
      "reason": "National Day",
      "hours": { "open": "10:00", "close": "18:00" }
    }
  ],
  "next_status_change": {
    "time": "2025-07-09T22:00:00+08:00",
    "status": "closed"
  }
}
```

---

## 🧮 **Calculator API**

### **POST /calculate**

Perform mathematical calculations and conversions.

#### **Request**

```json
{
  "expression": "25% of RM 48.50 + 10",
  "type": "financial"
}
```

#### **Request Schema**

```typescript
interface CalculationRequest {
  expression: string;                    // Mathematical expression
  type?: "basic" | "financial" | "unit"; // Calculation type (optional)
  precision?: number;                    // Decimal places (default: 2)
}
```

#### **Response**

```json
{
  "expression": "25% of RM 48.50 + 10",
  "result": 22.125,
  "formatted_result": "RM 22.13",
  "steps": [
    "25% of RM 48.50 = RM 12.125", 
    "RM 12.125 + 10 = RM 22.125",
    "Rounded to 2 decimal places: RM 22.13"
  ],
  "type": "financial",
  "currency": "MYR",
  "calculation_time": 0.003
}
```

### **Supported Operations**

- Basic arithmetic: `+`, `-`, `*`, `/`, `^`, `%`
- Percentages: `25% of 100`, `increase 50 by 20%`
- Financial: `tip calculation`, `tax calculation`, `currency conversion`
- Unit conversions: `5 km to miles`, `32°F to °C`
- Mathematical functions: `sqrt(16)`, `sin(30)`, `log(100)`

---

## 🔍 **Search & Discovery API**

### **GET /search**

Universal search across products, outlets, and content.

#### **Request**

```http
GET /search?q=coffee near me&type=all&limit=20
```

#### **Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search query |
| `type` | string | No | Search type: `all`, `products`, `outlets`, `content` |
| `limit` | integer | No | Maximum results per type |
| `location` | string | No | Location context for search |

#### **Response**

```json
{
  "query": "coffee near me",
  "results": {
    "products": [
      {
        "type": "product",
        "id": "prod_001",
        "title": "Caffe Latte",
        "description": "Smooth espresso with steamed milk",
        "price": 12.90,
        "relevance_score": 0.95
      }
    ],
    "outlets": [
      {
        "type": "outlet",
        "id": 1,
        "title": "ZUS Coffee KLCC", 
        "description": "Suria KLCC, Level G, Kuala Lumpur",
        "distance": "2.3 km",
        "relevance_score": 0.88
      }
    ],
    "content": [
      {
        "type": "content",
        "id": "article_001",
        "title": "The Perfect Coffee Guide",
        "description": "Learn about different coffee types and brewing methods",
        "url": "/content/perfect-coffee-guide",
        "relevance_score": 0.75
      }
    ]
  },
  "total_results": 3,
  "search_time": 0.067,
  "suggestions": ["latte near me", "coffee shops nearby", "espresso drinks"]
}
```

---

## 📊 **Analytics API**

### **GET /analytics/popular**

Get popular products, searches, and trends.

#### **Response**

```json
{
  "popular_products": [
    {
      "id": "prod_001",
      "name": "Caffe Latte",
      "search_count": 1247,
      "trend": "up"
    }
  ],
  "popular_searches": [
    {
      "query": "coffee near me",
      "count": 892,
      "trend": "stable"
    }
  ],
  "trending_topics": [
    {
      "topic": "iced coffee",
      "growth_rate": 0.25,
      "period": "last_7_days"
    }
  ],
  "time_period": "last_30_days",
  "generated_at": "2025-07-09T10:30:00Z"
}
```

---

## 🏥 **Health & Status API**

### **GET /health**

Basic health check endpoint.

#### **Response**

```json
{
  "status": "healthy",
  "timestamp": "2025-07-09T10:30:00Z",
  "version": "1.0.0",
  "uptime": 86400,
  "environment": "production"
}
```

### **GET /health/detailed**

Comprehensive health check with system metrics.

#### **Response**

```json
{
  "status": "healthy",
  "timestamp": "2025-07-09T10:30:00Z",
  "version": "1.0.0",
  "uptime": 86400,
  "environment": "production",
  "services": {
    "database": {
      "status": "healthy",
      "response_time": 0.012,
      "connections": 5
    },
    "vector_search": {
      "status": "healthy",
      "index_size": 100,
      "memory_usage": "245 MB"
    },
    "ai_model": {
      "status": "healthy",
      "model_loaded": true,
      "last_prediction_time": 0.234
    }
  },
  "metrics": {
    "requests_per_minute": 42,
    "average_response_time": 0.156,
    "error_rate": 0.002,
    "memory_usage": "512 MB",
    "cpu_usage": "23%"
  }
}
```

---

## ⚠️ **Error Handling**

### **Error Response Format**

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid parameters",
    "details": "The 'message' field is required and cannot be empty",
    "timestamp": "2025-07-09T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

### **HTTP Status Codes**

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### **Error Codes**

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `AUTHENTICATION_ERROR` | Authentication failed |
| `AUTHORIZATION_ERROR` | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | Requested resource not found |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `AI_MODEL_ERROR` | AI model processing error |
| `DATABASE_ERROR` | Database operation failed |
| `EXTERNAL_SERVICE_ERROR` | External service unavailable |
| `INTERNAL_ERROR` | Unexpected server error |

---

## 🔒 **Security**

### **CORS Configuration**

The API supports CORS for web applications:

```http
Access-Control-Allow-Origin: https://your-frontend-domain.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

### **Request Validation**

All requests are validated using Pydantic models:

- Input sanitization for XSS prevention
- SQL injection protection through parameterized queries
- File upload restrictions (if applicable)
- Request size limits

### **Rate Limiting**

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1625835600
```

---

## 📝 **Request/Response Examples**

### **Complete Chat Conversation**

```http
POST /chat
Content-Type: application/json

{
  "message": "Hi there! I'm looking for a good coffee recommendation",
  "context": []
}
```

```json
{
  "response": "Hello! 👋 Welcome to ZUS Coffee! I'd be happy to help you find the perfect coffee. \n\nHere are some of our most popular recommendations:\n\n☕ **Caffe Latte** - Smooth and creamy with rich espresso\n☕ **Cappuccino** - Perfect balance of espresso, steamed milk, and foam\n☕ **Flat White** - Strong coffee flavor with velvety microfoam\n\nWhat type of coffee flavors do you usually enjoy? Sweet, strong, or something in between?",
  "intent": "product_recommendation",
  "confidence": 0.92,
  "context": ["greeting", "product_inquiry"],
  "entities": {
    "beverage_type": "coffee",
    "request_type": "recommendation"
  },
  "products": [
    {
      "id": "prod_001",
      "name": "Caffe Latte",
      "price": 12.90,
      "image_url": "https://example.com/latte.jpg"
    },
    {
      "id": "prod_002", 
      "name": "Cappuccino",
      "price": 11.90,
      "image_url": "https://example.com/cappuccino.jpg"
    }
  ],
  "outlets": [],
  "calculation_result": null,
  "response_time": 0.198,
  "timestamp": "2025-07-09T10:30:00Z"
}
```

### **Product Search with Filters**

```http
GET /products/search?query=iced coffee&category=cold_drinks&max_price=20&limit=3
```

```json
{
  "products": [
    {
      "id": "prod_015",
      "name": "Iced Americano",
      "description": "Bold espresso over ice with cold water",
      "category": "cold_drinks",
      "price": 9.90,
      "image_url": "https://example.com/iced-americano.jpg",
      "ingredients": ["espresso", "cold water", "ice"],
      "nutritional_info": {
        "calories": 5,
        "caffeine_mg": 150,
        "fat_g": 0,
        "sugar_g": 0
      },
      "availability": true,
      "sizes": ["Regular", "Large"],
      "customizations": ["Extra shot", "Decaf"],
      "similarity_score": 0.98
    },
    {
      "id": "prod_016",
      "name": "Iced Latte",
      "description": "Smooth espresso with cold milk over ice",
      "category": "cold_drinks", 
      "price": 13.90,
      "image_url": "https://example.com/iced-latte.jpg",
      "ingredients": ["espresso", "cold milk", "ice"],
      "nutritional_info": {
        "calories": 120,
        "caffeine_mg": 75,
        "fat_g": 6,
        "sugar_g": 10
      },
      "availability": true,
      "sizes": ["Regular", "Large"],
      "customizations": ["Extra shot", "Oat milk", "Vanilla syrup"],
      "similarity_score": 0.94
    }
  ],
  "total_results": 2,
  "query_time": 0.034,
  "suggestions": ["cold brew", "frappuccino", "iced mocha"]
}
```

---

## 🧪 **Testing**

### **API Testing with cURL**

```bash
# Test chat endpoint
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, I need help finding coffee", "context": []}'

# Test product search
curl -X GET "http://localhost:8000/products/search?query=latte&limit=3"

# Test outlet finder
curl -X GET "http://localhost:8000/outlets?location=KLCC&radius=5"

# Test health check
curl -X GET "http://localhost:8000/health"
```

### **API Testing with Python**

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# Test chat endpoint
def test_chat():
    url = f"{BASE_URL}/chat"
    payload = {
        "message": "What's your most popular coffee?",
        "context": []
    }
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test product search
def test_product_search():
    url = f"{BASE_URL}/products/search"
    params = {"query": "cappuccino", "limit": 5}
    response = requests.get(url, params=params)
    print(f"Status: {response.status_code}")
    print(f"Products found: {len(response.json()['products'])}")

# Run tests
if __name__ == "__main__":
    test_chat()
    test_product_search()
```

---

## 📚 **SDK & Client Libraries**

### **JavaScript/TypeScript SDK**

```typescript
// zus-coffee-api-client.ts
class ZUSCoffeeAPI {
  private baseURL: string;
  
  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }
  
  async chat(message: string, context: string[] = []): Promise<ChatResponse> {
    const response = await fetch(`${this.baseURL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, context })
    });
    return response.json();
  }
  
  async searchProducts(query: string, options: SearchOptions = {}): Promise<ProductSearchResponse> {
    const params = new URLSearchParams({
      query,
      ...options
    });
    const response = await fetch(`${this.baseURL}/products/search?${params}`);
    return response.json();
  }
  
  async findOutlets(location: string, radius: number = 10): Promise<OutletResponse> {
    const params = new URLSearchParams({
      location,
      radius: radius.toString()
    });
    const response = await fetch(`${this.baseURL}/outlets?${params}`);
    return response.json();
  }
}

// Usage
const api = new ZUSCoffeeAPI();
const chatResponse = await api.chat("Find me a good latte");
console.log(chatResponse.response);
```

---

## 📊 **Performance & Monitoring**

### **Performance Metrics**

| Endpoint | Average Response Time | 95th Percentile | Throughput (req/s) |
|----------|----------------------|------------------|-------------------|
| `/chat` | 156ms | 234ms | 45 |
| `/products/search` | 45ms | 78ms | 120 |
| `/outlets` | 23ms | 45ms | 200 |
| `/health` | 3ms | 8ms | 500 |

### **Monitoring Setup**

```python
# Add to your monitoring system
import time
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'Request duration')

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(duration)
    
    return response
```

---

## 🔄 **Changelog**

### **Version 1.0.0** (2025-07-09)
- Initial API release
- Chat functionality with AI agent
- Product search with vector similarity
- Outlet finder with location services
- Calculator with mathematical operations
- Comprehensive error handling
- Mobile-optimized responses

### **Upcoming Features**
- User authentication with JWT
- Order management system
- Loyalty program integration
- Push notifications
- Real-time chat with WebSocket
- GraphQL endpoint
- Caching with Redis
- Advanced analytics dashboard

---

## 📞 **Support**

- **API Issues**: [GitHub Issues](https://github.com/Tanz2024/Zuschat-Rag-API/issues)
- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Interactive Testing**: [Swagger UI](http://localhost:8000/docs)
- **Alternative Docs**: [ReDoc](http://localhost:8000/redoc)

---

**API Version**: 1.0.0  
**Last Updated**: July 9, 2025  
**Maintained by**: ZUS Coffee Development Team
