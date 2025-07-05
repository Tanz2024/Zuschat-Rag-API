#!/usr/bin/env python3
"""
Advanced Intelligent Chatbot Agent for ZUS Coffee
Production-ready conversational AI with sophisticated natural language understanding
"""

import logging
import re
import json
import requests
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Intent(str, Enum):
    """Enhanced intent classification for intelligent conversation handling."""
    GREETING = "greeting"
    FAREWELL = "farewell"
    OUTLET_INQUIRY = "outlet_inquiry"
    OUTLET_HOURS = "outlet_hours"
    OUTLET_CONTACT = "outlet_contact"
    PRODUCT_INQUIRY = "product_inquiry"
    PRODUCT_COMPARISON = "product_comparison"
    PRODUCT_RECOMMENDATION = "product_recommendation"
    PRICE_INQUIRY = "price_inquiry"
    CALCULATION = "calculation"
    CART_CALCULATION = "cart_calculation"
    TAX_CALCULATION = "tax_calculation"
    DISCOUNT_INQUIRY = "discount_inquiry"
    PROMOTION_INQUIRY = "promotion_inquiry"
    GENERAL_QUESTION = "general_question"
    COMPLAINT = "complaint"
    COMPLIMENT = "compliment"
    UNCLEAR = "unclear"

class SmartUserState:
    """Advanced user state tracking with intelligence and context awareness."""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.conversation_history: List[Dict[str, Any]] = []
        self.mentioned_outlets: List[str] = []
        self.mentioned_products: List[str] = []
        self.preferred_location: Optional[str] = None
        self.budget_range: Optional[Tuple[float, float]] = None
        self.last_intent: Optional[Intent] = None
        self.context: Dict[str, Any] = {}
        self.user_preferences: Dict[str, Any] = {
            "preferred_material": None,
            "preferred_capacity": None,
            "price_sensitivity": "medium"
        }
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.interaction_count = 0
    
    def add_message(self, role: str, content: str, intent: Intent = None, metadata: Dict = None):
        """Add message with intelligent context extraction."""
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
        
        # Extract context from user messages
        if role == "user":
            self._extract_context(content)
    
    def _extract_context(self, content: str):
        """Extract intelligent context from user input."""
        content_lower = content.lower()
        
        # Extract location preferences
        location_map = {
            'klcc': 'KLCC area', 'pavilion': 'Pavilion KL', 'mid valley': 'Mid Valley',
            'sunway': 'Sunway', 'one utama': 'One Utama', 'bangsar': 'Bangsar',
            'damansara': 'Damansara', 'pj': 'Petaling Jaya', 'shah alam': 'Shah Alam'
        }
        
        for keyword, location in location_map.items():
            if keyword in content_lower:
                self.preferred_location = location
                break
        
        # Extract budget information
        price_matches = re.findall(r'rm\s*(\d+(?:\.\d{2})?)', content_lower)
        if price_matches:
            prices = [float(p) for p in price_matches]
            if len(prices) == 1:
                self.budget_range = (0, prices[0])
            elif len(prices) >= 2:
                self.budget_range = (min(prices), max(prices))
        
        # Extract material preferences
        if 'stainless steel' in content_lower or 'steel' in content_lower:
            self.user_preferences['preferred_material'] = 'stainless steel'
        elif 'ceramic' in content_lower:
            self.user_preferences['preferred_material'] = 'ceramic'
        elif 'acrylic' in content_lower:
            self.user_preferences['preferred_material'] = 'acrylic'
        
        # Extract capacity preferences
        if any(word in content_lower for word in ['large', 'big', '600ml', '650ml', '20oz', '22oz']):
            self.user_preferences['preferred_capacity'] = 'large'
        elif any(word in content_lower for word in ['small', 'compact', '350ml', '12oz', '14oz']):
            self.user_preferences['preferred_capacity'] = 'small'
        elif any(word in content_lower for word in ['medium', '500ml', '16oz', '17oz']):
            self.user_preferences['preferred_capacity'] = 'medium'
    
    def get_context_summary(self) -> str:
        """Generate intelligent conversation summary."""
        summary_parts = []
        
        if self.preferred_location:
            summary_parts.append(f"Interested in {self.preferred_location}")
        
        if self.budget_range:
            summary_parts.append(f"Budget: RM {self.budget_range[0]:.0f}-{self.budget_range[1]:.0f}")
        
        if self.user_preferences['preferred_material']:
            summary_parts.append(f"Prefers {self.user_preferences['preferred_material']}")
        
        recent_intents = [msg.get('intent') for msg in self.conversation_history[-3:] if msg.get('intent')]
        if recent_intents:
            summary_parts.append(f"Recent focus: {', '.join(set(recent_intents))}")
        
        return "; ".join(summary_parts) if summary_parts else "General conversation"

class IntelligentIntentDetector:
    """Advanced intent detection with context awareness and confidence scoring."""
    
    def __init__(self):
        self.intent_patterns = {
            Intent.GREETING: [
                r'\b(hi|hello|hey|good\s+(morning|afternoon|evening)|greetings)\b',
                r'\bhow\s+are\s+you\b', r'\bwhat\'?s\s+up\b'
            ],
            Intent.FAREWELL: [
                r'\b(bye|goodbye|see\s+you|farewell|thanks\s+bye)\b',
                r'\b(that\'?s\s+all|i\'?m\s+done|finished)\b'
            ],
            Intent.OUTLET_INQUIRY: [
                r'\b(outlet|store|shop|location|branch|address|find\s+store)\b',
                r'\b(where|find|show)\s+.*\b(outlet|store|shop|location)\b',
                r'\bhow\s+many\s+.*\b(outlet|store|location)\b',
                r'\b(nearest|closest)\s+.*\b(outlet|store|location)\b',
                r'\b(klcc|pavilion|pj|mall|shopping|damansara|bangsar)\b'
            ],
            Intent.OUTLET_HOURS: [
                r'\b(opening|hours|time|when)\s+.*\b(open|close|operating)\b',
                r'\bwhat\s+time.*\b(open|close)\b', r'\bis\s+.*\s+open\b'
            ],
            Intent.OUTLET_CONTACT: [
                r'\b(phone|contact|call|number|email)\b.*\b(outlet|store)\b',
                r'\bhow\s+to\s+contact\b'
            ],
            Intent.PRODUCT_INQUIRY: [
                r'\b(product|drinkware|tumbler|mug|cup|bottle|flask|item)\b',
                r'\b(show|find|search)\s+.*\b(product|drinkware|tumbler|mug|cup)\b',
                r'\b(what|which)\s+.*\b(products|items|drinkware|cups|mugs|tumblers)\b',
                r'\b(ceramic|stainless\s+steel|acrylic)\s+(mug|cup|tumbler)\b'
            ],
            Intent.PRODUCT_COMPARISON: [
                r'\b(compare|comparison|vs|versus|difference|better)\b.*\b(product|tumbler|mug|cup)\b',
                r'\bwhich\s+is\s+better\b', r'\bwhat\'?s\s+the\s+difference\b'
            ],
            Intent.PRODUCT_RECOMMENDATION: [
                r'\b(recommend|suggest|best|top|popular)\b.*\b(product|drinkware|tumbler|mug|cup)\b',
                r'\bwhat\s+do\s+you\s+recommend\b', r'\bbest\s+seller\b'
            ],
            Intent.PRICE_INQUIRY: [
                r'\b(price|cost|how\s+much|expensive|cheap|affordable)\b',
                r'\brm\s*\d+', r'\b(budget|under|below|above)\s+.*\s+rm\b'
            ],
            Intent.CART_CALCULATION: [
                r'\b(cart|order|total|checkout|purchase)\s+.*\b(price|cost|total)\b',
                r'\bcalculate\s+.*\b(price|cost|total|order)\b',
                r'\bhow\s+much\s+.*\b(total|altogether|combined)\b',
                r'\bprice\s+for\s+\d+\b', r'\btotal\s+cost\s+of\b'
            ],
            Intent.TAX_CALCULATION: [
                r'\b(tax|sst|including\s+tax|with\s+tax|after\s+tax)\b',
                r'\b6%\s*(tax|sst)\b'
            ],
            Intent.CALCULATION: [
                r'\b(calculate|compute|solve|math)\b(?!\s+price)(?!\s+cost)',
                r'\d+\s*[+\-*/^%]\s*\d+',
                r'\b(add|subtract|multiply|divide)\s+\d+\b'
            ],
            Intent.DISCOUNT_INQUIRY: [
                r'\b(discount|sale|offer|promotion|deal|cheaper)\b',
                r'\bon\s+sale\b', r'\bspecial\s+(price|offer)\b'
            ],
            Intent.PROMOTION_INQUIRY: [
                r'\b(promotion|promo|offer|deal|special)\b',
                r'\bbuy\s+\d+\s+free\s+\d+\b', r'\bcurrent\s+(promotion|offer)\b'
            ],
            Intent.GENERAL_QUESTION: [
                r'\b(help|information|about|tell\s+me|explain)\b',
                r'\bcan\s+you\s+help\b', r'\bwhat\s+(can|do)\s+you\b'
            ],
            Intent.COMPLAINT: [
                r'\b(problem|issue|complaint|wrong|error|bad|terrible)\b',
                r'\bnot\s+(working|good|happy)\b'
            ],
            Intent.COMPLIMENT: [
                r'\b(great|excellent|amazing|wonderful|fantastic|love|perfect)\b',
                r'\bthank\s+you\b', r'\bgreat\s+(job|work|service)\b'
            ]
        }
    
    def detect_intent(self, text: str, user_state: SmartUserState) -> Tuple[Intent, float]:
        """Detect intent with advanced context awareness."""
        text_lower = text.lower().strip()
        scores = {}
        
        # Base pattern matching with scoring
        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    matches += 1
                    score += 1.0
            
            if matches > 0:
                scores[intent] = (score / len(patterns)) + 0.2 * min(matches / len(patterns), 1.0)
            else:
                scores[intent] = 0.0
        
        # Context-based boosting
        if user_state.last_intent:
            self._apply_context_boost(scores, text_lower, user_state.last_intent)
        
        # Number detection for calculations
        if re.search(r'\\d+', text_lower):
            if any(word in text_lower for word in ['total', 'cost', 'price', 'rm']):
                scores[Intent.CART_CALCULATION] = scores.get(Intent.CART_CALCULATION, 0) + 0.4
            elif any(word in text_lower for word in ['calculate', 'math', '+', '-', '*', '/']):
                scores[Intent.CALCULATION] = scores.get(Intent.CALCULATION, 0) + 0.3
        
        # Find best intent
        if not scores or max(scores.values()) == 0:
            return Intent.UNCLEAR, 0.1
        
        best_intent = max(scores, key=scores.get)
        confidence = min(scores[best_intent], 1.0)
        
        if confidence < 0.2:
            return Intent.UNCLEAR, confidence
        
        return best_intent, confidence
    
    def _apply_context_boost(self, scores: Dict, text: str, last_intent: Intent):
        """Apply context-based intent boosting."""
        if last_intent == Intent.OUTLET_INQUIRY:
            if any(word in text for word in ['hours', 'time', 'open', 'close']):
                scores[Intent.OUTLET_HOURS] = scores.get(Intent.OUTLET_HOURS, 0) + 0.3
            elif any(word in text for word in ['phone', 'contact', 'call']):
                scores[Intent.OUTLET_CONTACT] = scores.get(Intent.OUTLET_CONTACT, 0) + 0.3
        
        elif last_intent == Intent.PRODUCT_INQUIRY:
            if any(word in text for word in ['price', 'cost', 'much']):
                scores[Intent.PRICE_INQUIRY] = scores.get(Intent.PRICE_INQUIRY, 0) + 0.3
            elif any(word in text for word in ['compare', 'vs', 'difference']):
                scores[Intent.PRODUCT_COMPARISON] = scores.get(Intent.PRODUCT_COMPARISON, 0) + 0.3

class SmartCalculationEngine:
    """Advanced calculation engine for pricing, tax, and complex calculations."""
    
    def __init__(self):
        self.tax_rate = 0.06  # 6% SST for Malaysia
    
    def parse_cart_request(self, text: str, available_products: List[Dict]) -> Dict[str, Any]:
        """Parse natural language cart requests into structured data."""
        text_lower = text.lower()
        cart_items = []
        
        for product in available_products:
            product_name = product.get('name', '').lower()
            
            # Check if product is mentioned
            if any(word in text_lower for word in product_name.split()[:3]):  # Check first 3 words
                quantity = self._extract_quantity(text_lower, product_name)
                if quantity > 0:
                    price = float(product.get('sale_price', 0) or 
                                product.get('price', '0').replace('RM ', '').replace(',', ''))
                    
                    cart_items.append({
                        'name': product.get('name'),
                        'price': price,
                        'quantity': quantity,
                        'subtotal': price * quantity,
                        'on_sale': product.get('on_sale', False),
                        'category': product.get('category', '')
                    })
        
        return {'items': cart_items}
    
    def _extract_quantity(self, text: str, product_name: str) -> int:
        """Extract quantity for specific product."""
        # Look for number patterns near product name
        quantity_patterns = [
            r'(\\d+)\\s*(?:x\\s*)?(?:' + re.escape(product_name.split()[0]) + ')',
            r'(\\d+)\\s+(?:of\\s+)?' + re.escape(product_name.split()[0])
        ]
        
        for pattern in quantity_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return 1  # Default quantity
    
    def calculate_with_breakdown(self, cart_items: List[Dict], include_tax: bool = True) -> Dict[str, Any]:
        """Calculate total with detailed breakdown."""
        subtotal = sum(item['subtotal'] for item in cart_items)
        tax_amount = subtotal * self.tax_rate if include_tax else 0.0
        total = subtotal + tax_amount
        
        return {
            'items': cart_items,
            'subtotal': subtotal,
            'tax_rate': self.tax_rate if include_tax else 0.0,
            'tax_amount': tax_amount,
            'total': total,
            'item_count': len(cart_items)
        }
    
    def format_calculation_response(self, breakdown: Dict[str, Any]) -> str:
        """Format calculation into user-friendly response."""
        if not breakdown['items']:
            return "I couldn't find any products to calculate. Please specify which ZUS Coffee products you'd like to calculate the price for."
        
        response_parts = ["🧮 **Price Calculation:**\\n"]
        
        # List items
        for i, item in enumerate(breakdown['items'], 1):
            response_parts.append(f"**{i}. {item['name']}**")
            response_parts.append(f"   • RM {item['price']:.2f} x {item['quantity']} = RM {item['subtotal']:.2f}")
            if item.get('on_sale'):
                response_parts.append("   • ✨ On Sale!")
            response_parts.append("")
        
        # Summary
        response_parts.append("📊 **Summary:**")
        response_parts.append(f"• Subtotal: RM {breakdown['subtotal']:.2f}")
        
        if breakdown['tax_amount'] > 0:
            response_parts.append(f"• Tax (6% SST): RM {breakdown['tax_amount']:.2f}")
        
        response_parts.append(f"• **Total: RM {breakdown['total']:.2f}**")
        
        return "\\n".join(response_parts)
    
    def solve_math(self, expression: str) -> Dict[str, Any]:
        """Safely solve mathematical expressions."""
        try:
            # Clean expression - fix regex pattern
            clean_expr = re.sub(r'[^0-9+\-*/.()%\s]', '', expression)
            
            # Handle percentage calculations
            if '%' in expression:
                # Convert "15% of 100" to "15 * 100 / 100"
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
            
            # Safely evaluate the expression
            result = eval(clean_expr)
            return {
                "expression": clean_expr,
                "result": result,
                "formatted": f"{result:.6f}".rstrip('0').rstrip('.') if isinstance(result, float) else str(result)
            }
        
        except Exception as e:
            return {"error": f"Calculation error: {str(e)}"}

class EnhancedAPIService:
    """Enhanced API service with intelligent data handling."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.timeout = 15
    
    async def call_outlets_api(self, query: str) -> Dict[str, Any]:
        """Call outlets API with enhanced error handling."""
        try:
            url = f"{self.base_url}/outlets"
            response = requests.get(url, params={"query": query}, timeout=self.timeout)
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"API returned status {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Outlets API error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def call_products_api(self, query: str, top_k: int = 12) -> Dict[str, Any]:
        """Call products API with enhanced filtering."""
        try:
            url = f"{self.base_url}/products"
            response = requests.get(url, params={"query": query, "top_k": top_k}, timeout=self.timeout)
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"API returned status {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Products API error: {str(e)}")
            return {"success": False, "error": str(e)}

class AdvancedZUSChatbot:
    """
    Advanced ZUS Coffee Chatbot - Production Ready
    Intelligent conversational AI with context awareness and natural responses.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.intent_detector = IntelligentIntentDetector()
        self.api_service = EnhancedAPIService(base_url)
        self.calculation_engine = SmartCalculationEngine()
        self.user_sessions: Dict[str, SmartUserState] = {}
    
    def get_or_create_session(self, session_id: str = None) -> SmartUserState:
        """Get or create user session."""
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        if session_id not in self.user_sessions:
            self.user_sessions[session_id] = SmartUserState(session_id)
        
        return self.user_sessions[session_id]
    
    async def process_message(self, message: str, session_id: str = None) -> Dict[str, Any]:
        """Main message processing with advanced intelligence."""
        try:
            user_state = self.get_or_create_session(session_id)
            user_state.add_message("user", message)
            
            logger.info(f"Processing: '{message[:100]}...' | Context: {user_state.get_context_summary()}")
            
            # Detect intent
            intent, confidence = self.intent_detector.detect_intent(message, user_state)
            
            # Check for missing info
            missing_info = self._check_missing_info(intent, message, user_state)
            if missing_info:
                response = missing_info
                response_type = "clarification"
            else:
                response, response_type = await self._generate_response(intent, message, user_state)
            
            user_state.add_message("assistant", response, intent, {"confidence": confidence})
            
            return {
                "response": response,
                "intent": intent.value,
                "confidence": confidence,
                "session_id": user_state.session_id,
                "response_type": response_type
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "response": "I apologize, but I encountered an error. Please try again or rephrase your question.",
                "intent": Intent.UNCLEAR.value,
                "confidence": 0.0,
                "session_id": session_id or "unknown",
                "response_type": "error"
            }
    
    def _check_missing_info(self, intent: Intent, text: str, user_state: SmartUserState) -> Optional[str]:
        """Check for missing information with intelligent prompting."""
        text_lower = text.lower()
        
        if intent == Intent.OUTLET_INQUIRY:
            if not any(loc in text_lower for loc in ['klcc', 'pavilion', 'pj', 'bangsar', 'damansara', 'kl']) and not user_state.preferred_location:
                return ("I'd be happy to help you find ZUS Coffee outlets! 📍 Which area are you looking for? "
                       "For example: KLCC, Pavilion, PJ, Bangsar, or any specific location.")
        
        elif intent == Intent.CART_CALCULATION:
            if not re.search(r'\\d+', text) and not any(p in text_lower for p in ['cup', 'tumbler', 'mug']):
                return ("I can calculate your order total! 🧮 Please specify which products and quantities. "
                       "For example: '2 ZUS OG Cups and 1 All-Can Tumbler' or 'Calculate price for 3 ceramic mugs'.")
        
        elif intent == Intent.PRICE_INQUIRY:
            if not any(p in text_lower for p in ['cup', 'tumbler', 'mug', 'drinkware', 'product']):
                return ("I can help with pricing! 💰 Which specific product would you like to know the price for? "
                       "You can ask about tumblers, mugs, cups, or any ZUS drinkware.")
        
        return None
    
    async def _generate_response(self, intent: Intent, message: str, user_state: SmartUserState) -> Tuple[str, str]:
        """Generate intelligent responses based on intent."""
        
        if intent == Intent.GREETING:
            if user_state.interaction_count == 1:
                return ("Hello! 👋 Welcome to ZUS Coffee! I'm your AI assistant ready to help with:\\n\\n"
                       "☕ **Products** - Explore our drinkware collection\\n"
                       "📍 **Outlets** - Find stores with hours & contact info\\n"
                       "🧮 **Calculations** - Get totals with tax included\\n"
                       "🎯 **Recommendations** - Find perfect drinkware for you\\n"
                       "💰 **Promotions** - Current deals and offers\\n\\n"
                       "What can I help you with today? 😊"), "greeting"
            else:
                return (f"Hello again! 👋 I see we were discussing {user_state.get_context_summary().lower()}. "
                       "How can I help you further? 😊"), "greeting"
        
        elif intent == Intent.FAREWELL:
            return ("Thank you for choosing ZUS Coffee! ☕ Have a wonderful day and see you again soon! 👋"), "farewell"
        
        elif intent in [Intent.OUTLET_INQUIRY, Intent.OUTLET_HOURS, Intent.OUTLET_CONTACT]:
            return await self._handle_outlet_inquiry(message, user_state), "outlet_info"
        
        elif intent in [Intent.PRODUCT_INQUIRY, Intent.PRODUCT_RECOMMENDATION]:
            return await self._handle_product_inquiry(message, user_state), "product_info"
        
        elif intent == Intent.PRODUCT_COMPARISON:
            return await self._handle_product_comparison(message, user_state), "product_comparison"
        
        elif intent in [Intent.PRICE_INQUIRY, Intent.CART_CALCULATION, Intent.TAX_CALCULATION]:
            return await self._handle_pricing_inquiry(message, user_state), "pricing_calculation"
        
        elif intent in [Intent.DISCOUNT_INQUIRY, Intent.PROMOTION_INQUIRY]:
            return await self._handle_promotion_inquiry(message, user_state), "promotion_info"
        
        elif intent == Intent.CALCULATION:
            return self._handle_math_calculation(message), "math_calculation"
        
        elif intent == Intent.COMPLAINT:
            return ("I'm sorry to hear you're experiencing an issue. 😔 Your feedback is important to us. "
                   "For immediate assistance, please contact our customer service team or visit any ZUS Coffee outlet. "
                   "Is there anything specific I can help you with regarding our products or services?"), "complaint_handling"
        
        elif intent == Intent.COMPLIMENT:
            return ("Thank you so much for your kind words! 😊 We're delighted to hear you're happy with ZUS Coffee. "
                   "Your satisfaction means everything to us! Is there anything else I can help you with today?"), "compliment_response"
        
        elif intent == Intent.GENERAL_QUESTION:
            return await self._handle_general_question(message, user_state), "general_response"
        
        else:  # UNCLEAR
            return ("I'd love to help you! 😊 Could you please rephrase your question or let me know if you're looking for:\\n"
                   "• Product information or recommendations\\n"
                   "• Outlet locations and details\\n"
                   "• Price calculations\\n"
                   "• Current promotions\\n\\n"
                   "What specific information can I assist you with?"), "clarification"
    
    async def _handle_outlet_inquiry(self, message: str, user_state: SmartUserState) -> str:
        """Handle outlet-related inquiries with intelligence."""
        try:
            result = await self.api_service.call_outlets_api(message)
            
            if result["success"]:
                outlet_data = result["data"]
                
                if isinstance(outlet_data, dict) and "message" in outlet_data:
                    response = outlet_data["message"]
                    
                    # Enhance response based on user preferences
                    if user_state.preferred_location:
                        response += f"\\n\\n💡 I noticed you're interested in the {user_state.preferred_location} area. Let me know if you need specific details about any of these outlets!"
                    
                    return response
                else:
                    return "I found outlet information, but couldn't format it properly. Please try asking for a specific area like KLCC or Pavilion."
            else:
                return ("I'm having trouble accessing outlet information right now. 😅 "
                       "You can visit zuscoffee.com for store locations, or try asking me again in a moment!")
                
        except Exception as e:
            logger.error(f"Error handling outlet inquiry: {str(e)}")
            return ("I encountered an issue while searching for outlets. Please try again or visit zuscoffee.com for store locations.")
    
    async def _handle_product_inquiry(self, message: str, user_state: SmartUserState) -> str:
        """Handle product inquiries with intelligent recommendations."""
        try:
            # Enhance query based on user preferences
            enhanced_query = message
            if user_state.user_preferences.get('preferred_material'):
                enhanced_query += f" {user_state.user_preferences['preferred_material']}"
            
            result = await self.api_service.call_products_api(enhanced_query, top_k=12)
            
            if result["success"]:
                product_data = result["data"]
                
                if isinstance(product_data, dict) and "message" in product_data:
                    response = product_data["message"]
                    
                    # Add personalized recommendations
                    if user_state.user_preferences.get('preferred_material'):
                        material = user_state.user_preferences['preferred_material']
                        response += f"\\n\\n💡 I noticed you prefer {material} products. Would you like me to show you more {material} options?"
                    
                    if user_state.budget_range:
                        min_price, max_price = user_state.budget_range
                        response += f"\\n\\n💰 Considering your budget of RM {min_price:.0f}-{max_price:.0f}, I can help you find the best options!"
                    
                    return response
                else:
                    return "I found some products, but couldn't format the information properly. Please try asking for a specific type like 'tumblers' or 'ceramic mugs'."
            else:
                return ("I'm having trouble accessing our product catalog right now. 😅 "
                       "You can browse our collection at zuscoffee.com, or try asking me again in a moment!")
                
        except Exception as e:
            logger.error(f"Error handling product inquiry: {str(e)}")
            return "I encountered an issue while searching for products. Please try again or visit zuscoffee.com to browse our collection."
    
    async def _handle_product_comparison(self, message: str, user_state: SmartUserState) -> str:
        """Handle product comparison requests."""
        # For now, get general product info and let user know comparison feature
        result = await self.api_service.call_products_api(message, top_k=8)
        
        if result["success"] and isinstance(result["data"], dict) and "message" in result["data"]:
            response = result["data"]["message"]
            response += ("\\n\\n🔍 **Product Comparison Tips:**\\n"
                        "• **Material**: Stainless steel (durable, temperature retention) vs Ceramic (classic, microwave safe) vs Acrylic (lightweight, cold drinks)\\n"
                        "• **Capacity**: Small (350ml) for espresso, Medium (500ml) for regular coffee, Large (600ml+) for long drinks\\n"
                        "• **Use**: Travel tumblers for on-the-go, mugs for office/home, cold cups for iced beverages\\n\\n"
                        "Which specific products would you like me to compare in detail?")
            return response
        else:
            return ("I can help you compare our products! Please specify which products you'd like to compare. "
                   "For example: 'Compare ZUS All Day Cup vs ZUS All-Can Tumbler' or 'Stainless steel vs ceramic mugs'.")
    
    async def _handle_pricing_inquiry(self, message: str, user_state: SmartUserState) -> str:
        """Handle pricing and calculation requests."""
        try:
            # Get product data for calculations
            result = await self.api_service.call_products_api(message, top_k=15)
            
            if result["success"] and isinstance(result["data"], dict):
                products = result["data"].get("results", [])
                
                if products:
                    # Parse cart request
                    cart_data = self.calculation_engine.parse_cart_request(message, products)
                    
                    if cart_data["items"]:
                        # Calculate with breakdown
                        include_tax = any(word in message.lower() for word in ['tax', 'sst', 'total', 'final'])
                        breakdown = self.calculation_engine.calculate_with_breakdown(cart_data["items"], include_tax)
                        
                        # Format response
                        return self.calculation_engine.format_calculation_response(breakdown)
                    else:
                        # No specific products found, show general pricing info
                        response = result["data"].get("message", "Here are our products:")
                        response += ("\\n\\n💡 **For accurate calculations**, please specify products and quantities. "
                                   "For example: '2 ZUS OG Cups and 1 tumbler' or 'Calculate total for 3 ceramic mugs including tax'.")
                        return response
                else:
                    return ("I couldn't find specific products for calculation. Please mention which ZUS Coffee products "
                           "you'd like to calculate the price for (e.g., 'ZUS OG Cup', 'All-Can Tumbler', 'ceramic mug').")
            else:
                return ("I'm having trouble accessing pricing information right now. Please try again or visit "
                       "zuscoffee.com for current prices.")
                
        except Exception as e:
            logger.error(f"Error handling pricing inquiry: {str(e)}")
            return "I encountered an issue while calculating prices. Please try again with specific product names and quantities."
    
    async def _handle_promotion_inquiry(self, message: str, user_state: SmartUserState) -> str:
        """Handle promotion and discount inquiries."""
        # Get product data to check for sales
        result = await self.api_service.call_products_api("promotion sale discount", top_k=12)
        
        if result["success"] and isinstance(result["data"], dict):
            response = result["data"].get("message", "")
            
            # Add promotion context
            response += ("\\n\\n🎉 **Current Promotions:**\\n"
                        "• **Sale Items**: Look for products marked with ✨ On Sale!\\n"
                        "• **Buy 1 Free 1**: Available on selected drinkware\\n"
                        "• **Bundle Deals**: Special pricing on collection sets\\n\\n"
                        "💡 All prices shown include current discounts. Tax (6% SST) applies to final total.")
            
            return response
        else:
            return ("🎉 **Current Promotions:**\\n"
                   "We have ongoing sales on selected drinkware items! Look for 'On Sale' tags and 'Buy 1 Free 1' deals. "
                   "Visit any ZUS Coffee outlet or check zuscoffee.com for the latest promotions and bundle offers!")
    
    def _handle_math_calculation(self, message: str) -> str:
        """Handle mathematical calculations."""
        # Extract mathematical expression
        expression = re.sub(r'^(calculate|compute|solve|what\\s+is)\\s*', '', message, flags=re.IGNORECASE)
        expression = re.sub(r'[?!.]+$', '', expression).strip()
        
        result = self.calculation_engine.solve_math(expression)
        
        if "error" in result:
            return f"I couldn't solve that calculation. {result['error']} Please provide a clear mathematical expression like '2 + 3 * 4' or '15% of 200'."
        else:
            return f"🧮 **Calculation Result:**\\n**{result['expression']}** = **{result['formatted']}**"
    
    async def _handle_general_question(self, message: str, user_state: SmartUserState) -> str:
        """Handle general questions about ZUS Coffee."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hours', 'open', 'close', 'time']):
            return await self._handle_outlet_inquiry(message, user_state)
        elif any(word in message_lower for word in ['about', 'company', 'zus', 'coffee']):
            return ("ZUS Coffee is Malaysia's specialty coffee chain, known for our premium drinkware collection and quality coffee experience! ☕\\n\\n"
                   "🌟 **What makes us special:**\\n"
                   "• Premium drinkware collections (tumblers, mugs, cups)\\n"
                   "• Multiple outlet locations across Malaysia\\n"
                   "• Quality coffee and beverages\\n"
                   "• Special promotions and bundle deals\\n\\n"
                   "I can help you find outlets, explore our drinkware, calculate prices, and answer questions about our products!")
        elif any(word in message_lower for word in ['help', 'what', 'can', 'do']):
            return ("I'm here to help with all things ZUS Coffee! 😊\\n\\n"
                   "🎯 **I can assist you with:**\\n"
                   "• **Find Outlets** - Locations, hours, contact info\\n"
                   "• **Explore Products** - Drinkware collection, features, prices\\n"
                   "• **Calculate Prices** - Order totals with tax included\\n"
                   "• **Recommendations** - Help you choose the perfect drinkware\\n"
                   "• **Promotions** - Current deals and special offers\\n"
                   "• **General Info** - About ZUS Coffee and our services\\n\\n"
                   "Just ask me anything! For example: 'Find outlets near KLCC' or 'Show me stainless steel tumblers'.")
        else:
            return ("I'd be happy to help! 😊 I specialize in ZUS Coffee information including outlets, products, pricing, and promotions. "
                   "Could you please let me know what specific information you're looking for?")

# Global chatbot instance
chatbot = AdvancedZUSChatbot()

def get_chatbot() -> AdvancedZUSChatbot:
    """Get the global chatbot instance."""
    return chatbot

# For backwards compatibility
AgenticChatbot = AdvancedZUSChatbot
