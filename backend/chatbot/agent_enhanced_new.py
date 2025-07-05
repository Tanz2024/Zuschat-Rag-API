#!/usr/bin/env python3
"""
Advanced Intelligent Chatbot Agent for ZUS Coffee
Production-ready conversational AI with sophisticated natural language understanding,
multi-turn memory, agentic planning, robust error handling, and direct database access.
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
    from services.product_search_service import get_vector_store
except ImportError:
    try:
        from services.simple_product_search import get_vector_store
        from data.database import SessionLocal, Outlet
    except ImportError:
        # Fallback for testing
        SessionLocal = None
        Outlet = None
        get_vector_store = None

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
        self.db_available = SessionLocal is not None
    
    def get_outlets(self, query: str = "", location: str = "", max_results: int = 10) -> List[Dict[str, Any]]:
        """Get outlets from database with filtering."""
        if not self.db_available:
            return []
        
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
                response = "I can't process that request. Please rephrase your question about ZUS Coffee products or outlets."
                user_state.add_message("assistant", response)
                return {
                    "response": response,
                    "session_id": session_id,
                    "intent": intent.value,
                    "confidence": confidence
                }
            
            # Handle unclear input
            if intent == Intent.UNCLEAR or confidence < 0.3:
                response = self._generate_clarification_response(user_state)
                user_state.add_message("assistant", response)
                return {
                    "response": response,
                    "session_id": session_id,
                    "intent": intent.value,
                    "confidence": confidence
                }
            
            # Route to appropriate handler
            response = await self._route_intent(intent, message, user_state)
            
            user_state.add_message("assistant", response)
            
            return {
                "response": response,
                "session_id": session_id,
                "intent": intent.value,
                "confidence": confidence
            }
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "I'm having technical difficulties. Please try again in a moment.",
                "session_id": session_id,
                "error": str(e)
            }
    
    async def _route_intent(self, intent: Intent, message: str, user_state: SmartUserState) -> str:
        """Route intent to appropriate handler."""
        
        if intent == Intent.GREETING:
            return self._handle_greeting(user_state)
        
        elif intent == Intent.FAREWELL:
            return "Thank you for using ZUS Coffee chatbot! Have a great day! ☕"
        
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
            return self._generate_helpful_response(user_state)
    
    def _handle_greeting(self, user_state: SmartUserState) -> str:
        """Handle greeting with personalization."""
        if user_state.interaction_count > 1:
            return f"Welcome back! 👋 How can I help you with ZUS Coffee today?"
        else:
            return ("Hello! 👋 Welcome to ZUS Coffee! I'm your AI assistant ready to help with:\n\n"
                   "☕ **Products** - Explore our drinkware collection\n"
                   "📍 **Outlets** - Find stores with hours & contact info\n"
                   "🧮 **Calculations** - Price calculations, tax, discounts\n"
                   "💰 **Pricing** - Product prices and comparisons\n\n"
                   "What can I help you with today?")
    
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
            
            if not outlets:
                return ("I couldn't find any outlets matching your criteria. "
                       "Could you try specifying a location like KLCC, Pavilion, or Sunway?")
            
            # Store results for context
            user_state.store_search_results("outlets", outlets)
            
            # Format response based on intent
            if intent == Intent.OUTLET_HOURS:
                return self._format_outlet_hours(outlets)
            elif intent == Intent.OUTLET_SERVICES:
                return self._format_outlet_services(outlets)
            else:
                return self._format_outlet_list(outlets, location)
        
        except Exception as e:
            logger.error(f"Error handling outlet query: {e}")
            return "I'm having trouble accessing outlet information right now. Please try again in a moment."
    
    async def _handle_product_query(self, intent: Intent, message: str, user_state: SmartUserState) -> str:
        """Handle product queries with vector search."""
        try:
            # Get products from vector search
            products = self.db_service.get_products(message, max_results=5)
            
            if not products:
                return ("I couldn't find any products matching your criteria. "
                       "Try asking about tumblers, mugs, cups, or specific features like 'dishwasher safe'.")
            
            # Filter by price if budget range specified
            if user_state.budget_range:
                min_price, max_price = user_state.budget_range
                products = [p for p in products if min_price <= p.get('sale_price', 0) <= max_price]
            
            # Store results for context
            user_state.store_search_results("products", products)
            
            return self._format_product_list(products, intent, user_state)
        
        except Exception as e:
            logger.error(f"Error handling product query: {e}")
            return "I'm having trouble accessing product information right now. Please try again in a moment."
    
    def _handle_calculation(self, intent: Intent, message: str, user_state: SmartUserState) -> str:
        """Handle calculations with enhanced logic."""
        if intent == Intent.CALCULATION:
            result = self.calculator.solve_math(message)
            if "error" in result:
                return f"I couldn't solve that calculation. {result['error']} Please provide a clear mathematical expression like '2 + 3 * 4' or '15% of 200'."
            else:
                return f"🧮 **Calculation Result:**\n**{result['expression']}** = **{result['formatted']}**"
        
        # For cart/tax calculations, would need product context
        return "I can help with calculations! Please provide a mathematical expression or specify which products you'd like to calculate pricing for."
    
    def _handle_context_recall(self, message: str, user_state: SmartUserState) -> str:
        """Handle context recall for multi-turn conversations."""
        recalled_context = user_state.recall_context(message)
        
        if recalled_context.get("outlets"):
            outlets = recalled_context["outlets"][-3:]  # Last 3 mentioned
            return f"From our earlier conversation, you were asking about these outlets:\n\n" + \
                   self._format_outlet_list(outlets, "")
        
        if recalled_context.get("products"):
            products = recalled_context["products"][-3:]  # Last 3 mentioned
            return f"From our earlier conversation, you were looking at these products:\n\n" + \
                   self._format_product_list(products, Intent.PRODUCT_INQUIRY, user_state)
        
        return "I'd be happy to help! Could you please be more specific about what you're referring to?"
    
    def _handle_about_us(self) -> str:
        """Handle about us queries."""
        return ("🏢 **About ZUS Coffee**\n\n"
               "ZUS Coffee is Malaysia's leading tech-driven coffee chain, bringing you premium coffee "
               "and innovative drinkware products. We're passionate about quality coffee and creating "
               "great experiences for our customers.\n\n"
               "📍 We have **243 outlets** across Malaysia, primarily in Kuala Lumpur and Selangor\n"
               "☕ We offer a wide range of premium drinkware including tumblers, mugs, and cups\n"
               "🚀 We're committed to innovation and technology in the coffee industry\n\n"
               "Visit zuscoffee.com to learn more!")
    
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
