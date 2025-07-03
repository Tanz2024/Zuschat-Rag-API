"""
Pydantic models for ZUS Chatbot Backend API.
Contains all request/response models and data structures.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict, Union
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Intent(str, Enum):
    """Intent classification enumeration."""
    PRODUCT_SEARCH = "product_search"
    OUTLET_SEARCH = "outlet_search"
    CALCULATION = "calculation"
    GENERAL_CHAT = "general_chat"
    GREETING = "greeting"
    GOODBYE = "goodbye"
    HELP = "help"
    UNKNOWN = "unknown"


class AgentAction(str, Enum):
    """Agent action enumeration."""
    SEARCH_PRODUCTS = "search_products"
    CALL_PRODUCT_SEARCH = "call_product_search"
    SEARCH_OUTLETS = "search_outlets"
    CALL_OUTLET_SEARCH = "call_outlet_search"
    CALCULATE = "calculate"
    CALL_CALCULATOR = "call_calculator"
    ANSWER_QUESTION = "answer_question"
    PROVIDE_ANSWER = "provide_answer"
    ASK_FOLLOWUP = "ask_followup"
    REQUEST_CLARIFICATION = "request_clarification"
    CLARIFY = "clarify"
    END_CONVERSATION = "end_conversation"


# Request Models
class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What coffee drinks do you have?",
                "session_id": "user123",
                "context": {"location": "KL"}
            }
        }


class ProductSearchRequest(BaseModel):
    """Product search request model."""
    query: str = Field(..., description="Search query for products")
    limit: Optional[int] = Field(10, ge=1, le=50, description="Maximum number of results")
    category: Optional[str] = Field(None, description="Product category filter")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "iced coffee",
                "limit": 10,
                "category": "beverages"
            }
        }


class OutletQueryRequest(BaseModel):
    """Outlet query request model."""
    query: str = Field(..., description="Query for outlet search")
    location: Optional[str] = Field(None, description="Location filter")
    limit: Optional[int] = Field(10, ge=1, le=50, description="Maximum number of results")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "outlets near KLCC",
                "location": "Kuala Lumpur",
                "limit": 10
            }
        }


class CalculatorRequest(BaseModel):
    """Calculator request model."""
    expression: str = Field(..., description="Mathematical expression to calculate")

    class Config:
        json_schema_extra = {
            "example": {
                "expression": "15 * 2 + 5"
            }
        }


# Response Models
class ProductInfo(BaseModel):
    """Product information model."""
    name: str
    description: Optional[str] = None
    price: Optional[str] = None
    category: Optional[str] = None
    availability: Optional[str] = None
    tags: Optional[List[str]] = None


class OutletInfo(BaseModel):
    """Outlet information model."""
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    hours: Optional[str] = None
    location: Optional[str] = None
    services: Optional[List[str]] = None


class ChatMessage(BaseModel):
    """Chat message model."""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConversationState(BaseModel):
    """Conversation state model."""
    session_id: str
    messages: List[ChatMessage] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    intent_history: List[Intent] = Field(default_factory=list)
    current_intent: Optional[Intent] = Field(None, description="Current detected intent")
    last_action: Optional[AgentAction] = Field(None, description="Last action taken")
    last_activity: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    user_preferences: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChatResponse(BaseModel):
    """Chat response model."""
    message: str = Field(..., description="Assistant response message")
    session_id: str = Field(..., description="Session ID")
    intent: Optional[Intent] = Field(None, description="Detected intent")
    action: Optional[AgentAction] = Field(None, description="Agent action taken")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Response context")
    products: Optional[List[ProductInfo]] = Field(None, description="Related products")
    outlets: Optional[List[OutletInfo]] = Field(None, description="Related outlets")
    calculation_result: Optional[Union[float, str]] = Field(None, description="Calculation result if applicable")
    suggestions: Optional[List[str]] = Field(None, description="Follow-up suggestions")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Response confidence score")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Here are some coffee drinks we have available:",
                "session_id": "user123",
                "intent": "product_search",
                "action": "search_products",
                "products": [
                    {
                        "name": "Iced Americano",
                        "description": "Rich espresso with cold water",
                        "price": "RM 8.50",
                        "category": "coffee"
                    }
                ],
                "suggestions": ["Would you like to know about our pastries?"]
            }
        }


class ProductSearchResponse(BaseModel):
    """Product search response model."""
    products: List[ProductInfo] = Field(..., description="Found products")
    total_count: int = Field(..., description="Total number of matching products")
    query: str = Field(..., description="Original search query")

    class Config:
        json_schema_extra = {
            "example": {
                "products": [
                    {
                        "name": "Iced Americano",
                        "description": "Rich espresso with cold water",
                        "price": "RM 8.50",
                        "category": "coffee"
                    }
                ],
                "total_count": 15,
                "query": "iced coffee"
            }
        }


class OutletQueryResponse(BaseModel):
    """Outlet query response model."""
    outlets: List[OutletInfo] = Field(..., description="Found outlets")
    total_count: int = Field(..., description="Total number of matching outlets")
    query: str = Field(..., description="Original search query")

    class Config:
        json_schema_extra = {
            "example": {
                "outlets": [
                    {
                        "name": "ZUS Coffee KLCC",
                        "address": "Lot 421, Level 4, Suria KLCC",
                        "phone": "+60 3-2382 0832",
                        "hours": "8:00 AM - 10:00 PM",
                        "location": "Kuala Lumpur"
                    }
                ],
                "total_count": 5,
                "query": "outlets near KLCC"
            }
        }


class CalculatorResponse(BaseModel):
    """Calculator response model."""
    result: Union[float, str] = Field(..., description="Calculation result")
    expression: str = Field(..., description="Original expression")
    success: bool = Field(..., description="Whether calculation was successful")
    error: Optional[str] = Field(None, description="Error message if calculation failed")

    class Config:
        json_schema_extra = {
            "example": {
                "result": 35.0,
                "expression": "15 * 2 + 5",
                "success": True
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid input provided",
                "error_code": "VALIDATION_ERROR",
                "details": {"field": "message", "issue": "cannot be empty"},
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now)
    version: Optional[str] = Field(None, description="API version")
    services: Optional[Dict[str, str]] = Field(None, description="Service statuses")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00Z",
                "version": "1.0.0",
                "services": {
                    "database": "connected",
                    "vector_store": "loaded",
                    "ai_service": "ready"
                }
            }
        }
