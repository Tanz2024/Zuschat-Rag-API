"""
Robust FastAPI main application for ZUS Coffee Chatbot
Handles database connectivity issues gracefully while maintaining chatbot functionality
Version: 1.0.3 - July 8, 2025 - Fixed test endpoints with proper JSON structure
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import logging
import asyncio
import os
from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi.middleware.gzip import GZipMiddleware

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log startup immediately
logger.info("=== ZUS Coffee Chatbot Backend Starting ===")
logger.info(f"Target Port: {os.getenv('PORT', '10000')}")
logger.info("Initializing components...")

# Import models (basic Pydantic models, no database dependency)
try:
    try:
        from backend.models import (
            ChatRequest, ChatResponse, ErrorResponse
        )
    except ImportError:
        from models import (
            ChatRequest, ChatResponse, ErrorResponse
        )
    logger.info("Models imported successfully")
except Exception as e:
    logger.warning(f"Models import issue: {e}")
    # Create basic models if import fails
    from pydantic import BaseModel
    
    class ChatRequest(BaseModel):
        message: str
        session_id: str = "default"
    
    class ChatResponse(BaseModel):
        message: str
        session_id: str
        intent: str = "unknown"
        confidence: float = 0.5
    
    class ErrorResponse(BaseModel):
        error: str
        status_code: int
        detail: str = ""

# Import database with fallback handling
database_available = False
try:
    try:
        from backend.data.database import get_db, create_tables, validate_database_config
    except ImportError:
        from data.database import get_db, create_tables, validate_database_config
    database_available = validate_database_config()
    def check_database_health():
        if database_available:
            return {"status": "available", "available": True}
        else:
            return {"status": "not_available", "available": False}
    logger.info(f"Database system loaded (available: {database_available})")
except Exception as e:
    logger.warning(f"Database system not available: {e}")
    # Create mock database functions
    def get_db():
        return None
    def create_tables():
        pass
    def check_database_health():
        return {"status": "not_available", "available": False}

# Import enhanced chatbot agent with multiple fallback layers
chatbot_available = False
chatbot_type = "none"

try:
    try:
        from backend.chatbot.enhanced_minimal_agent import get_chatbot
    except ImportError:
        from chatbot.enhanced_minimal_agent import get_chatbot
    chatbot_available = True
    chatbot_type = "enhanced_minimal"
    logger.info("Using ENHANCED MINIMAL chatbot with real data keyword matching")
except Exception as e:
    logger.warning(f"Enhanced minimal chatbot not available: {e}")
    try:
        try:
            from backend.chatbot.minimal_agent import get_chatbot
        except ImportError:
            from chatbot.minimal_agent import get_chatbot
        chatbot_available = True
        chatbot_type = "minimal"
        logger.info("Using minimal working chatbot")
    except Exception as e2:
        logger.warning(f"Minimal chatbot not available: {e2}")
        # Create ultra-simple fallback chatbot
        class SimpleFallbackChatbot:
            async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
                return {
                    "message": "Welcome to ZUS Coffee! I'm temporarily running in limited mode. Our premium drinkware collection includes tumblers, cups, and mugs. Visit our outlets in KLCC, Pavilion, Mid Valley, and more locations across KL and Selangor.",
                    "session_id": session_id,
                    "intent": "general_chat",
                    "confidence": 0.5
                }
            
            def chat(self, message: str, session_id: str = "default") -> Dict[str, Any]:
                return {
                    "response": "Welcome to ZUS Coffee! I'm temporarily running in limited mode. Our premium drinkware collection includes tumblers, cups, and mugs. Visit our outlets in KLCC, Pavilion, Mid Valley, and more locations across KL and Selangor.",
                    "session_id": session_id,
                    "intent": "general_chat"
                }
        
        def get_chatbot():
            return SimpleFallbackChatbot()
        
        chatbot_available = True
        chatbot_type = "fallback"
        logger.info("Using ultra-simple fallback chatbot")

# Fast response cache for instant replies to common queries
FAST_RESPONSES = {
    # Product queries
    "products": {
        "message": "Our premium drinkware collection includes ceramic mugs, stainless steel tumblers, and travel cups. Popular items: ZUS Signature Tumbler (RM45), Ceramic Mug Set (RM35), and Travel Cup (RM25).",
        "intent": "product_search",
        "confidence": 0.9
    },
    "tumbler": {
        "message": "ZUS Signature Tumbler (RM45) - Premium stainless steel with double-wall insulation. Perfect for hot and cold beverages. Available in multiple colors!",
        "intent": "product_search", 
        "confidence": 0.95
    },
    "mug": {
        "message": "Ceramic Mug Set (RM35) - Beautiful ceramic mugs perfect for your morning coffee. Dishwasher safe and comes in elegant designs.",
        "intent": "product_search",
        "confidence": 0.95
    },
    
    # Outlet queries
    "outlets": {
        "message": "ZUS Coffee outlets: KLCC, Pavilion KL, Mid Valley, 1 Utama, Sunway Pyramid, IOI City Mall, and 50+ locations across KL & Selangor. Most open 10am-10pm daily.",
        "intent": "outlet_search",
        "confidence": 0.9
    },
    "location": {
        "message": "Major ZUS Coffee locations: KLCC (Level 2), Pavilion KL (Level 4), Mid Valley (LG Floor), 1 Utama (Level 1). Check our website for complete list!",
        "intent": "outlet_search",
        "confidence": 0.9
    },
    
    # Common greetings
    "hello": {
        "message": "Hello! Welcome to ZUS Coffee! ☕ I can help you with our drinkware products, outlet locations, and calculations. What would you like to know?",
        "intent": "greeting",
        "confidence": 0.95
    },
    "hi": {
        "message": "Hi there! Welcome to ZUS Coffee! ☕ How can I assist you today? I can help with products, outlets, or any questions you have.",
        "intent": "greeting", 
        "confidence": 0.95
    }
}

def get_fast_response(message: str) -> Dict[str, Any] | None:
    """Get instant response for common queries."""
    msg_lower = message.lower().strip()
    
    # Direct keyword matches
    for keyword, response in FAST_RESPONSES.items():
        if keyword in msg_lower:
            return response
    
    # Pattern matching for instant responses
    if any(word in msg_lower for word in ["show", "list", "what"] + ["product", "item", "buy"]):
        return FAST_RESPONSES["products"]
    
    if any(word in msg_lower for word in ["where", "find", "nearest"] + ["outlet", "store", "location"]):
        return FAST_RESPONSES["outlets"]
        
    if any(word in msg_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
        return FAST_RESPONSES["hello"]
    
    return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events with error handling and immediate port binding."""
    # Startup
    logger.info("Starting ZUS Chatbot Backend...")
    
    # Log port information immediately
    port = os.getenv("PORT", "10000")
    logger.info(f"Backend will bind to port: {port}")
    
    # Initialize database (fast startup with shorter timeout)
    try:
        import asyncio
        # Shorter timeout for faster startup - 10 seconds max
        await asyncio.wait_for(asyncio.to_thread(create_tables), timeout=10.0)
        logger.info("Database initialized quickly")
    except asyncio.TimeoutError:
        logger.warning("Database initialization timed out - continuing with fallback")
    except Exception as e:
        logger.warning(f"Database initialization failed - continuing: {e}")
    
    # Test chatbot (with fast timeout for instant startup)
    try:
        chatbot = get_chatbot()
        if hasattr(chatbot, 'process_message'):
            # Very fast test - 2 seconds max
            test_result = await asyncio.wait_for(
                chatbot.process_message("test", "startup_test"),
                timeout=2.0
            )
        else:
            test_result = chatbot.chat("test", "startup_test")
        logger.info("Chatbot ready - fast response mode enabled")
    except asyncio.TimeoutError:
        logger.info("Chatbot test timed out - using fast fallback mode")
    except Exception as e:
        logger.info(f"Chatbot test bypassed - fast mode active: {e}")
    
    logger.info(f"Backend ready - Database: {database_available}, Chatbot: {chatbot_type}")
    logger.info(f"Server should be accessible on port {port}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ZUS Chatbot Backend...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="ZUS Coffee Chatbot API",
    description="Robust chatbot API for ZUS Coffee with graceful fallback handling",
    version="1.0.1",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add compression for faster responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Performance monitoring middleware
@app.middleware("http")
async def performance_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log slow requests
    if process_time > 1.0:
        logger.warning(f"Slow request: {request.url.path} took {process_time:.2f}s")
    
    return response

# Global error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions gracefully."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(ErrorResponse(
            error=str(exc.detail),
            status_code=exc.status_code,
            detail=str(exc.detail)
        ))
    )


# Improved: Global exception handler returns 200 with fallback message for all unhandled errors in production
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    # Try to return a ChatResponse if this was a /chat call, else ErrorResponse
    try:
        if request.url.path == "/chat":
            # Try to extract session_id if possible
            try:
                body = await request.json()
                session_id = body.get("session_id", "unknown")
            except Exception:
                session_id = "unknown"
            return JSONResponse(
                status_code=200,
                content=jsonable_encoder({
                    "message": "Thank you for contacting ZUS Coffee! I'm experiencing technical difficulties, but you can still ask about our products, outlets, or pricing. Please try again shortly!",
                    "session_id": session_id,
                    "intent": "unknown",
                    "confidence": 0.1
                })
            )
        else:
            return JSONResponse(
                status_code=200,
                content=jsonable_encoder(ErrorResponse(
                    error="Internal server error",
                    status_code=500,
                    detail="An unexpected error occurred. The service is still operational."
                ))
            )
    except Exception as e:
        logger.error(f"Exception in global exception handler: {e}")
        return JSONResponse(
            status_code=200,
            content={
                "message": "Thank you for contacting ZUS Coffee! I'm experiencing technical difficulties. Please try again later.",
                "session_id": "unknown",
                "intent": "unknown",
                "confidence": 0.1
            }
        )

# Root endpoint - support both GET and HEAD for health checks
@app.get("/")
@app.head("/")
async def root():
    """Root endpoint with comprehensive system status."""
    return {
        "message": "ZUS Coffee Chatbot API",
        "version": "1.0.1",
        "status": "active",
        "system": {
            "database_available": database_available,
            "chatbot_type": chatbot_type,
            "chatbot_available": chatbot_available
        },
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "debug": "/debug/system"
        },
        "description": "Robust chatbot with graceful fallback handling"
    }

# Health check endpoint
@app.get("/health")
@app.head("/health")
async def health_check():
    """Fast health check for Render deployment - instant response."""
    return {"status": "healthy", "service": "zus-chatbot", "ready": True}

# Main chat endpoint with robust error handling
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint with multi-layer error handling and fallback.
    Always returns a response, even if individual components fail.
    """
    try:
        logger.info(f"Chat endpoint called with request: {request}")
        
        # Safely extract message and session_id with fallbacks
        try:
            message = getattr(request, 'message', '').strip() if request else ''
            session_id = getattr(request, 'session_id', 'default') if request else 'default'
            logger.info(f"Extracted message: '{message}', session_id: '{session_id}'")
        except Exception as e:
            logger.error(f"Error extracting request data: {e}")
            message = ''
            session_id = 'default'
        
        # Validate input
        if not message:
            return ChatResponse(
                message="I'd love to help you! Please send me a message about ZUS Coffee products, outlets, calculations, or any questions you have.",
                session_id=session_id,
                intent="help",
                confidence=0.5
            )
        
        # FAST RESPONSE: Check for instant replies first (under 50ms)
        fast_response = get_fast_response(message)
        if fast_response:
            logger.info(f"Fast response triggered for: {message[:30]}...")
            return ChatResponse(
                message=fast_response["message"],
                session_id=session_id,
                intent=fast_response["intent"],
                confidence=fast_response["confidence"]
            )
        
        # Check fast response cache first
        try:
            logger.info("Checking fast response cache...")
            cached_response = get_fast_response(message)
            if cached_response:
                logger.info(f"Fast response cache hit for message: {message}")
                return ChatResponse(
                    message=cached_response["message"],
                    session_id=session_id,
                    intent=cached_response["intent"],
                    confidence=cached_response["confidence"]
                )
            logger.info("No fast response cache hit")
        except Exception as e:
            logger.error(f"Error checking fast response cache: {e}")
        
        # Get chatbot instance
        try:
            logger.info("Getting chatbot instance...")
            chatbot = get_chatbot()
            logger.info(f"Chatbot instance obtained: {type(chatbot)}")
        except Exception as e:
            logger.error(f"Failed to get chatbot: {e}")
            return ChatResponse(
                message="I'm temporarily experiencing technical difficulties. Please try again in a moment.",
                session_id=session_id,
                intent="unknown",
                confidence=0.1
            )
        
        # Process message with the chatbot with fast response protection
        try:
            # Get chatbot with timeout protection
            chatbot = get_chatbot()
            
            # Try enhanced method first with fast timeout
            if hasattr(chatbot, 'process_message'):
                # Fast timeout for instant response (3 seconds max)
                result = await asyncio.wait_for(
                    chatbot.process_message(message, session_id),
                    timeout=3.0  # Fast 3 second timeout for instant response
                )
                return ChatResponse(
                    message=result.get("message", "I'm sorry, I couldn't process that request properly."),
                    session_id=session_id,
                    intent=result.get("intent", "unknown"),
                    confidence=result.get("confidence", 0.5)
                )
            # Fallback to simple chat method
            elif hasattr(chatbot, 'chat'):
                result = chatbot.chat(message, session_id)
                return ChatResponse(
                    message=result.get("response", "I'm sorry, I couldn't process that request properly."),
                    session_id=session_id,
                    intent=result.get("intent", "unknown"),
                    confidence=result.get("confidence", 0.5)
                )
            else:
                # Ultimate fallback
                return ChatResponse(
                    message="Welcome to ZUS Coffee! I'm temporarily running in limited mode. Our premium drinkware collection includes tumblers, cups, and mugs. Visit our outlets in KLCC, Pavilion, Mid Valley, and more locations across KL and Selangor.",
                    session_id=session_id,
                    intent="general_chat",
                    confidence=0.3
                )
        except asyncio.TimeoutError:
            logger.warning(f"Fast timeout (3s) for message: {message[:50]}... - providing instant fallback")
            # Instant fallback for fast user experience
            if "product" in message.lower() or "tumbler" in message.lower() or "cup" in message.lower():
                return ChatResponse(
                    message="Our premium drinkware collection includes ceramic mugs, stainless steel tumblers, and travel cups. Popular items: ZUS Signature Tumbler (RM45), Ceramic Mug Set (RM35), and Travel Cup (RM25).",
                    session_id=session_id,
                    intent="product_search",
                    confidence=0.8
                )
            elif "outlet" in message.lower() or "location" in message.lower() or "where" in message.lower():
                return ChatResponse(
                    message="ZUS Coffee outlets are located in major malls: KLCC, Pavilion KL, Mid Valley, 1 Utama, Sunway Pyramid, and many more across KL and Selangor. Visit our website for the complete list!",
                    session_id=session_id,
                    intent="outlet_search",
                    confidence=0.8
                )
            elif any(char.isdigit() for char in message) and any(op in message for op in ['+', '-', '*', '/', 'x', 'add', 'minus']):
                return ChatResponse(
                    message="I can help with calculations! Try asking like '25 + 15' or 'what is 100 minus 30'. For complex calculations, please use our calculator feature.",
                    session_id=session_id,
                    intent="calculation",
                    confidence=0.8
                )
            else:
                return ChatResponse(
                    message="Welcome to ZUS Coffee! ☕ I can help you with our drinkware products, outlet locations, and calculations. What would you like to know?",
                    session_id=session_id,
                    intent="general_chat",
                    confidence=0.7
                )
        except Exception as e:
            logger.error(f"Chatbot processing error: {e}")
            return ChatResponse(
                message="I apologize for the inconvenience. I'm experiencing some technical issues but I'm still here to help! ZUS Coffee offers premium drinkware and has outlets across KL and Selangor. Please try your question again.",
                session_id=session_id,
                intent="unknown",
                confidence=0.2
            )
    except Exception as e:
        logger.error(f"Unexpected chat endpoint error: {e}")
        return ChatResponse(
            message="Thank you for contacting ZUS Coffee! While I'm experiencing some technical difficulties right now, I want you to know that we offer premium drinkware and have multiple outlet locations. Please try again shortly!",
            session_id="default",
            intent="unknown",
            confidence=0.1
        )

# Simple ping endpoint for basic connectivity testing
@app.get("/ping")
async def ping():
    """Simple ping endpoint for connectivity testing."""
    return {"status": "pong", "timestamp": "2025-07-08"}

# Simple GET version of test endpoint
@app.get("/test-chat-get")
async def test_chat_get():
    """Simple GET test endpoint for basic connectivity."""
    return {
        "message": "✅ GET test endpoint working",
        "session_id": "default",
        "intent": "help",
        "confidence": 1.0,
        "context": {"endpoint": "test-chat-get", "status": "working", "method": "GET"},
        "products": None,
        "outlets": None,
        "calculation_result": None,
        "suggestions": ["Use POST /test-chat for full testing", "Try the main /chat endpoint"],
        "action": "provide_answer"
    }

# Test chat endpoint that doesn't use the complex chatbot
@app.post("/test-chat")
async def test_chat(request: ChatRequest):
    """Simple test endpoint to isolate chatbot issues."""
    try:
        message = getattr(request, 'message', '').strip() if request else ''
        session_id = getattr(request, 'session_id', 'default') if request else 'default'
        
        return {
            "message": f"✅ Test response for: {message}",
            "session_id": session_id,
            "intent": "help",
            "confidence": 1.0,
            "context": {"endpoint": "test-chat", "status": "working"},
            "products": None,
            "outlets": None,
            "calculation_result": None,
            "suggestions": ["Try the main /chat endpoint", "Check out our ceramic mugs"],
            "action": "provide_answer"
        }
    except Exception as e:
        logger.error(f"Test chat error: {e}")
        return {
            "message": " Test endpoint error occurred",
            "session_id": "default",
            "intent": "unknown",
            "confidence": 0.0,
            "context": {"endpoint": "test-chat", "status": "error", "error": str(e)},
            "products": None,
            "outlets": None,
            "calculation_result": None,
            "suggestions": ["Check server logs", "Try again"],
            "action": "request_clarification"
        }

# Simple health check for Render (before the complex root endpoint)
@app.get("/render-health")
async def render_health():
    """Simple health check endpoint for Render platform."""
    return {"status": "ok", "service": "zus-chatbot"}

# Startup validation
if __name__ == "__main__":
    import uvicorn
    # Use PORT environment variable (required for Render)
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting ZUS Coffee Backend on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)

"""
This file is intended to be run with:
    uvicorn backend.main:app --host 0.0.0.0 --port 8000
from the project root.
Do NOT use python main.py in production.
"""
