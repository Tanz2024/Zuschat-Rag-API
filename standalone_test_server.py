#!/usr/bin/env python3
"""
Standalone FastAPI server for testing chatbot without database
This is for testing the Render deployment issue
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any
import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(__file__)
backend_dir = os.path.join(current_dir, "backend")
sys.path.insert(0, backend_dir)

# Import the chatbot agent
from chatbot.enhanced_minimal_agent import EnhancedMinimalAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ZUS Coffee Chatbot API - Standalone Test",
    description="Standalone chatbot API for testing without database",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot
chatbot_agent = EnhancedMinimalAgent()

@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "ZUS Coffee Chatbot API - Standalone Test",
        "version": "1.0.0",
        "status": "active",
        "mode": "standalone_test",
        "endpoints": {
            "chat": "/chat",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "chatbot": "available",
        "mode": "standalone_test",
        "timestamp": "2025-07-06"
    }

@app.post("/chat")
async def chat_endpoint(request: Dict[str, Any]):
    """Chat endpoint for testing."""
    try:
        message = request.get("message", "")
        session_id = request.get("session_id", "default")
        
        if not message:
            return JSONResponse(
                status_code=400,
                content={"error": "Message is required"}
            )
        
        # Process with chatbot agent
        result = await chatbot_agent.process_message(message, session_id)
        
        return {
            "response": result.get("message", "No response available"),
            "session_id": session_id,
            "intent": result.get("intent", "unknown"),
            "confidence": result.get("confidence", 0.5)
        }
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(e)
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
