#!/usr/bin/env python3
"""
6. Build Agentic Chatbot Logic
Create a planner/controller in chatbot/agent.py

This module implements:
- State tracking: what the user has already said (e.g., outlet name)
- Intent detection: outlets → /outlets, products → /products, math → /calculate
- Missing info handling: ask for details if needed
- Unhappy flow handling: graceful fallbacks, friendly responses, error logging
"""

import logging
import re
import json
import requests
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from enum import Enum
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Intent(str, Enum):
    """User intent classification."""
    GREETING = "greeting"
    OUTLET_INQUIRY = "outlet_inquiry"
    PRODUCT_INQUIRY = "product_inquiry"
    CALCULATION = "calculation"
    GENERAL_QUESTION = "general_question"
    UNCLEAR = "unclear"

class UserState:
    """Track user conversation state."""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.conversation_history: List[Dict[str, Any]] = []
        self.mentioned_outlets: List[str] = []
        self.mentioned_products: List[str] = []
        self.last_intent: Optional[Intent] = None
        self.context: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_message(self, role: str, content: str, intent: Intent = None):
        """Add a message to conversation history."""
        message = {
            "role": role,
            "content": content,
            "intent": intent.value if intent else None,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(message)
        self.updated_at = datetime.now()
        
        if intent:
            self.last_intent = intent
    
    def extract_mentions(self, text: str):
        """Extract outlet and product mentions from text."""
        text_lower = text.lower()
        
        # Common outlet locations in Malaysia
        outlet_keywords = [
            'klcc', 'pavilion', 'mid valley', 'sunway', 'one utama', 'ioi mall',
            'the gardens', 'suria klcc', 'lot 10', 'fahrenheit 88', 'avenue k',
            'plaza mont kiara', 'bangsar village', 'hartamas', 'damansara',
            'petaling jaya', 'shah alam', 'subang', 'pj', 'kl', 'kuala lumpur'
        ]
        
        # Product keywords
        product_keywords = [
            'tumbler', 'mug', 'cup', 'bottle', 'flask', 'glass', 'travel mug',
            'insulated', 'thermal', 'stainless steel', 'ceramic', 'drinkware'
        ]
        
        # Extract outlet mentions
        for outlet in outlet_keywords:
            if outlet in text_lower and outlet not in self.mentioned_outlets:
                self.mentioned_outlets.append(outlet)
        
        # Extract product mentions
        for product in product_keywords:
            if product in text_lower and product not in self.mentioned_products:
                self.mentioned_products.append(product)

class IntentDetector:
    """Detect user intent from natural language."""
    
    def __init__(self):
        self.intent_patterns = {
            Intent.GREETING: [
                r'\b(hi|hello|hey|good\s+(morning|afternoon|evening)|greetings)\b',
                r'\bhow\s+are\s+you\b',
                r'\bwhat\'?s\s+up\b'
            ],
            Intent.OUTLET_INQUIRY: [
                r'\b(outlet|store|shop|location|branch|address)\b',
                r'\b(where|find|show)\s+.*\b(outlet|store|shop)\b',
                r'\b(opening|hours|time|when)\s+.*\b(open|close)\b',
                r'\bhow\s+many\s+.*\b(outlet|store)\b',
                r'\b(nearest|closest)\s+.*\b(outlet|store)\b',
                r'\bfind\s+outlets\b',
                r'\b(klcc|pavilion|pj|mall|shopping)\b',
                r'\bi\s+want\s+outlets?\b',
                r'\bshow\s+me\s+outlets?\b',
                r'\bfind\s+stores?\b',
                r'\boutlets?\s+in\b'
            ],
            Intent.PRODUCT_INQUIRY: [
                r'\b(product|drinkware|tumbler|mug|cup|bottle|flask)\b',
                r'\b(show|find|search|look\s+for)\s+.*\b(product|item|drinkware|tumbler|mug|cup)\b',
                r'\b(what|which)\s+.*\b(products|items|drinkware)\b',
                r'\b(recommend|suggest)\s+.*\b(product|drinkware)\b',
                r'\b(price|cost|how\s+much)\b.*\b(product|drinkware)\b',
                r'\bshow\s+me\s+(tumblers?|mugs?|cups?|products?|drinkware)\b',
                r'\bi\s+want\s+products?\b',
                r'\bshow\s+me\s+products?\b',
                r'\bwhat\s+products?\b'
            ],
            Intent.CALCULATION: [
                r'\b(calculate|compute|solve)\b(?!\s+outlets)(?!\s+products)',
                r'\d+\s*[+\-*/^%]\s*\d+',
                r'\b(add|subtract|multiply|divide|plus|minus|times)\s+\d+',
                r'\b(percentage|percent|%)\b',
                r'\b(square\s+root|sqrt|sin|cos|tan|log)\b',
                r'\bwhat\s+is\s+\d+',
                r'^calculate$',
                r'\bi\s+need\s+a\s+calculation\b',
                r'\bhelp\s+me\s+with\s+math\b'
            ]
        }
    
    def detect_intent(self, text: str, user_state: UserState) -> Tuple[Intent, float]:
        """Detect intent with confidence score."""
        text_lower = text.lower().strip()
        scores = {}
        
        # Calculate scores for each intent
        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            matches = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    matches += 1
                    score += 1.0
            
            # Boost score for any match in shorter pattern lists
            if matches > 0:
                # Give higher weight to matches
                base_score = matches / len(patterns) if patterns else 0.0
                # Bonus for having any matches at all
                scores[intent] = base_score + 0.3 * (matches > 0)
            else:
                scores[intent] = 0.0
        
        # Context-based adjustments
        if user_state.last_intent:
            # Boost related intents based on conversation flow
            if user_state.last_intent == Intent.OUTLET_INQUIRY:
                if any(word in text_lower for word in ['hours', 'address', 'phone', 'contact']):
                    scores[Intent.OUTLET_INQUIRY] += 0.3
            elif user_state.last_intent == Intent.PRODUCT_INQUIRY:
                if any(word in text_lower for word in ['more', 'details', 'info', 'price']):
                    scores[Intent.PRODUCT_INQUIRY] += 0.3
        
        # Find best intent
        if not scores or max(scores.values()) == 0:
            return Intent.UNCLEAR, 0.1
        
        best_intent = max(scores, key=scores.get)
        confidence = scores[best_intent]
        
        # Minimum confidence threshold
        if confidence < 0.15:
            return Intent.UNCLEAR, confidence
        
        return best_intent, confidence

class APIService:
    """Handle API calls to different endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.timeout = 10  # seconds
    
    async def call_outlets_api(self, query: str) -> Dict[str, Any]:
        """Call the /outlets endpoint."""
        try:
            url = f"{self.base_url}/outlets"
            params = {"query": query}
            
            logger.info(f"Calling outlets API: {url} with query: {query}")
            
            # Use requests with timeout
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "source": "outlets_api"
                }
            else:
                logger.warning(f"Outlets API returned status {response.status_code}: {response.text}")
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}",
                    "fallback": True
                }
                
        except requests.exceptions.Timeout:
            logger.error("Outlets API timeout")
            return {
                "success": False,
                "error": "API timeout - service may be slow",
                "fallback": True
            }
        except requests.exceptions.ConnectionError:
            logger.error("Outlets API connection error")
            return {
                "success": False,
                "error": "Cannot connect to outlets service",
                "fallback": True
            }
        except Exception as e:
            logger.error(f"Outlets API unexpected error: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "fallback": True
            }
    
    async def call_products_api(self, query: str) -> Dict[str, Any]:
        """Call the /products endpoint."""
        try:
            url = f"{self.base_url}/products"
            params = {"query": query, "top_k": 5}
            
            logger.info(f"Calling products API: {url} with query: {query}")
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "source": "products_api"
                }
            else:
                logger.warning(f"Products API returned status {response.status_code}: {response.text}")
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}",
                    "fallback": True
                }
                
        except requests.exceptions.Timeout:
            logger.error("Products API timeout")
            return {
                "success": False,
                "error": "API timeout - service may be slow",
                "fallback": True
            }
        except requests.exceptions.ConnectionError:
            logger.error("Products API connection error")
            return {
                "success": False,
                "error": "Cannot connect to products service",
                "fallback": True
            }
        except Exception as e:
            logger.error(f"Products API unexpected error: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "fallback": True
            }
    
    async def call_calculate_api(self, expression: str) -> Dict[str, Any]:
        """Call the /calculate endpoint."""
        try:
            url = f"http://localhost:8001/calculate"  # Calculator runs on port 8001
            params = {"expression": expression}
            
            logger.info(f"Calling calculator API: {url} with expression: {expression}")
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "source": "calculator_api"
                }
            elif response.status_code == 400:
                # Expected error for invalid expressions
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("detail", "Invalid expression"),
                    "user_error": True  # This is a user input issue, not a system error
                }
            else:
                logger.warning(f"Calculator API returned status {response.status_code}: {response.text}")
                return {
                    "success": False,
                    "error": f"Calculator service error (status {response.status_code})",
                    "fallback": True
                }
                
        except requests.exceptions.Timeout:
            logger.error("Calculator API timeout")
            return {
                "success": False,
                "error": "Calculator service timeout",
                "fallback": True
            }
        except requests.exceptions.ConnectionError:
            logger.error("Calculator API connection error")
            return {
                "success": False,
                "error": "Cannot connect to calculator service",
                "fallback": True
            }
        except Exception as e:
            logger.error(f"Calculator API unexpected error: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "fallback": True
            }

class AgenticChatbot:
    """Main agentic chatbot controller."""
    
    def __init__(self):
        self.intent_detector = IntentDetector()
        self.api_service = APIService()
        self.user_sessions: Dict[str, UserState] = {}
    
    def get_or_create_session(self, session_id: str = None) -> UserState:
        """Get or create user session."""
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        if session_id not in self.user_sessions:
            self.user_sessions[session_id] = UserState(session_id)
        
        return self.user_sessions[session_id]
    
    def extract_mathematical_expression(self, text: str) -> Optional[str]:
        """Extract mathematical expression from natural language."""
        text = text.lower().strip()
        
        # Remove common prefixes
        prefixes_to_remove = [
            'calculate', 'compute', 'solve', 'find', 'what is', 'what\'s',
            'can you calculate', 'please calculate', 'help me calculate'
        ]
        
        for prefix in prefixes_to_remove:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        # Remove question marks and trailing words
        text = re.sub(r'[?!.]+$', '', text)
        text = re.sub(r'\bfor me\b', '', text)
        text = re.sub(r'\bplease\b', '', text)
        
        # If it looks like a mathematical expression, return it
        if re.search(r'\d+\s*[+\-*/^%]|sqrt|sin|cos|tan|log|abs|round|pow', text):
            return text.strip()
        
        return None
    
    def check_missing_info(self, intent: Intent, text: str, user_state: UserState) -> Optional[str]:
        """Check if required information is missing for the intent."""
        
        if intent == Intent.OUTLET_INQUIRY:
            # Check if user mentioned a location
            location_indicators = ['klcc', 'pavilion', 'pj', 'kl', 'shah alam', 'subang', 'damansara']
            has_location = any(loc in text.lower() for loc in location_indicators)
            
            if not has_location and not user_state.mentioned_outlets:
                return "I'd be happy to help you find ZUS Coffee outlets! Could you please tell me which area you're looking for? (e.g., KLCC, Pavilion, PJ, etc.)"
        
        elif intent == Intent.PRODUCT_INQUIRY:
            # Check if user mentioned specific product type
            specific_products = ['tumbler', 'mug', 'cup', 'bottle', 'flask', 'glass', 'ceramic', 'stainless']
            has_specific_product = any(prod in text.lower() for prod in specific_products)
            
            # General terms like "drinkware", "products", "items" should trigger missing info
            general_terms = ['drinkware', 'products', 'items', 'what products', 'show me products']
            has_general_term_only = any(term in text.lower() for term in general_terms) and not has_specific_product
            
            if has_general_term_only or (not has_specific_product and not user_state.mentioned_products):
                return "I'd love to help you find the perfect drinkware! What type of product are you interested in? (e.g., tumbler, travel mug, glass cup, etc.)"
        
        elif intent == Intent.CALCULATION:
            # Check if there's a mathematical expression
            expression = self.extract_mathematical_expression(text)
            if not expression:
                return "I can help you with calculations! Please provide a mathematical expression (e.g., '2 + 3 * 4', 'sqrt(16)', 'sin(pi/2)')."
        
        return None
    
    def generate_fallback_response(self, intent: Intent, error_type: str) -> str:
        """Generate friendly fallback responses for different scenarios."""
        
        fallback_responses = {
            Intent.OUTLET_INQUIRY: {
                "api_down": "I'm having trouble accessing the outlet information right now. You can also visit zuscoffee.com to find store locations, or try asking me again in a moment!",
                "timeout": "The outlet search is taking longer than usual. Please try again in a moment, or visit our website for store locations.",
                "general": "I'm having trouble finding outlet information right now. You can visit zuscoffee.com for store locations, or try asking me again!"
            },
            Intent.PRODUCT_INQUIRY: {
                "api_down": "I'm having trouble accessing the product catalog right now. You can browse our drinkware collection at zuscoffee.com, or try asking me again in a moment!",
                "timeout": "The product search is taking longer than usual. Please try again in a moment, or visit our website to browse products.",
                "general": "I'm having trouble finding product information right now. You can browse our collection at zuscoffee.com, or try asking me again!"
            },
            Intent.CALCULATION: {
                "api_down": "The calculator service is temporarily unavailable. You can try using your device's calculator app, or ask me again in a moment!",
                "timeout": "The calculation is taking longer than usual. Please try again, or use your device's calculator app.",
                "general": "I'm having trouble with calculations right now. You can try using your device's calculator app, or ask me again!"
            }
        }
        
        # Determine specific error type
        if "timeout" in error_type.lower():
            error_key = "timeout"
        elif "connect" in error_type.lower() or "500" in error_type:
            error_key = "api_down"
        else:
            error_key = "general"
        
        return fallback_responses.get(intent, {}).get(error_key, 
            "I'm experiencing some technical difficulties. Please try again in a moment, or visit zuscoffee.com for more information!")
    
    async def process_message(self, message: str, session_id: str = None) -> Dict[str, Any]:
        """Process user message and generate response."""
        
        try:
            # Get or create user session
            user_state = self.get_or_create_session(session_id)
            
            # Add user message to history
            user_state.add_message("user", message)
            
            # Extract mentions
            user_state.extract_mentions(message)
            
            # Detect intent
            intent, confidence = self.intent_detector.detect_intent(message, user_state)
            
            logger.info(f"Session {user_state.session_id}: Intent={intent}, Confidence={confidence:.2f}")
            
            # Handle greeting
            if intent == Intent.GREETING:
                response = "Hello! I'm your ZUS Coffee assistant. I can help you find outlet locations, browse our drinkware products, and perform calculations. How can I help you today?"
                user_state.add_message("assistant", response, intent)
                return {
                    "response": response,
                    "intent": intent.value,
                    "confidence": confidence,
                    "session_id": user_state.session_id,
                    "action_taken": "greeting"
                }
            
            # Check for missing information
            missing_info_response = self.check_missing_info(intent, message, user_state)
            if missing_info_response:
                user_state.add_message("assistant", missing_info_response, intent)
                return {
                    "response": missing_info_response,
                    "intent": intent.value,
                    "confidence": confidence,
                    "session_id": user_state.session_id,
                    "action_taken": "ask_for_info"
                }
            
            # Process based on intent
            if intent == Intent.OUTLET_INQUIRY:
                api_result = await self.api_service.call_outlets_api(message)
                
                if api_result["success"]:
                    # Format successful response
                    outlets_data = api_result["data"]
                    total_found = outlets_data.get("total_found", 0)
                    
                    if total_found == 0:
                        response = "I couldn't find any outlets matching your query. Try asking about specific locations like 'outlets in KLCC' or 'PJ outlets'."
                    else:
                        outlets = outlets_data.get("outlets", [])
                        response = f"I found {total_found} outlet{'s' if total_found != 1 else ''} for you:\\n\\n"
                        
                        for i, outlet in enumerate(outlets[:3], 1):  # Show first 3
                            response += f"{i}. **{outlet.get('name', 'ZUS Coffee')}**\\n"
                            response += f"   📍 {outlet.get('address', 'Address not available')}\\n"
                            if outlet.get('opening_hours'):
                                response += f"   🕒 {outlet['opening_hours']}\\n"
                            response += "\\n"
                        
                        if total_found > 3:
                            response += f"... and {total_found - 3} more outlet{'s' if total_found - 3 != 1 else ''}."
                else:
                    # API failed - use fallback
                    response = self.generate_fallback_response(intent, api_result["error"])
                    logger.error(f"Outlets API failed: {api_result['error']}")
            
            elif intent == Intent.PRODUCT_INQUIRY:
                api_result = await self.api_service.call_products_api(message)
                
                if api_result["success"]:
                    # Format successful response
                    products_data = api_result["data"]
                    products = products_data.get("products", [])
                    
                    if not products:
                        response = "I couldn't find any products matching your query. Try asking about 'tumblers', 'travel mugs', or 'glass cups'."
                    else:
                        response = f"Here are some great drinkware options for you:\\n\\n"
                        
                        for i, product in enumerate(products[:3], 1):  # Show first 3
                            response += f"{i}. **{product.get('name', 'ZUS Product')}**\\n"
                            if product.get('price'):
                                response += f"   💰 {product['price']}\\n"
                            if product.get('description'):
                                response += f"   📝 {product['description'][:100]}...\\n"
                            response += "\\n"
                else:
                    # API failed - use fallback
                    response = self.generate_fallback_response(intent, api_result["error"])
                    logger.error(f"Products API failed: {api_result['error']}")
            
            elif intent == Intent.CALCULATION:
                expression = self.extract_mathematical_expression(message)
                
                if expression:
                    api_result = await self.api_service.call_calculate_api(expression)
                    
                    if api_result["success"]:
                        calc_data = api_result["data"]
                        result = calc_data.get("result")
                        response = f"The result is: **{result}**\\n\\nExpression: `{calc_data.get('expression', expression)}`"
                    else:
                        if api_result.get("user_error"):
                            # User input error - show helpful message
                            response = f"I couldn't calculate that: {api_result['error']}\\n\\nPlease check your expression and try again. For example: '2 + 3 * 4' or 'sqrt(16)'."
                        else:
                            # System error - use fallback
                            response = self.generate_fallback_response(intent, api_result["error"])
                            logger.error(f"Calculator API failed: {api_result['error']}")
                else:
                    response = "I can help with calculations! Please provide a mathematical expression (e.g., '2 + 3 * 4', 'sqrt(16)', 'sin(pi/2)')."
            
            else:
                # Unclear intent or general question
                response = "I'm here to help with ZUS Coffee outlets, drinkware products, and calculations. What would you like to know more about?"
            
            # Add response to history
            user_state.add_message("assistant", response, intent)
            
            return {
                "response": response,
                "intent": intent.value,
                "confidence": confidence,
                "session_id": user_state.session_id,
                "action_taken": f"call_{intent.value}" if intent in [Intent.OUTLET_INQUIRY, Intent.PRODUCT_INQUIRY, Intent.CALCULATION] else "general_response",
                "context": {
                    "mentioned_outlets": user_state.mentioned_outlets,
                    "mentioned_products": user_state.mentioned_products,
                    "conversation_length": len(user_state.conversation_history)
                }
            }
            
        except Exception as e:
            # Log the error but never crash
            logger.error(f"Unexpected error in process_message: {str(e)}", exc_info=True)
            
            return {
                "response": "I apologize, but I encountered an unexpected error. Please try again, or visit zuscoffee.com for more information!",
                "intent": "error",
                "confidence": 0.0,
                "session_id": session_id or "unknown",
                "action_taken": "error_fallback",
                "error": str(e)
            }

# Global chatbot instance
chatbot = AgenticChatbot()

def get_chatbot() -> AgenticChatbot:
    """Get the global chatbot instance."""
    return chatbot


