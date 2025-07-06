"""
Robust FastAPI main application for ZUS Coffee Chatbot
Handles database connectivity issues gracefully while maintaining chatbot functionality
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

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import models (basic Pydantic models, no database dependency)
try:
    from models import (
        ChatRequest, ChatResponse, ErrorResponse
    )
    logger.info("✅ Models imported successfully")
except Exception as e:
    logger.warning(f"⚠️  Models import issue: {e}")
    # Create basic models if import fails
    from pydantic import BaseModel
    
    class ChatRequest(BaseModel):
        message: str
        session_id: str = "default"
    
    class ChatResponse(BaseModel):
        response: str
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
    from data.database import get_db, create_tables, validate_database_config
    database_available = validate_database_config()
    def check_database_health():
        if database_available:
            return {"status": "available", "available": True}
        else:
            return {"status": "not_available", "available": False}
    logger.info(f"✅ Database system loaded (available: {database_available})")
except Exception as e:
    logger.warning(f"⚠️  Database system not available: {e}")
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
    from chatbot.enhanced_minimal_agent import get_chatbot
    chatbot_available = True
    chatbot_type = "enhanced_minimal"
    logger.info("✅ Using ENHANCED MINIMAL chatbot with real data keyword matching")
except Exception as e:
    logger.warning(f"⚠️  Enhanced minimal chatbot not available: {e}")
    try:
        from chatbot.minimal_agent import get_chatbot
        chatbot_available = True
        chatbot_type = "minimal"
        logger.info("✅ Using minimal working chatbot")
    except Exception as e2:
        logger.warning(f"⚠️  Minimal chatbot not available: {e2}")
        # Create ultra-simple fallback chatbot
        class SimpleFallbackChatbot:
            async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
                return {
                    "message": "Welcome to ZUS Coffee! I'm temporarily running in limited mode. Our premium drinkware collection includes tumblers, cups, and mugs. Visit our outlets in KLCC, Pavilion, Mid Valley, and more locations across KL and Selangor.",
                    "session_id": session_id,
                    "intent": "fallback",
                    "confidence": 0.5
                }
            
            def chat(self, message: str, session_id: str = "default") -> Dict[str, Any]:
                return {
                    "response": "Welcome to ZUS Coffee! I'm temporarily running in limited mode. Our premium drinkware collection includes tumblers, cups, and mugs. Visit our outlets in KLCC, Pavilion, Mid Valley, and more locations across KL and Selangor.",
                    "session_id": session_id,
                    "intent": "fallback"
                }
        
        def get_chatbot():
            return SimpleFallbackChatbot()
        
        chatbot_available = True
        chatbot_type = "fallback"
        logger.info("✅ Using ultra-simple fallback chatbot")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events with error handling."""
    # Startup
    logger.info("🚀 Starting ZUS Chatbot Backend...")
    
    # Initialize database (graceful failure)
    try:
        create_tables()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.warning(f"⚠️  Database initialization failed: {e}")
    
    # Test chatbot
    try:
        chatbot = get_chatbot()
        if hasattr(chatbot, 'process_message'):
            test_result = await chatbot.process_message("test", "startup_test")
        else:
            test_result = chatbot.chat("test", "startup_test")
        logger.info("✅ Chatbot test successful")
    except Exception as e:
        logger.warning(f"⚠️  Chatbot test failed: {e}")
    
    logger.info(f"🎯 Backend ready - Database: {database_available}, Chatbot: {chatbot_type}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down ZUS Chatbot Backend...")

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

# Global error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions gracefully."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(ErrorResponse(
            error=exc.detail,
            status_code=exc.status_code,
            detail=str(exc.detail)
        ))
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions gracefully."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder(ErrorResponse(
            error="Internal server error",
            status_code=500,
            detail="An unexpected error occurred. The service is still operational."
        ))
    )

# Root endpoint
@app.get("/")
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
async def health_check():
    """Comprehensive health check endpoint."""
    health_status = {
        "status": "healthy",
        "timestamp": "2025-07-06",
        "chatbot": {
            "available": chatbot_available,
            "type": chatbot_type
        }
    }
    
    # Add database health if available
    if database_available:
        try:
            db_health = check_database_health()
            health_status["database"] = db_health
        except Exception as e:
            health_status["database"] = {"status": "error", "error": str(e)}
    else:
        health_status["database"] = {"status": "not_configured"}
    
    return health_status

# Debug endpoint
@app.get("/debug/system")
async def debug_system():
    """Debug endpoint to check all system components."""
    debug_info = {
        "status": "available",
        "database": {
            "available": database_available,
            "health": "unknown"
        },
        "chatbot": {
            "available": chatbot_available,
            "type": chatbot_type,
            "capabilities": []
        },
        "environment": {
            "deployment_mode": os.getenv("DEPLOYMENT_MODE", "production"),
            "database_url_set": bool(os.getenv("DATABASE_URL")),
            "python_version": "3.x"
        }
    }
    
    # Test database if available
    if database_available:
        try:
            debug_info["database"]["health"] = check_database_health()
        except Exception as e:
            debug_info["database"]["health"] = {"error": str(e)}
    
    # Test chatbot
    if chatbot_available:
        try:
            chatbot = get_chatbot()
            if chatbot_type == "enhanced_minimal":
                debug_info["chatbot"]["capabilities"] = [
                    "product_search", "outlet_search", "calculations",
                    "real_data_matching", "agentic_planning", "context_memory"
                ]
            elif chatbot_type == "minimal":
                debug_info["chatbot"]["capabilities"] = [
                    "basic_responses", "simple_queries"
                ]
            else:
                debug_info["chatbot"]["capabilities"] = ["fallback_responses"]
        except Exception as e:
            debug_info["chatbot"]["error"] = str(e)
    
    return debug_info

# Main chat endpoint with robust error handling
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint with multi-layer error handling and fallback.
    Always returns a response, even if individual components fail.
    """
    try:
        # Validate input
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=400, 
                detail="Message cannot be empty"
            )
        
        # Get chatbot instance
        try:
            chatbot = get_chatbot()
        except Exception as e:
            logger.error(f"Failed to get chatbot: {e}")
            return ChatResponse(
                message="I'm temporarily experiencing technical difficulties. Please try again in a moment.",
                session_id=request.session_id,
                intent="error",
                confidence=0.1
            )
        
        # Process message with the chatbot
        try:
            # Try enhanced method first
            if hasattr(chatbot, 'process_message'):
                result = await chatbot.process_message(request.message, request.session_id)
                return ChatResponse(
                    message=result.get("message", "I'm sorry, I couldn't process that request properly."),
                    session_id=request.session_id,
                    intent=result.get("intent", "unknown"),
                    confidence=result.get("confidence", 0.5)
                )
            # Fallback to simple chat method
            elif hasattr(chatbot, 'chat'):
                result = chatbot.chat(request.message, request.session_id)
                return ChatResponse(
                    message=result.get("response", "I'm sorry, I couldn't process that request properly."),
                    session_id=request.session_id,
                    intent=result.get("intent", "unknown"),
                    confidence=result.get("confidence", 0.5)
                )
            else:
                # Ultimate fallback
                return ChatResponse(
                    message="Welcome to ZUS Coffee! I'm temporarily running in limited mode. Our premium drinkware collection includes tumblers, cups, and mugs. Visit our outlets in KLCC, Pavilion, Mid Valley, and more locations across KL and Selangor.",
                    session_id=request.session_id,
                    intent="fallback",
                    confidence=0.3
                )
                
        except Exception as e:
            logger.error(f"Chatbot processing error: {e}")
            return ChatResponse(
                message="I apologize for the inconvenience. I'm experiencing some technical issues but I'm still here to help! ZUS Coffee offers premium drinkware and has outlets across KL and Selangor. Please try your question again.",
                session_id=request.session_id,
                intent="error",
                confidence=0.2
            )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected chat endpoint error: {e}")
        return ChatResponse(
            message="Thank you for contacting ZUS Coffee! While I'm experiencing some technical difficulties right now, I want you to know that we offer premium drinkware and have multiple outlet locations. Please try again shortly!",
            session_id=request.session_id,
            intent="critical_error",
            confidence=0.1
        )

# Simple ping endpoint for basic connectivity testing
@app.get("/ping")
async def ping():
    """Simple ping endpoint for connectivity testing."""
    return {"status": "pong", "timestamp": "2025-07-06"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
