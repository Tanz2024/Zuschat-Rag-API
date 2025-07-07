# ZUS Coffee Chatbot API Documentation

## Overview

The ZUS Coffee Chatbot API provides a comprehensive set of endpoints for conversational AI, product search, outlet finder, and calculation services. Built with FastAPI, it offers high-performance, type-safe APIs with automatic documentation.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-render-app.onrender.com`

## Authentication

Currently, the API is open and does not require authentication. In production environments, consider implementing:
- API key authentication for external integrations
- Session-based authentication for web applications
- Rate limiting based on IP address or user sessions

## API Endpoints

### 1. Health Check

Check the health status of the API and its dependencies.

#### `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "database": "connected",
  "services": {
    "chatbot": "operational",
    "vector_search": "operational",
    "calculator": "operational"
  }
}
```

**Status Codes:**
- `200`: Service is healthy
- `503`: Service is unhealthy or dependencies are down

---

### 2. Chat Endpoint (Core RAG & Conversational AI)

The main chatbot endpoint that handles all user interactions including RAG queries, product search, outlet finder, and calculations.

#### `POST /chat`

**Request Body:**
```json
{
  "message": "string",
  "session_id": "string"
}
```

**Parameters:**
- `message` (required): User's input message
- `session_id` (required): Unique session identifier for conversation continuity

**Response:**
```json
{
  "message": "string",
  "session_id": "string",
  "intent": "string",
  "confidence": 0.95,
  "metadata": {
    "response_time": 0.234,
    "tools_used": ["product_search", "vector_db"],
    "context_turns": 3
  }
}
```

**Intent Types:**
- `greeting`: Welcome messages and greetings
- `product_search`: Product information and search queries
- `outlet_search`: Outlet location and information queries
- `calculation`: Mathematical calculations and pricing
- `promotion_inquiry`: Promotions and offers
- `farewell`: Goodbye messages
- `general`: General information requests

**Example Requests:**

1. **Product Search (RAG)**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me coffee tumblers under RM50",
    "session_id": "user_123"
  }'
```

2. **Outlet Search (Text2SQL)**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find ZUS outlets in Kuala Lumpur with drive-thru",
    "session_id": "user_123"
  }'
```

3. **Calculator Tool**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Calculate 6% SST on RM55",
    "session_id": "user_123"
  }'
```

**Status Codes:**
- `200`: Successful response
- `400`: Invalid request format
- `422`: Validation error
- `500`: Internal server error

---

### 3. Product Search (Direct RAG Endpoint)

Direct access to the RAG-powered product search functionality.

#### `GET /products/search`

**Query Parameters:**
- `q` (required): Search query
- `limit` (optional): Maximum number of results (default: 10)
- `min_price` (optional): Minimum price filter
- `max_price` (optional): Maximum price filter

**Response:**
```json
{
  "products": [
    {
      "id": "product_001",
      "name": "ZUS All-Can Tumbler 600ml (20oz)",
      "price": "RM 105.00",
      "description": "Premium stainless steel tumbler...",
      "category": "Drinkware",
      "features": ["600ml capacity", "Leak-proof", "Insulated"],
      "availability": "In Stock",
      "similarity_score": 0.89
    }
  ],
  "total_found": 5,
  "query_time": 0.045,
  "search_method": "vector_similarity"
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/products/search?q=tumbler&max_price=60&limit=5"
```

---

### 4. Outlet Search (Direct Text2SQL Endpoint)

Direct access to the outlet search functionality with SQL-based filtering.

#### `GET /outlets/search`

**Query Parameters:**
- `location` (optional): Location/area name
- `services` (optional): Comma-separated services (e.g., "drive-thru,wifi")
- `open_24h` (optional): Filter for 24-hour outlets (true/false)
- `limit` (optional): Maximum number of results (default: 20)

**Response:**
```json
{
  "outlets": [
    {
      "id": "outlet_001",
      "name": "ZUS Coffee KLCC",
      "address": "Lower Ground Floor, Suria KLCC",
      "city": "Kuala Lumpur",
      "state": "Kuala Lumpur",
      "operating_hours": {
        "weekday": "7:00 AM - 10:00 PM",
        "weekend": "8:00 AM - 10:00 PM"
      },
      "services": ["Dine-in", "Takeaway", "WiFi", "Power Outlets"],
      "contact": "+60 3-2382 2828",
      "coordinates": {
        "latitude": 3.1580,
        "longitude": 101.7118
      }
    }
  ],
  "total_found": 12,
  "query_time": 0.023,
  "sql_query": "SELECT * FROM outlets WHERE city ILIKE '%kuala lumpur%'"
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/outlets/search?location=KLCC&services=wifi,drive-thru"
```

---

### 5. Calculator Service

Direct access to the calculation functionality.

#### `POST /calculate`

**Request Body:**
```json
{
  "expression": "string",
  "context": "string (optional)"
}
```

**Response:**
```json
{
  "expression": "25 + (15 * 2)",
  "result": 55,
  "formatted_result": "RM 55.00",
  "calculation_type": "arithmetic",
  "steps": [
    "15 * 2 = 30",
    "25 + 30 = 55"
  ]
}
```

**Supported Operations:**
- Basic arithmetic: `+`, `-`, `*`, `/`, `^`
- Percentage calculations: `20% of 100`
- Tax calculations: `6% SST on RM50`
- Currency formatting for Malaysian Ringgit

**Example:**
```bash
curl -X POST "http://localhost:8000/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "expression": "6% SST on RM100",
    "context": "tax_calculation"
  }'
```

---

### 6. Session Management

Manage conversation sessions and context.

#### `GET /sessions/{session_id}`

**Response:**
```json
{
  "session_id": "user_123",
  "created_at": "2024-01-15T10:00:00Z",
  "last_activity": "2024-01-15T10:30:00Z",
  "message_count": 15,
  "context": {
    "last_intent": "product_search",
    "conversation_flow": [
      {
        "turn": 1,
        "intent": "greeting",
        "timestamp": "2024-01-15T10:00:00Z"
      }
    ]
  }
}
```

#### `DELETE /sessions/{session_id}`

Clear session data and context.

**Response:**
```json
{
  "message": "Session cleared successfully",
  "session_id": "user_123"
}
```

---

### 7. Analytics and Metrics

Get usage analytics and performance metrics.

#### `GET /analytics/summary`

**Query Parameters:**
- `start_date` (optional): Start date for analytics (YYYY-MM-DD)
- `end_date` (optional): End date for analytics (YYYY-MM-DD)

**Response:**
```json
{
  "period": {
    "start": "2024-01-01",
    "end": "2024-01-15"
  },
  "metrics": {
    "total_conversations": 1250,
    "total_messages": 8750,
    "avg_conversation_length": 7.0,
    "most_common_intents": {
      "product_search": 45.2,
      "outlet_search": 28.7,
      "calculation": 15.3,
      "greeting": 10.8
    },
    "avg_response_time": 0.187,
    "user_satisfaction": 4.6
  }
}
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "error": {
    "type": "ValidationError",
    "message": "Invalid input parameters",
    "details": [
      {
        "field": "message",
        "issue": "Field required"
      }
    ],
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456"
  }
}
```

### Common HTTP Status Codes

- `200`: Success
- `400`: Bad Request - Invalid parameters
- `404`: Not Found - Resource doesn't exist
- `422`: Unprocessable Entity - Validation error
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error - Server-side error
- `503`: Service Unavailable - Temporary service issue

### Error Types

1. **ValidationError**: Input validation failed
2. **DatabaseError**: Database connection or query error
3. **ProcessingError**: Error in chatbot processing
4. **RateLimitError**: Too many requests from client
5. **ServiceUnavailableError**: External service unavailable

---

## Rate Limiting

### Current Limits

- **Chat Endpoint**: 60 requests per minute per IP
- **Search Endpoints**: 100 requests per minute per IP
- **Calculator**: 120 requests per minute per IP
- **Analytics**: 20 requests per minute per IP

### Rate Limit Headers

Response headers include rate limiting information:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642248600
X-RateLimit-Window: 60
```

---

## SDKs and Code Examples

### Python SDK Example

```python
import requests
import json

class ZUSChatbotClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def chat(self, message, session_id):
        response = self.session.post(
            f"{self.base_url}/chat",
            json={"message": message, "session_id": session_id}
        )
        return response.json()
    
    def search_products(self, query, limit=10):
        response = self.session.get(
            f"{self.base_url}/products/search",
            params={"q": query, "limit": limit}
        )
        return response.json()

# Usage
client = ZUSChatbotClient()
result = client.chat("Show me tumblers", "user_123")
print(result["message"])
```

### JavaScript/Node.js Example

```javascript
class ZUSChatbotClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async chat(message, sessionId) {
        const response = await fetch(`${this.baseUrl}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });
        
        return await response.json();
    }
    
    async searchOutlets(location) {
        const response = await fetch(
            `${this.baseUrl}/outlets/search?location=${encodeURIComponent(location)}`
        );
        return await response.json();
    }
}

// Usage
const client = new ZUSChatbotClient();
const result = await client.chat('Find outlets in KL', 'user_456');
console.log(result.message);
```

---

## WebSocket Support

For real-time chat applications, the API supports WebSocket connections.

### WebSocket Endpoint

`ws://localhost:8000/ws/{session_id}`

### Message Format

**Client to Server:**
```json
{
    "type": "message",
    "content": "Show me coffee tumblers",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

**Server to Client:**
```json
{
    "type": "response",
    "content": "Here are our coffee tumblers...",
    "intent": "product_search",
    "confidence": 0.95,
    "timestamp": "2024-01-15T10:30:01Z"
}
```

### Connection States

- `connecting`: Initial connection attempt
- `connected`: Successfully connected
- `message`: Regular message exchange
- `error`: Error occurred
- `disconnected`: Connection closed

---

## Testing the API

### Using curl

```bash
# Test health endpoint
curl -X GET "http://localhost:8000/health"

# Test chat functionality
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test_session"}'

# Test product search
curl -X GET "http://localhost:8000/products/search?q=tumbler&limit=3"
```

### Using Postman

1. Import the Postman collection from `docs/postman/ZUS_Chatbot_API.json`
2. Set up environment variables:
   - `BASE_URL`: Your API base URL
   - `SESSION_ID`: A test session ID
3. Run the collection tests

### Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger documentation where you can:
- View all endpoints and parameters
- Test API calls directly in the browser
- View request/response schemas
- Download OpenAPI specification

---

## Performance Considerations

### Response Times

- **Chat responses**: < 200ms average
- **Product search**: < 100ms average
- **Outlet search**: < 50ms average
- **Calculations**: < 10ms average

### Caching Strategy

- **Product data**: Cached for 1 hour
- **Outlet data**: Cached for 6 hours
- **Vector embeddings**: Loaded once at startup
- **Session data**: Stored in memory with TTL

### Optimization Tips

1. **Batch requests** when possible
2. **Reuse session IDs** for conversation continuity
3. **Implement client-side caching** for repeated queries
4. **Use appropriate timeout values** for your use case
5. **Monitor rate limits** to avoid throttling

---

## Security Best Practices

### API Security

1. **Input Validation**: All inputs are validated using Pydantic models
2. **SQL Injection Protection**: Parameterized queries only
3. **XSS Prevention**: Response sanitization
4. **Rate Limiting**: Prevents abuse and DoS attacks
5. **CORS Configuration**: Restricted cross-origin requests

### Data Privacy

1. **Session Data**: Automatically expires after inactivity
2. **User Messages**: Not permanently stored
3. **Analytics**: Aggregated and anonymized
4. **Logging**: Personal information excluded

### Production Recommendations

1. Use HTTPS in production
2. Implement API key authentication
3. Set up monitoring and alerting
4. Regular security audits
5. Keep dependencies updated

---

For more information or support, please refer to the main [README.md](../README.md) or open an issue in the project repository.
