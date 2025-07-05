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

# Import enhanced chatbot agent
from chatbot.agent_enhanced import get_chatbot

# Try to import ML-based search, fallback to simple search
try:
    from services.product_search_service import get_vector_store
    print("Using ML-based product search")
except ImportError:
    from services.simple_product_search import get_vector_store
    print("ML dependencies not available, using simple product search")

from services.real_data_outlet_filter import get_real_data_outlet_filter
from tools.calculator import get_calculator

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
    
    # Initialize vector store
    vector_store = get_vector_store()
    if vector_store:
        logger.info("Product vector store initialized")
    else:
        logger.warning("Product vector store failed to initialize")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ZUS Chatbot Backend...")

# Create FastAPI app
app = FastAPI(
    title="ZUS Chatbot Backend",
    description="AI-powered chatbot for ZUS Coffee with RAG, Text2SQL, and tool calling capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    error_response = ErrorResponse(
        error=exc.detail,
        error_type="HTTPException",
        message=exc.detail,
        status_code=exc.status_code
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(error_response.dict())
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    error_response = ErrorResponse(
        error="Internal server error",
        error_type="InternalServerError",
        message="An unexpected error occurred",
        status_code=500
    )
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder(error_response.dict())
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - Welcome message."""
    return {
        "message": "Welcome to ZUS Coffee Chatbot API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "chat": "/chat",
            "products": "/products",
            "outlets": "/outlets",
            "calculator": "/calculator"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "ZUS Chatbot Backend is running",
        "version": "1.0.0"
    }

# Main chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Enhanced chatbot endpoint with advanced intelligence."""
    try:
        # Validate input
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if len(request.message) > 1000:
            raise HTTPException(status_code=400, detail="Message too long (max 1000 characters)")
        
        # Process message with enhanced chatbot
        chatbot = get_chatbot()
        response_data = await chatbot.process_message(
            message=request.message,
            session_id=request.session_id
        )
        
        # Convert to expected response format
        return ChatResponse(
            message=response_data["response"],
            session_id=response_data["session_id"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Product search endpoint
@app.get("/products", response_model=ProductSearchResponse)
async def search_products(query: str, top_k: int = 15):
    """Search products using vector similarity."""
    try:
        # Validate parameters
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        if top_k < 1 or top_k > 50:
            raise HTTPException(status_code=400, detail="top_k must be between 1 and 50")
        
        # Search products
        vector_store = get_vector_store()
        if not vector_store:
            raise HTTPException(status_code=500, detail="Vector store not available")
        
        results = vector_store.search(query, top_k)
        summary = vector_store.generate_summary(query, results)
        
        return ProductSearchResponse(
            products=results,
            summary=summary,
            total_found=len(results)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in products endpoint: {e}")
        raise HTTPException(status_code=500, detail="Error searching products")

# Outlet search endpoint
@app.get("/outlets", response_model=OutletQueryResponse)
async def search_outlets(query: str = None, location: str = None, db: Session = Depends(get_db)):
    """Search outlets using natural language to SQL conversion."""
    try:
        # Use location as query if query is not provided
        search_query = query or location or ""
        
        # Validate parameters
        if not search_query.strip():
            raise HTTPException(status_code=400, detail="Query or location parameter is required")
        
        # Search outlets using real data filter
        outlet_filter = get_real_data_outlet_filter()
        result = outlet_filter.generate_response(search_query)
        
        # For API response, we need to extract outlets from the response
        outlets = outlet_filter.search_outlets(search_query)
        
        return OutletQueryResponse(
            outlets=outlets,
            sql_query="Real data filter query",
            total_found=len(outlets)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in outlets endpoint: {e}")
        raise HTTPException(status_code=500, detail="Error searching outlets")

# Calculator endpoint  
@app.post("/calculator", response_model=CalculatorResponse)
async def calculate(request: CalculatorRequest):
    """Perform mathematical calculations."""
    try:
        # Validate input
        if not request.expression or not request.expression.strip():
            raise HTTPException(status_code=400, detail="Expression cannot be empty")
        
        if len(request.expression) > 200:
            raise HTTPException(status_code=400, detail="Expression too long (max 200 characters)")
        
        # Calculate
        calculator = get_calculator()
        result = calculator.calculate(request.expression)
        
        # Handle None result for invalid expressions
        calculated_result = result.get('result')
        if calculated_result is None and not result['is_valid']:
            calculated_result = 0.0  # Default for invalid expressions
        
        return CalculatorResponse(
            result=calculated_result,
            expression=result.get('normalized_expression', request.expression),
            is_valid=result['is_valid'],
            error_message=result.get('error_message')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in calculate endpoint: {e}")
        raise HTTPException(status_code=500, detail="Error performing calculation")

# Legacy endpoint for backwards compatibility
@app.post("/calculate", response_model=CalculatorResponse)
async def calculate_legacy(request: CalculatorRequest):
    """Legacy calculate endpoint - redirects to /calculator."""
    return await calculate(request)

# Admin endpoints for data management
@app.post("/admin/rebuild-vector-store")
async def rebuild_vector_store():
    """Rebuild the vector store from current product data."""
    try:
        vector_store = get_vector_store()
        if not vector_store:
            raise HTTPException(status_code=500, detail="Vector store not available")
        
        vector_store.build_index()
        vector_store.save_index()
        return {"message": "Vector store rebuilt successfully"}
        
    except Exception as e:
        logger.error(f"Error rebuilding vector store: {e}")
        raise HTTPException(status_code=500, detail="Error rebuilding vector store")

# Development endpoints
@app.get("/debug/sessions")
async def get_active_sessions():
    """Get information about active chat sessions (debug only)."""
    try:
        chatbot = get_chatbot()
        sessions_info = {
            "total_sessions": len(chatbot.user_sessions),
            "session_ids": list(chatbot.user_sessions.keys())
        }
        return sessions_info
        
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving session information")

@app.get("/debug/vector-store-status")
async def vector_store_status():
    """Get vector store status information."""
    try:
        vector_store = get_vector_store()
        if not vector_store:
            return {"status": "Vector store not available"}
        
        status = {
            "index_loaded": vector_store.index is not None,
            "total_products": len(vector_store.products),
            "index_size": vector_store.index.ntotal if vector_store.index else 0,
            "model": "all-MiniLM-L6-v2",
            "dimension": vector_store.dimension
        }
        return status
        
    except Exception as e:
        logger.error(f"Error getting enhanced vector store status: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving enhanced vector store status")

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
