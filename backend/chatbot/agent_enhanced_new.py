#!/usr/bin/env python3
"""
Advanced Intelligent Chatbot Agent for ZUS Coffee
Production-ready conversational AI with sophisticated natural language understanding,
multi-turn memory, agentic planning, robust error handling, and direct database access.
Enhanced with professional response formatting for production deployment.
"""

import logging
import re
import json
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import math
import os
from sqlalchemy.orm import Session

# Import database and models
try:
    from data.database import SessionLocal, Outlet
    DB_AVAILABLE = True
except (ImportError, ValueError) as e:
    logger.warning(f"Database not available: {e}")
    SessionLocal = None
    Outlet = None
    DB_AVAILABLE = False

# Import vector search service
try:
    from services.product_search_service import get_vector_store
    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    try:
        from services.simple_product_search import get_vector_store
        VECTOR_SEARCH_AVAILABLE = True
    except ImportError:
        # Fallback for testing
        get_vector_store = None
        VECTOR_SEARCH_AVAILABLE = False

# Import professional formatter
try:
    from .professional_formatter import ProfessionalResponseFormatter
except ImportError:
    try:
        from chatbot.professional_formatter import ProfessionalResponseFormatter
    except ImportError:
        # Fallback if formatter not available
        class ProfessionalResponseFormatter:
            @staticmethod
            def clean_response(response: str) -> str:
                import re
                response = re.sub(r'\n+', ' ', response)
                response = re.sub(r'\s+', ' ', response)
                return response.strip()
            
            @staticmethod
            def format_greeting(is_returning_user: bool = False) -> str:
                if is_returning_user:
                    return "👋 Welcome back to ZUS Coffee! How can I assist you today? I'm here to help with product recommendations, outlet locations, pricing calculations, and any questions about our services."
                else:
                    return "🎉 Hello and welcome to ZUS Coffee! I'm your friendly AI assistant, ready to help you explore our premium drinkware collection, find nearby outlets with their hours and services, calculate pricing and taxes, or answer any questions about ZUS Coffee. What would you like to know today?"
            
            @staticmethod
            def format_farewell() -> str:
                return "☕ Thank you for choosing ZUS Coffee! Have a wonderful day and we look forward to serving you again soon. Don't forget to check out our latest products and visit our outlets for the best coffee experience! 🌟"
            
            @staticmethod
            def format_outlet_list(outlets, location="") -> str:
                if not outlets:
                    return "🔍 I couldn't find any ZUS Coffee outlets matching your search criteria. Could you try specifying a more specific location like KLCC, Pavilion KL, Sunway Pyramid, or mention your preferred area? I'll help you find the perfect outlet nearby!"
                
                location_text = f" in {location}" if location else ""
                response = f"🏪 Great! I found {len(outlets)} ZUS Coffee outlet{'s' if len(outlets) > 1 else ''}{location_text} for you: "
                
                outlet_details = []
                for i, outlet in enumerate(outlets, 1):
                    details = f"{i}. **{outlet['name']}** 📍 {outlet['address']}"
                    outlet_details.append(details)
                
                response += " | ".join(outlet_details)
                response += " 💡 Would you like more details about any of these outlets, such as contact information or specific services?"
                return response
            
            @staticmethod
            def format_outlet_hours(outlets) -> str:
                if not outlets:
                    return "⏰ I don't have specific hour information available right now. Could you specify which outlet you're interested in? I'll help you find their exact operating hours!"
                
                response = f"🕒 Here are the operating hours for our ZUS Coffee outlet{'s' if len(outlets) > 1 else ''}: "
                hour_details = []
                for outlet in outlets:
                    detail = f"**{outlet['name']}** Hours available upon request"
                    hour_details.append(detail)
                
                response += " | ".join(hour_details)
                response += " 📞 For the most up-to-date hours or holiday schedules, feel free to call the outlet directly or ask me about specific days!"
                return response
            
            @staticmethod
            def format_product_list(products, user_context="") -> str:
                if not products:
                    return "🔍 I couldn't find products matching your criteria right now. Try asking about our popular items like 'tumblers', 'coffee mugs', 'travel cups', or specific features like 'dishwasher safe' or 'double wall insulation'. I'm here to help you find the perfect ZUS drinkware!"
                
                response = f"☕ Excellent choice! Here are {len(products)} fantastic ZUS Coffee product{'s' if len(products) > 1 else ''} I'd recommend: "
                
                product_details = []
                for i, product in enumerate(products, 1):
                    detail = f"{i}. **{product.get('name', 'Premium Product')}** 💰 {product.get('price', 'Contact for pricing')}"
                    product_details.append(detail)
                
                response += " | ".join(product_details)
                response += " 🛒 Would you like more details about any of these products, or shall I help you with pricing calculations?"
                return response
            
            @staticmethod
            def format_calculation_result(expression, result, calculation_type="general") -> str:
                return f"🧮 Calculation complete! **{expression}** equals **{result}**. Is there anything else I can calculate for you?"
            
            @staticmethod
            def format_error_message(error_type="general") -> str:
                if error_type == "calculation":
                    return "🤔 I had trouble with that calculation. Could you rephrase it using numbers and basic operations like '+', '-', '*', '/' or percentages? For example: '15% of 50' or '25.50 + 18.90'. I'm here to help!"
                elif error_type == "product":
                    return "🔍 I'm having trouble accessing our product catalog right now. Could you try asking about specific items like 'coffee mugs', 'tumblers', or 'travel cups'? I'll do my best to help you find what you're looking for!"
                elif error_type == "outlet":
                    return "📍 I'm having difficulty finding outlet information at the moment. Could you specify a location like 'KLCC', 'Sunway', or your preferred area? I'll help you locate the nearest ZUS Coffee outlet!"
                elif error_type == "malicious":
                    return "🛡️ I can't process that type of request for security reasons. I'm here to help with ZUS Coffee products, outlet locations, calculations, and general inquiries. What would you like to know about our coffee and drinkware?"
                else:
                    return "🤝 I want to help you, but I'm not quite sure what you're looking for. Could you rephrase your question? I can assist with product information, outlet locations, pricing calculations, or general ZUS Coffee inquiries!"
            
            @staticmethod
            def format_clarification_request() -> str:
                return "🤝 I'd love to help you find exactly what you need! Could you please be more specific? I can assist with 🏪 outlet locations and hours, ☕ product recommendations and details, 🧮 pricing calculations and tax computations, or 💰 current promotions and offers. What interests you most?"
            
            @staticmethod
            def format_about_us() -> str:
                return "🏢 ZUS Coffee is Malaysia's leading tech-driven coffee chain, passionate about delivering premium coffee experiences and innovative drinkware products! 📍 We proudly operate 243 outlets across Malaysia, especially in Kuala Lumpur and Selangor, serving quality coffee and offering an amazing selection of tumblers, mugs, and cups. 🚀 We're committed to innovation, technology, and creating exceptional customer experiences. Visit zuscoffee.com to discover more about our journey and latest offerings!"
            
            @staticmethod
            def format_context_recall(context_type, items) -> str:
                return "🔄 I'd be happy to continue helping you! Could you remind me what specific information you're looking for? I have access to all our outlet and product details!"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Intent(str, Enum):
    """Enhanced intent classification for all conversation scenarios."""
    GREETING = "greeting"
    FAREWELL = "farewell"
    OUTLET_INQUIRY = "outlet_inquiry"
    OUTLET_HOURS = "outlet_hours"
    OUTLET_SERVICES = "outlet_services"
    OUTLET_CONTACT = "outlet_contact"
    PRODUCT_INQUIRY = "product_inquiry"
    PRODUCT_COMPARISON = "product_comparison"
    PRODUCT_RECOMMENDATION = "product_recommendation"
    PRICE_INQUIRY = "price_inquiry"
    PRICE_FILTER = "price_filter"
    CALCULATION = "calculation"
    CART_CALCULATION = "cart_calculation"
    TAX_CALCULATION = "tax_calculation"
    DISCOUNT_INQUIRY = "discount_inquiry"
    PROMOTION_INQUIRY = "promotion_inquiry"
    ABOUT_US = "about_us"
    GENERAL_QUESTION = "general_question"
    COMPLAINT = "complaint"
    COMPLIMENT = "compliment"
    MALICIOUS = "malicious"
    CONTEXT_RECALL = "context_recall"
    UNCLEAR = "unclear"

class SmartUserState:
    """Advanced user state tracking with sequential conversation memory."""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Multi-turn memory
        self.mentioned_outlets: List[Dict[str, Any]] = []
        self.mentioned_products: List[Dict[str, Any]] = []
        self.last_search_results: Dict[str, List] = {}
        self.saved_context: Dict[str, Any] = {}
        
        # Location and preferences
        self.preferred_location: Optional[str] = None
        self.current_context_location: Optional[str] = None
        self.budget_range: Optional[Tuple[float, float]] = None
        self.last_intent: Optional[Intent] = None
        
        # User preferences
        self.user_preferences: Dict[str, Any] = {
            "preferred_material": None,
            "preferred_capacity": None,
            "preferred_features": [],
            "price_sensitivity": "medium"
        }
        
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.interaction_count = 0
    
    def add_message(self, role: str, content: str, intent: Intent = None, metadata: Dict = None):
        """Add message with context tracking."""
        message = {
            "role": role,
            "content": content,
            "intent": intent.value if intent else None,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)
        self.updated_at = datetime.now()
        self.interaction_count += 1
        
        if intent:
            self.last_intent = intent
        
        if role == "user":
            self._extract_context(content)
    
    def _extract_context(self, content: str):
        """Extract context from user messages."""
        content_lower = content.lower()
        
        # Location extraction
        location_map = {
            'klcc': 'KLCC', 'pavilion': 'Pavilion KL', 'mid valley': 'Mid Valley',
            'sunway': 'Sunway', 'one utama': 'One Utama', 'bangsar': 'Bangsar',
            'damansara': 'Damansara', 'pj': 'Petaling Jaya', 'shah alam': 'Shah Alam',
            'ss2': 'SS2', 'ss 2': 'SS2', 'kuala lumpur': 'Kuala Lumpur', 'selangor': 'Selangor'
        }
        
        for keyword, location in location_map.items():
            if keyword in content_lower:
                self.current_context_location = location
                if not self.preferred_location:
                    self.preferred_location = location
                break
        
        # Price range extraction
        if 'under rm' in content_lower or 'below rm' in content_lower:
            price_match = re.search(r'(under|below)\s+rm\s*(\d+(?:\.\d{2})?)', content_lower)
            if price_match:
                self.budget_range = (0, float(price_match.group(2)))
    
    def store_search_results(self, result_type: str, results: List[Dict]):
        """Store search results for context recall."""
        self.last_search_results[result_type] = results
        if result_type == "outlets":
            self.mentioned_outlets.extend(results)
        elif result_type == "products":
            self.mentioned_products.extend(results)
    
    def recall_context(self, query: str) -> Dict[str, Any]:
        """Recall previous context based on user query."""
        query_lower = query.lower()
        
        if any(phrase in query_lower for phrase in ["back to", "earlier", "before"]):
            return self.saved_context
        
        if any(phrase in query_lower for phrase in ["which one", "that one", "those"]):
            return {
                "outlets": self.mentioned_outlets,
                "products": self.mentioned_products,
                "search_results": self.last_search_results
            }
        
        return {}

class IntelligentIntentDetector:
    """Advanced intent detection with security and robustness."""
    
    def __init__(self):
        self.intent_patterns = {
            Intent.GREETING: [
                r'\b(hi|hello|hey|good\s+(morning|afternoon|evening))\b',
                r'\bhow\s+are\s+you\b'
            ],
            Intent.FAREWELL: [
                r'\b(bye|goodbye|see\s+you|thanks\s+bye)\b',
                r'\b(that\'?s\s+all|i\'?m\s+done)\b'
            ],
            Intent.OUTLET_INQUIRY: [
                r'\b(outlet|store|shop|location|branch)\b',
                r'\b(where|find|show)\s+.*\b(outlet|store)\b',
                r'\bis\s+there\s+.*\b(outlet|store)\s+.*\b(in|at)\b',
                r'\b(klcc|pavilion|pj|sunway|damansara|bangsar)\b'
            ],
            Intent.OUTLET_HOURS: [
                r'\b(opening|hours|time|when)\s+.*\b(open|close)\b',
                r'\bwhat\s+time.*\b(open|close)\b',
                r'\bis\s+.*\s+open\b',
                r'\bopen\s+(after|until|at)\s+\d+'
            ],
            Intent.OUTLET_SERVICES: [
                r'\b(service|services|delivery|dine.?in|takeaway)\b',
                r'\bis\s+.*\s+(delivery|dine.?in)\s+available\b',
                r'\bdo\s+.*\s+(deliver|have\s+wifi)\b'
            ],
            Intent.PRODUCT_INQUIRY: [
                r'\b(product|drinkware|tumbler|mug|cup|bottle)\b',
                r'\b(show|find|tell\s+me\s+about)\s+.*\b(tumbler|mug|cup)\b',
                r'\bdo\s+you\s+(have|sell)\b.*\b(mug|cup|tumbler)\b',
                r'\b(dishwasher|microwave).?safe\b',
                r'\bmatte\s+finish\b'
            ],
            Intent.PRICE_FILTER: [
                r'\b(under|below|less\s+than)\s+rm\s*\d+\b',
                r'\b(above|over|more\s+than)\s+rm\s*\d+\b',
                r'\bbetween\s+rm\s*\d+\s+and\s+rm\s*\d+\b',
                r'\bshow\s+.*\s+(under|below)\s+rm\s*\d+\b'
            ],
            Intent.PRICE_INQUIRY: [
                r'\b(price|cost|how\s+much)\b(?!\s+(under|below))',
                r'\bhow\s+much\s+(is|does|for)\b'
            ],
            Intent.CALCULATION: [
                r'\b(calculate|compute|solve)\b(?!\s+(price|cost))',
                r'^\s*\d+\s*[+\-*/]\s*\d+',
                r'\b\d+\s*[+\-*/]\s*\d+\b',
                r'\b\d+%\s+of\s+\d+\b'
            ],
            Intent.CART_CALCULATION: [
                r'\bcalculate\s+.*\b(price|cost|total)\b',
                r'\bhow\s+much\s+.*\btotal\b',
                r'\bprice\s+for\s+\d+\b',
                r'\btotal\s+cost\b'
            ],
            Intent.TAX_CALCULATION: [
                r'\b(tax|sst|with\s+tax)\b',
                r'\b6%\s*(tax|sst)\b'
            ],
            Intent.CONTEXT_RECALL: [
                r'\b(which\s+one|that\s+one|those|them)\b',
                r'\b(back\s+to|earlier|before)\b',
                r'\breturn\s+to\b'
            ],
            Intent.ABOUT_US: [
                r'\b(about|company|history)\b.*\bzus\b',
                r'\bwho\s+(are\s+you|is\s+zus)\b'
            ],
            Intent.MALICIOUS: [
                r'\b(select|insert|update|delete|drop|union)\b.*\b(table|database)\b',
                r'1\s*=\s*1',
                r'or\s+1\s*=\s*1',
                r'<script|javascript:|eval\(',
                r'\bdrop\s+table\b',
                r'--\s*$'
            ],
            Intent.DISCOUNT_INQUIRY: [
                r'\b(discount|sale|promotion|offer)\b',
                r'\bon\s+sale\b'
            ]
        }
    
    def detect_intent(self, message: str, context: SmartUserState = None) -> Tuple[Intent, float]:
        """Detect intent with security checks."""
        if not message or not message.strip():
            return Intent.UNCLEAR, 0.0
        
        message_lower = message.lower().strip()
        
        # Security check first
        if self._check_malicious(message_lower):
            return Intent.MALICIOUS, 1.0
        
        # Garbage input check
        if self._is_garbage(message):
            return Intent.UNCLEAR, 0.0
        
        # Pattern matching
        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = self._calculate_score(message_lower, patterns)
            if score > 0:
                intent_scores[intent] = score
        
        if not intent_scores:
            return Intent.UNCLEAR, 0.0
        
        best_intent, confidence = max(intent_scores.items(), key=lambda x: x[1])
        
        if confidence < 0.3:
            return Intent.UNCLEAR, confidence
        
        return best_intent, confidence
    
    def _check_malicious(self, message: str) -> bool:
        """Check for malicious patterns."""
        for pattern in self.intent_patterns[Intent.MALICIOUS]:
            if re.search(pattern, message, re.IGNORECASE):
                logger.warning(f"Malicious pattern detected: {message[:50]}...")
                return True
        return False
    
    def _is_garbage(self, message: str) -> bool:
        """Detect garbage input."""
        clean_message = re.sub(r'\s+', '', message)
        if not clean_message:
            return True
        
        alphanumeric_ratio = len(re.findall(r'[a-zA-Z0-9]', clean_message)) / len(clean_message)
        return alphanumeric_ratio < 0.3 and len(clean_message) > 3
    
    def _calculate_score(self, message: str, patterns: List[str]) -> float:
        """Calculate confidence score."""
        total_score = 0.0
        for pattern in patterns:
            if re.search(pattern, message, re.IGNORECASE):
                total_score += 0.4
        return min(total_score, 1.0)

class EnhancedCalculationEngine:
    """Advanced calculation engine with robust error handling."""
    
    def solve_math(self, expression: str) -> Dict[str, Any]:
        """Safely solve mathematical expressions."""
        try:
            # Clean expression - fixed regex pattern
            clean_expr = re.sub(r'[^0-9+\-*/.()%\s]', '', expression)
            
            # Handle percentage calculations
            if '%' in expression:
                percent_match = re.search(r'(\d+(?:\.\d+)?)%\s*(?:of\s*)?(\d+(?:\.\d+)?)', expression)
                if percent_match:
                    percent = float(percent_match.group(1))
                    value = float(percent_match.group(2))
                    result = (percent / 100) * value
                    return {
                        "expression": f"{percent}% of {value}",
                        "result": result,
                        "formatted": f"{result:.2f}"
                    }
            
            if not clean_expr.strip():
                return {"error": "Invalid expression"}
            
            # Safely evaluate
            result = eval(clean_expr)
            return {
                "expression": clean_expr,
                "result": result,
                "formatted": f"{result:.6f}".rstrip('0').rstrip('.') if isinstance(result, float) else str(result)
            }
        
        except Exception as e:
            return {"error": f"Calculation error: {str(e)}"}

class DatabaseService:
    """Direct database access service."""
    
    def __init__(self):
        self.db_available = DB_AVAILABLE and SessionLocal is not None
        self.vector_search_available = VECTOR_SEARCH_AVAILABLE
    
    def get_outlets(self, query: str = "", location: str = "", max_results: int = 10) -> List[Dict[str, Any]]:
        """Get outlets from database with filtering."""
        if not self.db_available:
            logger.warning("Database not available, returning fallback outlet data")
            # Return some fallback outlet data
            return [
                {
                    "name": "ZUS Coffee KLCC",
                    "address": "Lot G-316A, Ground Floor, Suria KLCC, Kuala Lumpur City Centre, 50088 Kuala Lumpur",
                    "opening_hours": {"monday": "8:00 AM - 10:00 PM", "tuesday": "8:00 AM - 10:00 PM"},
                    "services": ["Dine-in", "Takeaway", "Delivery"]
                },
                {
                    "name": "ZUS Coffee Pavilion KL",
                    "address": "Lot 1.39.00, Level 1, Pavilion Kuala Lumpur, 168, Jalan Bukit Bintang, 55100 Kuala Lumpur",
                    "opening_hours": {"monday": "10:00 AM - 10:00 PM", "tuesday": "10:00 AM - 10:00 PM"},
                    "services": ["Dine-in", "Takeaway"]
                }
            ]
        
        try:
            with SessionLocal() as db:
                outlets_query = db.query(Outlet)
                
                # Filter by location if specified
                if location:
                    outlets_query = outlets_query.filter(
                        Outlet.address.ilike(f'%{location}%')
                    )
                
                # General text search
                if query:
                    outlets_query = outlets_query.filter(
                        Outlet.name.ilike(f'%{query}%') |
                        Outlet.address.ilike(f'%{query}%')
                    )
                
                outlets = outlets_query.limit(max_results).all()
                
                return [
                    {
                        "name": outlet.name,
                        "address": outlet.address,
                        "opening_hours": json.loads(outlet.opening_hours) if outlet.opening_hours else {},
                        "services": json.loads(outlet.services) if outlet.services else []
                    }
                    for outlet in outlets
                ]
        
        except Exception as e:
            logger.error(f"Database error getting outlets: {e}")
            return []
    
    def get_products(self, query: str = "", max_results: int = 10) -> List[Dict[str, Any]]:
        """Get products using vector search."""
        if not self.vector_search_available:
            logger.warning("Vector search not available, returning fallback product data")
            # Return some fallback product data
            return [
                {
                    "name": "ZUS Coffee Premium Tumbler",
                    "price": "RM 25.90",
                    "description": "Premium double-wall insulated tumbler perfect for your daily coffee",
                    "features": ["Double wall insulation", "Leak-proof", "BPA-free"],
                    "capacity": "350ml",
                    "material": "Stainless steel"
                },
                {
                    "name": "ZUS Coffee Travel Mug",
                    "price": "RM 32.90",
                    "description": "Perfect travel companion for coffee lovers",
                    "features": ["Spill-proof lid", "Easy grip handle", "Dishwasher safe"],
                    "capacity": "500ml",
                    "material": "Ceramic with silicone grip"
                }
            ]
        
        try:
            vector_store = get_vector_store()
            if not vector_store:
                return []
            
            results = vector_store.search(query, max_results)
            return results
        
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            return []

class EnhancedChatbotAgent:
    """Main enhanced chatbot agent with all advanced features."""
    
    def __init__(self):
        self.intent_detector = IntelligentIntentDetector()
        self.calculator = EnhancedCalculationEngine()
        self.db_service = DatabaseService()
        self.user_sessions: Dict[str, SmartUserState] = {}
    
    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """Process message with full intelligence and context."""
        try:
            # Get or create user state
            if session_id not in self.user_sessions:
                self.user_sessions[session_id] = SmartUserState(session_id)
            
            user_state = self.user_sessions[session_id]
            
            # Detect intent
            intent, confidence = self.intent_detector.detect_intent(message, user_state)
            
            # Add message to history
            user_state.add_message("user", message, intent)
            
            # Handle malicious input
            if intent == Intent.MALICIOUS:
                response = ProfessionalResponseFormatter.format_error_message("malicious")
                response = ProfessionalResponseFormatter.clean_response(response)
                user_state.add_message("assistant", response)
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": intent.value,
                    "confidence": confidence
                }
            
            # Handle unclear input
            if intent == Intent.UNCLEAR or confidence < 0.3:
                response = ProfessionalResponseFormatter.format_clarification_request()
                response = ProfessionalResponseFormatter.clean_response(response)
                user_state.add_message("assistant", response)
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": intent.value,
                    "confidence": confidence
                }
            
            # Route to appropriate handler
            response = await self._route_intent(intent, message, user_state)
            response = ProfessionalResponseFormatter.clean_response(response)
            
            user_state.add_message("assistant", response)
            
            return {
                "message": response,
                "session_id": session_id,
                "intent": intent.value,
                "confidence": confidence
            }
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            response = "🔧 I'm experiencing some technical difficulties right now. Please try again in a moment, and I'll be happy to help you with ZUS Coffee information, outlet locations, or product recommendations!"
            response = ProfessionalResponseFormatter.clean_response(response)
            return {
                "message": response,
                "session_id": session_id,
                "error": str(e)
            }
    
    async def _route_intent(self, intent: Intent, message: str, user_state: SmartUserState) -> str:
        """Route intent to appropriate handler."""
        
        if intent == Intent.GREETING:
            return self._handle_greeting(user_state)
        
        elif intent == Intent.FAREWELL:
            response = ProfessionalResponseFormatter.format_farewell()
            return ProfessionalResponseFormatter.clean_response(response)
        
        elif intent in [Intent.OUTLET_INQUIRY, Intent.OUTLET_HOURS, Intent.OUTLET_SERVICES]:
            return await self._handle_outlet_query(intent, message, user_state)
        
        elif intent in [Intent.PRODUCT_INQUIRY, Intent.PRODUCT_RECOMMENDATION, Intent.PRICE_FILTER]:
            return await self._handle_product_query(intent, message, user_state)
        
        elif intent in [Intent.CALCULATION, Intent.CART_CALCULATION, Intent.TAX_CALCULATION]:
            return self._handle_calculation(intent, message, user_state)
        
        elif intent == Intent.CONTEXT_RECALL:
            return self._handle_context_recall(message, user_state)
        
        elif intent == Intent.ABOUT_US:
            return self._handle_about_us()
        
        else:
            response = ProfessionalResponseFormatter.format_clarification_request()
            return ProfessionalResponseFormatter.clean_response(response)
    
    def _handle_greeting(self, user_state: SmartUserState) -> str:
        """Handle greeting with personalization."""
        is_returning = user_state.interaction_count > 1
        response = ProfessionalResponseFormatter.format_greeting(is_returning)
        return ProfessionalResponseFormatter.clean_response(response)
    
    async def _handle_outlet_query(self, intent: Intent, message: str, user_state: SmartUserState) -> str:
        """Handle outlet queries with database access."""
        try:
            # Extract location from message or use context
            location = user_state.current_context_location or user_state.preferred_location or ""
            
            # Get outlets from database
            outlets = self.db_service.get_outlets(
                query=message,
                location=location,
                max_results=5
            )
            
            # Store results for context
            if outlets:
                user_state.store_search_results("outlets", outlets)
            
            # Format response based on intent
            if intent == Intent.OUTLET_HOURS:
                response = ProfessionalResponseFormatter.format_outlet_hours(outlets)
            elif intent == Intent.OUTLET_SERVICES:
                response = ProfessionalResponseFormatter.format_outlet_list(outlets, location)
            else:
                response = ProfessionalResponseFormatter.format_outlet_list(outlets, location)
            
            return ProfessionalResponseFormatter.clean_response(response)
        
        except Exception as e:
            logger.error(f"Error handling outlet query: {e}")
            response = ProfessionalResponseFormatter.format_error_message("outlet")
            return ProfessionalResponseFormatter.clean_response(response)
    
    async def _handle_product_query(self, intent: Intent, message: str, user_state: SmartUserState) -> str:
        """Handle product queries with vector search."""
        try:
            # Get products from vector search
            products = self.db_service.get_products(message, max_results=5)
            
            # Filter by price if budget range specified
            if user_state.budget_range and products:
                min_price, max_price = user_state.budget_range
                products = [p for p in products if min_price <= p.get('sale_price', 0) <= max_price]
            
            # Store results for context
            if products:
                user_state.store_search_results("products", products)
            
            response = ProfessionalResponseFormatter.format_product_list(products, str(intent))
            return ProfessionalResponseFormatter.clean_response(response)
        
        except Exception as e:
            logger.error(f"Error handling product query: {e}")
            response = ProfessionalResponseFormatter.format_error_message("product")
            return ProfessionalResponseFormatter.clean_response(response)
    
    def _handle_calculation(self, intent: Intent, message: str, user_state: SmartUserState) -> str:
        """Handle calculations with enhanced logic."""
        if intent == Intent.CALCULATION:
            result = self.calculator.solve_math(message)
            if "error" in result:
                response = ProfessionalResponseFormatter.format_error_message("calculation")
                return ProfessionalResponseFormatter.clean_response(response)
            else:
                calculation_type = "general"
                if "%" in message.lower() or "tax" in message.lower():
                    calculation_type = "tax"
                elif "discount" in message.lower():
                    calculation_type = "discount"
                elif "total" in message.lower() or "cart" in message.lower():
                    calculation_type = "cart"
                
                response = ProfessionalResponseFormatter.format_calculation_result(
                    result['expression'], result['formatted'], calculation_type
                )
                return ProfessionalResponseFormatter.clean_response(response)
        
        # For cart/tax calculations, would need product context
        response = "🧮 I'm ready to help with your calculations! Please provide a mathematical expression like '25.50 + 18.90', percentage calculations like '15% of 200', or let me know which products you'd like pricing calculations for."
        return ProfessionalResponseFormatter.clean_response(response)
    
    def _handle_context_recall(self, message: str, user_state: SmartUserState) -> str:
        """Handle context recall for multi-turn conversations."""
        recalled_context = user_state.recall_context(message)
        
        if recalled_context.get("outlets"):
            outlets = recalled_context["outlets"][-3:]  # Last 3 mentioned
            response = ProfessionalResponseFormatter.format_context_recall("outlets", outlets)
            return ProfessionalResponseFormatter.clean_response(response)
        
        if recalled_context.get("products"):
            products = recalled_context["products"][-3:]  # Last 3 mentioned
            response = ProfessionalResponseFormatter.format_context_recall("products", products)
            return ProfessionalResponseFormatter.clean_response(response)
        
        response = ProfessionalResponseFormatter.format_context_recall("general", [])
        return ProfessionalResponseFormatter.clean_response(response)
    
    def _handle_about_us(self) -> str:
        """Handle about us queries."""
        response = ProfessionalResponseFormatter.format_about_us()
        return ProfessionalResponseFormatter.clean_response(response)
    
    def _generate_clarification_response(self, user_state: SmartUserState) -> str:
        """Generate helpful clarification."""
        return ("I'd love to help you! 😊 Could you please rephrase your question or let me know if you're looking for:\n"
               "• Product information or recommendations\n"
               "• Outlet locations and details\n"
               "• Price calculations\n"
               "• Current promotions\n\n"
               "What specific information can I assist you with?")
    
    def _generate_helpful_response(self, user_state: SmartUserState) -> str:
        """Generate helpful fallback response."""
        return ("I'm here to help with ZUS Coffee! 😊 You can ask me about:\n\n"
               "🏪 **Outlets** - locations, hours, services\n"
               "☕ **Products** - drinkware, features, prices\n"
               "🧮 **Calculations** - pricing, tax, totals\n"
               "ℹ️ **Information** - about ZUS Coffee\n\n"
               "What would you like to know?")
    
    def _format_outlet_list(self, outlets: List[Dict], location: str) -> str:
        """Format outlet list for display."""
        if not outlets:
            return "No outlets found."
        
        response_parts = [f"🏪 **ZUS Coffee Outlets" + (f" in {location}" if location else "") + ":**\n"]
        
        for i, outlet in enumerate(outlets, 1):
            response_parts.append(f"**{i}. {outlet['name']}**")
            response_parts.append(f"📍 {outlet['address']}")
            
            # Add hours if available
            hours = outlet.get('opening_hours', {})
            if hours and isinstance(hours, dict):
                # Show today's hours or general hours
                today = datetime.now().strftime('%A').lower()
                if today in hours:
                    response_parts.append(f"🕒 Today: {hours[today]}")
                elif 'monday' in hours:
                    response_parts.append(f"🕒 Hours: {hours['monday']}")
            
            # Add services if available
            services = outlet.get('services', [])
            if services:
                if isinstance(services, list):
                    response_parts.append(f"🔧 Services: {', '.join(services)}")
            
            response_parts.append("")  # Empty line
        
        return "\n".join(response_parts)
    
    def _format_outlet_hours(self, outlets: List[Dict]) -> str:
        """Format outlet hours specifically."""
        if not outlets:
            return "No outlet hours information available."
        
        response_parts = ["🕒 **Outlet Hours:**\n"]
        
        for outlet in outlets:
            response_parts.append(f"**{outlet['name']}**")
            hours = outlet.get('opening_hours', {})
            if hours and isinstance(hours, dict):
                for day, time in hours.items():
                    response_parts.append(f"• {day.title()}: {time}")
            else:
                response_parts.append("• Hours not available")
            response_parts.append("")
        
        return "\n".join(response_parts)
    
    def _format_outlet_services(self, outlets: List[Dict]) -> str:
        """Format outlet services specifically."""
        if not outlets:
            return "No outlet services information available."
        
        response_parts = ["🔧 **Outlet Services:**\n"]
        
        for outlet in outlets:
            response_parts.append(f"**{outlet['name']}**")
            services = outlet.get('services', [])
            if services:
                if isinstance(services, list):
                    for service in services:
                        response_parts.append(f"• {service}")
                else:
                    response_parts.append(f"• {services}")
            else:
                response_parts.append("• Services information not available")
            response_parts.append("")
        
        return "\n".join(response_parts)
    
    def _format_product_list(self, products: List[Dict], intent: Intent, user_state: SmartUserState) -> str:
        """Format product list for display."""
        if not products:
            return "No products found matching your criteria."
        
        response_parts = ["☕ **ZUS Coffee Products:**\n"]
        
        for i, product in enumerate(products, 1):
            response_parts.append(f"**{i}. {product.get('name', 'Unknown Product')}**")
            
            # Price information
            price = product.get('price', 'N/A')
            sale_price = product.get('sale_price')
            regular_price = product.get('regular_price')
            
            if sale_price and regular_price and sale_price < float(regular_price.replace('RM ', '').replace(',', '')):
                response_parts.append(f"💰 **{price}** ~~{regular_price}~~ (On Sale!)")
            else:
                response_parts.append(f"💰 Price: {price}")
            
            # Description
            description = product.get('description', '')
            if description:
                response_parts.append(f"📝 {description[:100]}{'...' if len(description) > 100 else ''}")
            
            # Features
            features = product.get('features', [])
            if features and isinstance(features, list):
                response_parts.append(f"✨ Features: {', '.join(features[:3])}")
            
            # Capacity and material
            capacity = product.get('capacity')
            material = product.get('material')
            if capacity:
                response_parts.append(f"📏 Capacity: {capacity}")
            if material:
                response_parts.append(f"🧱 Material: {material}")
            
            response_parts.append("")  # Empty line
        
        # Add helpful suggestion based on user preferences
        if user_state.budget_range:
            min_price, max_price = user_state.budget_range
            response_parts.append(f"💡 *Showing products in your budget range: RM {min_price:.0f} - RM {max_price:.0f}*")
        
        return "\n".join(response_parts)

# Global chatbot instance
_chatbot_instance = None

def get_chatbot() -> EnhancedChatbotAgent:
    """Get or create the global chatbot instance."""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = EnhancedChatbotAgent()
    return _chatbot_instance
