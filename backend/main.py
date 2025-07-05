from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import logging
import asyncio
from contextlib import asynccontextmanager

# Import models and services
from models import (
    ChatRequest, ChatResponse, ProductSearchRequest, ProductSearchResponse,
    OutletQueryRequest, OutletQueryResponse, CalculatorRequest, CalculatorResponse,
    ErrorResponse
)
from data.database import get_db, create_tables

# Import enhanced chatbot agent with fallback
try:
    from chatbot.enhanced_minimal_agent import get_chatbot
    print("✅ Using ENHANCED MINIMAL chatbot with real data keyword matching")
    ENHANCED_CHATBOT = True
except Exception as e:
    print(f"⚠️  Enhanced minimal chatbot not available: {e}")
    try:
        from chatbot.minimal_agent import get_chatbot
        print("✅ Using minimal working chatbot")
        ENHANCED_CHATBOT = True
    except Exception as e2:
        print(f"❌ No chatbot available: {e2}")
        # Create a simple fallback
        def get_chatbot():
            class SimpleAgent:
                def chat(self, message, session_id="default"):
                    return {"response": "I'm temporarily unavailable. Please try again later."}
            return SimpleAgent()
        ENHANCED_CHATBOT = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting ZUS Chatbot Backend...")
    
    # Initialize database
    create_tables()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ZUS Chatbot Backend...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="ZUS Coffee Chatbot API",
    description="Enhanced chatbot API for ZUS Coffee with real product and outlet data",
    version="1.0.0",
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

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions gracefully."""
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
            detail="An unexpected error occurred"
        ))
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "ZUS Coffee Chatbot API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "debug": "/debug/chatbot"
        },
        "description": "Enhanced chatbot with real ZUS Coffee product and outlet data"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "chatbot": "available" if ENHANCED_CHATBOT else "limited",
        "timestamp": "2024-12-27"
    }

# Debug endpoint
@app.get("/debug/chatbot")
async def debug_chatbot():
    """Debug endpoint to check chatbot status."""
    try:
        chatbot = get_chatbot()
        return {
            "status": "available",
            "type": "enhanced_minimal_agent" if ENHANCED_CHATBOT else "fallback",
            "capabilities": [
                "product_search",
                "outlet_search", 
                "calculations",
                "real_data_matching"
            ] if ENHANCED_CHATBOT else ["basic_responses"]
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# Main chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Main chat endpoint for processing user messages."""
    try:
        # Basic validation
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if len(request.message) > 1000:
            raise HTTPException(status_code=400, detail="Message too long (max 1000 characters)")
        
        # Use enhanced chatbot if available, otherwise fallback
        if ENHANCED_CHATBOT:
            try:
                # Process with enhanced chatbot
                chatbot = get_chatbot()
                response_data = await chatbot.process_message(
                    message=request.message,
                    session_id=request.session_id
                )
                
                return ChatResponse(
                    message=response_data.get("message", response_data.get("response", "No response")),
                    session_id=response_data.get("session_id", request.session_id)
                )
            except Exception as enhanced_error:
                logger.error(f"Enhanced chatbot failed: {enhanced_error}")
                # Fallback to basic response
                return ChatResponse(
                    message="Hello! I'm temporarily experiencing some technical difficulties. I can still help you with ZUS Coffee products, outlet locations, and general inquiries. What would you like to know?",
                    session_id=request.session_id
                )
        else:
            try:
                # Fallback to basic chatbot
                controller = get_chatbot()
                response = await controller.process_message(request, db)
                return response
            except Exception as basic_error:
                logger.error(f"Basic chatbot failed: {basic_error}")
                # Ultimate fallback
                return ChatResponse(
                    message="I'm currently experiencing technical difficulties. Please try again in a moment. I'm here to help with ZUS Coffee information!",
                    session_id=request.session_id
                )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Run the application
if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable (Render sets this)
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Set to False for production
        log_level="info"
    )
