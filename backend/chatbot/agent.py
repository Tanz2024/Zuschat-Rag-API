#!/usr/bin/env python3
"""
Advanced Intelligent Chatbot Agent for ZUS Coffee
This module implements a sophisticated conversational AI that can:

- Advanced natural language understanding with context awareness
- Smart product recommendations and comparisons
- Complex calculations (pricing, tax, discounts, bulk orders)
- Intelligent outlet recommendations based on location and preferences
- Multi-turn conversations with memory
- Smart fallback and error handling
- Real-time data analysis and insights
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
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Intent(str, Enum):
    """Advanced user intent classification."""
    GREETING = "greeting"
    FAREWELL = "farewell"
    OUTLET_INQUIRY = "outlet_inquiry"
    OUTLET_DIRECTIONS = "outlet_directions"
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
    AVAILABILITY_CHECK = "availability_check"
    GENERAL_QUESTION = "general_question"
    COMPLAINT = "complaint"
    COMPLIMENT = "compliment"
    UNCLEAR = "unclear"

@dataclass
class ProductItem:
    """Represents a product in user's cart or query."""
    name: str
    price: float
    quantity: int = 1
    discount_percent: float = 0.0
    on_sale: bool = False
    category: str = ""
    
    @property
    def subtotal(self) -> float:
        """Calculate subtotal with discount."""
        base_total = self.price * self.quantity
        if self.discount_percent > 0:
            base_total *= (1 - self.discount_percent / 100)
        return base_total

@dataclass 
class CartCalculation:
    """Represents a shopping cart calculation."""
    items: List[ProductItem] = field(default_factory=list)
    subtotal: float = 0.0
    tax_rate: float = 0.06  # 6% SST for Malaysia
    delivery_fee: float = 0.0
    discount_code: str = ""
    discount_amount: float = 0.0
    
    @property
    def total_before_tax(self) -> float:
        """Calculate total before tax."""
        return sum(item.subtotal for item in self.items) - self.discount_amount
    
    @property
    def tax_amount(self) -> float:
        """Calculate tax amount."""
        return self.total_before_tax * self.tax_rate
    
    @property
    def final_total(self) -> float:
        """Calculate final total including tax and delivery."""
        return self.total_before_tax + self.tax_amount + self.delivery_fee

class AdvancedUserState:
    """Enhanced user conversation state with intelligence."""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.conversation_history: List[Dict[str, Any]] = []
        self.mentioned_outlets: List[str] = []
        self.mentioned_products: List[str] = []
        self.preferred_location: Optional[str] = None
        self.budget_range: Optional[Tuple[float, float]] = None
        self.current_cart: CartCalculation = CartCalculation()
        self.last_intent: Optional[Intent] = None
        self.context: Dict[str, Any] = {}
        self.user_preferences: Dict[str, Any] = {
            "preferred_material": None,  # stainless steel, ceramic, acrylic
            "preferred_capacity": None,  # small, medium, large
            "color_preference": None,
            "price_sensitivity": "medium"  # low, medium, high
        }
        self.conversation_sentiment: str = "neutral"  # positive, neutral, negative
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.interaction_count = 0
    
    def add_message(self, role: str, content: str, intent: Intent = None, metadata: Dict = None):
        """Add a message to conversation history with enhanced tracking."""
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
        
        # Update context based on message content
        self._update_context_from_message(content, intent)
    
    def _update_context_from_message(self, content: str, intent: Intent = None):
        """Extract and update context from user message."""
        content_lower = content.lower()
        
        # Extract location preferences
        location_keywords = {
            'klcc': 'KLCC area',
            'pavilion': 'Pavilion KL area', 
            'mid valley': 'Mid Valley area',
            'sunway': 'Sunway area',
            'one utama': 'One Utama area',
            'bangsar': 'Bangsar area',
            'damansara': 'Damansara area',
            'pj': 'Petaling Jaya',
            'shah alam': 'Shah Alam',
            'subang': 'Subang area'
        }
        
        for keyword, location in location_keywords.items():
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
    
    def get_conversation_summary(self) -> str:
        """Generate intelligent conversation summary."""
        if not self.conversation_history:
            return "New conversation started."
        
        recent_messages = self.conversation_history[-3:]
        intents = [msg.get('intent') for msg in recent_messages if msg.get('intent')]
        
        summary_parts = []
        
        if self.preferred_location:
            summary_parts.append(f"User interested in {self.preferred_location}")
        
        if self.budget_range:
            summary_parts.append(f"Budget range: RM {self.budget_range[0]:.2f} - RM {self.budget_range[1]:.2f}")
        
        if self.user_preferences['preferred_material']:
            summary_parts.append(f"Prefers {self.user_preferences['preferred_material']} products")
        
        if len(self.current_cart.items) > 0:
            summary_parts.append(f"Has {len(self.current_cart.items)} items in consideration")
        
        recent_intent_summary = f"Recent focus: {', '.join(set(intents)) if intents else 'general inquiry'}"
        summary_parts.append(recent_intent_summary)
        
        return "; ".join(summary_parts) if summary_parts else "General conversation in progress."

class AdvancedIntentDetector:
    """Advanced intent detection with context awareness and confidence scoring."""
    
    def __init__(self):
        self.intent_patterns = {
            Intent.GREETING: [
                r'\b(hi|hello|hey|good\s+(morning|afternoon|evening)|greetings|hola|sup)\b',
                r'\bhow\s+are\s+you\b',
                r'\bwhat\'?s\s+up\b',
                r'\b(start|begin|new)\s+(conversation|chat)\b'
            ],
            Intent.FAREWELL: [
                r'\b(bye|goodbye|see\s+you|farewell|thanks\s+bye|talk\s+later)\b',
                r'\b(that\'?s\s+all|i\'?m\s+done|finished|complete)\b'
            ],
            Intent.OUTLET_INQUIRY: [
                r'\b(outlet|store|shop|location|branch|address|find\s+store)\b',
                r'\b(where|find|show)\s+.*\b(outlet|store|shop|location)\b',
                r'\bhow\s+many\s+.*\b(outlet|store|location)\b',
                r'\b(nearest|closest)\s+.*\b(outlet|store|location)\b',
                r'\bfind\s+outlets?\b',
                r'\b(klcc|pavilion|pj|mall|shopping|damansara|bangsar)\b',
                r'\boutlets?\s+in\s+\w+\b',
                r'\bstore\s+locations?\b'
            ],
            Intent.OUTLET_DIRECTIONS: [
                r'\b(direction|how\s+to\s+get|navigate|route|way\s+to)\b.*\b(outlet|store)\b',
                r'\b(driving|walking|public\s+transport)\s+to\b',
                r'\bshow\s+me\s+the\s+way\b'
            ],
            Intent.OUTLET_HOURS: [
                r'\b(opening|hours|time|when)\s+.*\b(open|close|operating)\b',
                r'\bwhat\s+time.*\b(open|close)\b',
                r'\b(business|operating)\s+hours\b',
                r'\bis\s+.*\s+open\b'
            ],
            Intent.OUTLET_CONTACT: [
                r'\b(phone|contact|call|number|email|reach)\b.*\b(outlet|store)\b',
                r'\bhow\s+to\s+contact\b',
                r'\bphone\s+number\b'
            ],
            Intent.PRODUCT_INQUIRY: [
                r'\b(product|drinkware|tumbler|mug|cup|bottle|flask|item)\b',
                r'\b(show|find|search|look\s+for)\s+.*\b(product|drinkware|tumbler|mug|cup)\b',
                r'\b(what|which)\s+.*\b(products|items|drinkware|cups|mugs|tumblers)\b',
                r'\bshow\s+me\s+(products?|drinkware|tumblers?|mugs?|cups?)\b',
                r'\b(ceramic|stainless\s+steel|acrylic)\s+(mug|cup|tumbler)\b',
                r'\b(collection|series|range)\b.*\b(product|drinkware)\b'
            ],
            Intent.PRODUCT_COMPARISON: [
                r'\b(compare|comparison|vs|versus|difference|better)\b.*\b(product|tumbler|mug|cup)\b',
                r'\bwhich\s+is\s+better\b',
                r'\b(pros\s+and\s+cons|advantages|disadvantages)\b',
                r'\bwhat\'?s\s+the\s+difference\b'
            ],
            Intent.PRODUCT_RECOMMENDATION: [
                r'\b(recommend|suggest|best|top|popular|favorite)\b.*\b(product|drinkware|tumbler|mug|cup)\b',
                r'\bwhat\s+do\s+you\s+recommend\b',
                r'\bbest\s+seller\b',
                r'\bmost\s+popular\b',
                r'\bi\s+need\s+.*\b(recommendation|suggestion)\b'
            ],
            Intent.PRICE_INQUIRY: [
                r'\b(price|cost|how\s+much|expensive|cheap|affordable)\b',
                r'\brm\s*\d+',
                r'\b(budget|under|below|above)\s+.*\s+rm\b',
                r'\bprice\s+(range|list)\b'
            ],
            Intent.CALCULATION: [
                r'\b(calculate|compute|solve|math|total)\b(?!\s+price)(?!\s+cost)',
                r'\d+\s*[+\-*/^%]\s*\d+',
                r'\b(add|subtract|multiply|divide|plus|minus|times)\s+\d+',
                r'\b(percentage|percent|%)\b.*\b(calculation|compute)\b',
                r'\b(square\s+root|sqrt|sin|cos|tan|log)\b',
                r'^calculate\s+\d+',
                r'\bmath\s+(problem|question|help)\b'
            ],
            Intent.CART_CALCULATION: [
                r'\b(cart|order|total|checkout|purchase)\s+.*\b(price|cost|total)\b',
                r'\bcalculate\s+.*\b(price|cost|total|order)\b',
                r'\bhow\s+much\s+.*\b(total|altogether|combined)\b',
                r'\b(subtotal|grand\s+total|final\s+total)\b',
                r'\bprice\s+for\s+\d+\b',
                r'\btotal\s+cost\s+of\b'
            ],
            Intent.TAX_CALCULATION: [
                r'\b(tax|sst|gst|including\s+tax|with\s+tax|after\s+tax)\b',
                r'\b6%\s*(tax|sst)\b',
                r'\btax\s+(calculation|included|amount)\b'
            ],
            Intent.DISCOUNT_INQUIRY: [
                r'\b(discount|sale|offer|promotion|deal|cheaper)\b',
                r'\bon\s+sale\b',
                r'\bspecial\s+(price|offer)\b',
                r'\bany\s+(discount|deal|promotion)\b'
            ],
            Intent.PROMOTION_INQUIRY: [
                r'\b(promotion|promo|offer|deal|special)\b',
                r'\bbuy\s+\d+\s+free\s+\d+\b',
                r'\bcurrent\s+(promotion|offer|deal)\b',
                r'\bwhat\'?s\s+on\s+(offer|sale|promotion)\b'
            ],
            Intent.AVAILABILITY_CHECK: [
                r'\b(available|in\s+stock|have|carry|sell)\b.*\b(product|item|tumbler|mug|cup)\b',
                r'\bdo\s+you\s+(have|carry|sell)\b',
                r'\bis\s+.*\s+available\b',
                r'\bin\s+stock\b'
            ],
            Intent.GENERAL_QUESTION: [
                r'\b(help|information|about|tell\s+me|explain|what\s+is)\b',
                r'\bcan\s+you\s+help\b',
                r'\bi\s+want\s+to\s+know\b',
                r'\bwhat\s+(can|do)\s+you\b'
            ],
            Intent.COMPLAINT: [
                r'\b(problem|issue|complaint|wrong|error|bad|terrible|awful)\b',
                r'\bnot\s+(working|good|happy|satisfied)\b',
                r'\bi\s+have\s+a\s+problem\b',
                r'\bthis\s+is\s+(wrong|bad|terrible)\b'
            ],
            Intent.COMPLIMENT: [
                r'\b(great|excellent|amazing|wonderful|fantastic|love|perfect)\b',
                r'\bthank\s+you\b',
                r'\bgreat\s+(job|work|service)\b',
                r'\bi\s+(love|like)\s+this\b'
            ]
        }
        
        # Context-aware modifiers
        self.context_modifiers = {
            Intent.OUTLET_INQUIRY: ["location", "address", "store", "shop"],
            Intent.PRODUCT_INQUIRY: ["drinkware", "product", "item", "buy"],
            Intent.CALCULATION: ["calculate", "math", "compute", "total"],
            Intent.PRICE_INQUIRY: ["price", "cost", "rm", "money", "expensive"]
        }
    
    def detect_intent(self, text: str, user_state: AdvancedUserState) -> Tuple[Intent, float]:
        """Detect intent with advanced context awareness and confidence scoring."""
        text_lower = text.lower().strip()
        scores = {}
        
        # Base pattern matching
        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            matches = 0
            total_patterns = len(patterns)
            
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    matches += 1
                    # Weight matches by pattern specificity
                    pattern_weight = 1.0 / math.sqrt(len(pattern)) if len(pattern) > 10 else 1.0
                    score += pattern_weight
            
            if matches > 0:
                # Normalize score by number of patterns
                base_score = score / total_patterns if total_patterns > 0 else 0.0
                # Boost for having any matches at all
                scores[intent] = base_score + 0.2 * min(matches / total_patterns, 1.0)
            else:
                scores[intent] = 0.0
        
        # Context-based boosting
        if user_state.last_intent:
            # Conversation flow logic
            context_boost = self._get_context_boost(text_lower, user_state.last_intent, user_state)
            for intent, boost in context_boost.items():
                if intent in scores:
                    scores[intent] += boost
        
        # User preference boosting
        preference_boost = self._get_preference_boost(text_lower, user_state)
        for intent, boost in preference_boost.items():
            if intent in scores:
                scores[intent] += boost
        
        # Number and calculation detection
        if re.search(r'\d+', text_lower):
            if any(word in text_lower for word in ['total', 'cost', 'price', 'rm']):
                scores[Intent.CART_CALCULATION] = scores.get(Intent.CART_CALCULATION, 0) + 0.4
            elif any(word in text_lower for word in ['calculate', 'math', '+', '-', '*', '/']):
                scores[Intent.CALCULATION] = scores.get(Intent.CALCULATION, 0) + 0.3
        
        # Find best intent
        if not scores or max(scores.values()) == 0:
            return Intent.UNCLEAR, 0.1
        
        best_intent = max(scores, key=scores.get)
        confidence = min(scores[best_intent], 1.0)  # Cap at 1.0
        
        # Apply minimum confidence threshold
        if confidence < 0.2:
            return Intent.UNCLEAR, confidence
        
        logger.info(f"Intent detected: {best_intent.value} (confidence: {confidence:.2f})")
        return best_intent, confidence
    
    def _get_context_boost(self, text: str, last_intent: Intent, user_state: AdvancedUserState) -> Dict[Intent, float]:
        """Get context-based intent boosting."""
        boosts = {}
        
        # Follow-up conversation patterns
        if last_intent == Intent.OUTLET_INQUIRY:
            if any(word in text for word in ['hours', 'time', 'open', 'close']):
                boosts[Intent.OUTLET_HOURS] = 0.3
            elif any(word in text for word in ['phone', 'contact', 'call']):
                boosts[Intent.OUTLET_CONTACT] = 0.3
            elif any(word in text for word in ['direction', 'how to get', 'way']):
                boosts[Intent.OUTLET_DIRECTIONS] = 0.3
        
        elif last_intent == Intent.PRODUCT_INQUIRY:
            if any(word in text for word in ['price', 'cost', 'much']):
                boosts[Intent.PRICE_INQUIRY] = 0.3
            elif any(word in text for word in ['compare', 'vs', 'difference']):
                boosts[Intent.PRODUCT_COMPARISON] = 0.3
            elif any(word in text for word in ['more', 'details', 'info']):
                boosts[Intent.PRODUCT_INQUIRY] = 0.2
        
        elif last_intent in [Intent.PRICE_INQUIRY, Intent.PRODUCT_INQUIRY]:
            if any(word in text for word in ['calculate', 'total', 'how much']):
                boosts[Intent.CART_CALCULATION] = 0.4
        
        return boosts
    
    def _get_preference_boost(self, text: str, user_state: AdvancedUserState) -> Dict[Intent, float]:
        """Get user preference-based intent boosting."""
        boosts = {}
        
        # Boost based on conversation history
        if user_state.interaction_count > 3:
            # User is engaged, boost specific intents
            if user_state.preferred_location:
                boosts[Intent.OUTLET_INQUIRY] = 0.1
            
            if user_state.user_preferences.get('preferred_material'):
                boosts[Intent.PRODUCT_INQUIRY] = 0.1
        
        # Boost based on mentioned items
        if len(user_state.mentioned_products) > 0:
            boosts[Intent.PRODUCT_INQUIRY] = 0.15
            boosts[Intent.CART_CALCULATION] = 0.1
        
        if user_state.budget_range:
            boosts[Intent.PRICE_INQUIRY] = 0.1
            boosts[Intent.CART_CALCULATION] = 0.1
        
        return boosts

class SmartCalculationEngine:
    """Advanced calculation engine for prices, taxes, and complex math."""
    
    def __init__(self):
        self.tax_rate = 0.06  # 6% SST for Malaysia
        self.delivery_rates = {
            "standard": 0.0,  # Free for most areas
            "express": 5.0,   # Express delivery
            "remote": 8.0     # Remote areas
        }
    
    def parse_cart_request(self, text: str, available_products: List[Dict]) -> CartCalculation:
        """Parse natural language cart request."""
        cart = CartCalculation()
        text_lower = text.lower()
        
        # Extract product names and quantities
        for product in available_products:
            product_name = product.get('name', '').lower()
            product_keywords = product_name.split()
            
            # Check if product is mentioned
            product_mentioned = False
            for keyword in product_keywords:
                if len(keyword) > 3 and keyword in text_lower:
                    product_mentioned = True
                    break
            
            if product_mentioned:
                # Extract quantity
                quantity = self._extract_quantity_for_product(text_lower, product_name)
                if quantity > 0:
                    # Extract pricing info
                    price = float(product.get('sale_price', 0) or product.get('price', '0').replace('RM ', ''))
                    discount = 0.0
                    
                    if product.get('on_sale') or 'sale' in product.get('promotion', '').lower():
                        regular_price = product.get('regular_price')
                        if regular_price:
                            regular = float(regular_price.replace('RM ', ''))
                            discount = ((regular - price) / regular) * 100 if regular > price else 0.0
                    
                    cart_item = ProductItem(
                        name=product.get('name', ''),
                        price=price,
                        quantity=quantity,
                        discount_percent=discount,
                        on_sale=product.get('on_sale', False),
                        category=product.get('category', '')
                    )
                    cart.items.append(cart_item)
        
        return cart
    
    def _extract_quantity_for_product(self, text: str, product_name: str) -> int:
        """Extract quantity for a specific product."""
        # Look for quantity patterns near product name
        quantity_patterns = [
            r'(\d+)\s*(?:x\s*)?(?:' + re.escape(product_name[:10]) + ')',
            r'(\d+)\s+(?:of\s+)?(?:' + re.escape(product_name[:10]) + ')',
            r'(\d+)\s+' + re.escape(product_name.split()[0])
        ]
        
        for pattern in quantity_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        # Default to 1 if product is mentioned but no quantity specified
        return 1
    
    def calculate_total_with_breakdown(self, cart: CartCalculation, include_tax: bool = True, 
                                     delivery_type: str = "standard") -> Dict[str, Any]:
        """Calculate total with detailed breakdown."""
        breakdown = {
            "items": [],
            "subtotal": 0.0,
            "total_discount": 0.0,
            "delivery_fee": self.delivery_rates.get(delivery_type, 0.0),
            "tax_rate": self.tax_rate if include_tax else 0.0,
            "tax_amount": 0.0,
            "final_total": 0.0,
            "savings": 0.0
        }
        
        # Calculate item details
        for item in cart.items:
            item_total = item.price * item.quantity
            item_discount = (item_total * item.discount_percent / 100) if item.discount_percent > 0 else 0.0
            item_final = item_total - item_discount
            
            breakdown["items"].append({
                "name": item.name,
                "price": item.price,
                "quantity": item.quantity,
                "subtotal": item_total,
                "discount": item_discount,
                "final_price": item_final,
                "on_sale": item.on_sale
            })
            
            breakdown["subtotal"] += item_final
            breakdown["total_discount"] += item_discount
            breakdown["savings"] += item_discount
        
        # Calculate tax
        if include_tax:
            breakdown["tax_amount"] = breakdown["subtotal"] * self.tax_rate
        
        # Calculate final total
        breakdown["final_total"] = breakdown["subtotal"] + breakdown["tax_amount"] + breakdown["delivery_fee"]
        
        return breakdown
    
    def format_calculation_response(self, breakdown: Dict[str, Any]) -> str:
        """Format calculation results into user-friendly response."""
        response_parts = ["🧮 **Cart Calculation Breakdown:**\n"]
        
        # Items details
        for i, item in enumerate(breakdown["items"], 1):
            response_parts.append(f"**{i}. {item['name']}**")
            response_parts.append(f"   • Price: RM {item['price']:.2f} x {item['quantity']}")
            
            if item['discount'] > 0:
                response_parts.append(f"   • Discount: -RM {item['discount']:.2f} ({'Sale Price!' if item['on_sale'] else 'Discount Applied'})")
                response_parts.append(f"   • Item Total: ~~RM {item['subtotal']:.2f}~~ → **RM {item['final_price']:.2f}**")
            else:
                response_parts.append(f"   • Item Total: **RM {item['final_price']:.2f}**")
            response_parts.append("")
        
        # Summary
        response_parts.append("📊 **Order Summary:**")
        response_parts.append(f"• Subtotal: RM {breakdown['subtotal']:.2f}")
        
        if breakdown['total_discount'] > 0:
            response_parts.append(f"• Total Savings: -RM {breakdown['total_discount']:.2f} 🎉")
        
        if breakdown['delivery_fee'] > 0:
            response_parts.append(f"• Delivery Fee: RM {breakdown['delivery_fee']:.2f}")
        
        if breakdown['tax_amount'] > 0:
            response_parts.append(f"• Tax (6% SST): RM {breakdown['tax_amount']:.2f}")
        
        response_parts.append(f"• **Final Total: RM {breakdown['final_total']:.2f}**")
        
        if breakdown['savings'] > 0:
            response_parts.append(f"\n💰 You saved **RM {breakdown['savings']:.2f}** with current promotions!")
        
        return "\n".join(response_parts)
    
    def solve_math_expression(self, expression: str) -> Dict[str, Any]:
        """Safely solve mathematical expressions."""
        try:
            # Clean the expression
            clean_expr = re.sub(r'[^0-9+\-*/().\s]', '', expression)
            
            # Basic safety check
            if not clean_expr or 'import' in expression or 'exec' in expression:
                return {"error": "Invalid expression", "result": None}
            
            # Evaluate safely
            result = eval(clean_expr)
            
            return {
                "expression": clean_expr,
                "result": result,
                "formatted_result": f"{result:.6f}".rstrip('0').rstrip('.') if isinstance(result, float) else str(result)
            }
        
        except Exception as e:
            return {"error": f"Calculation error: {str(e)}", "result": None}
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
            params = {"query": query, "top_k": 15}
            
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

class EnhancedAPIService:
    """Enhanced API service with intelligent data handling and caching."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.timeout = 15  # Increased timeout for complex queries
        self.cache = {}  # Simple in-memory cache
        self.cache_expiry = timedelta(minutes=5)
    
    async def call_outlets_api(self, query: str, user_state: AdvancedUserState = None) -> Dict[str, Any]:
        """Call outlets API with enhanced context awareness."""
        try:
            # Build enhanced query based on user context
            enhanced_query = self._enhance_outlet_query(query, user_state)
            
            url = f"{self.base_url}/outlets"
            params = {"query": enhanced_query}
            
            # Check cache first
            cache_key = f"outlets_{hash(enhanced_query)}"
            if self._is_cache_valid(cache_key):
                logger.info(f"Returning cached outlets result for: {enhanced_query}")
                return self.cache[cache_key]["data"]
            
            logger.info(f"Calling outlets API: {url} with enhanced query: {enhanced_query}")
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                result = {
                    "success": True,
                    "data": response.json(),
                    "source": "outlets_api",
                    "query_used": enhanced_query
                }
                
                # Cache the result
                self.cache[cache_key] = {
                    "data": result,
                    "timestamp": datetime.now()
                }
                
                return result
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
        except Exception as e:
            logger.error(f"Outlets API unexpected error: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "fallback": True
            }
    
    async def call_products_api(self, query: str, user_state: AdvancedUserState = None, top_k: int = 12) -> Dict[str, Any]:
        """Call products API with intelligent filtering and recommendations."""
        try:
            # Build enhanced query based on user preferences
            enhanced_query = self._enhance_product_query(query, user_state)
            
            url = f"{self.base_url}/products"
            params = {"query": enhanced_query, "top_k": top_k}
            
            # Check cache first
            cache_key = f"products_{hash(enhanced_query)}_{top_k}"
            if self._is_cache_valid(cache_key):
                logger.info(f"Returning cached products result for: {enhanced_query}")
                return self.cache[cache_key]["data"]
            
            logger.info(f"Calling products API: {url} with enhanced query: {enhanced_query}, top_k: {top_k}")
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                result = {
                    "success": True,
                    "data": response.json(),
                    "source": "products_api",
                    "query_used": enhanced_query
                }
                
                # Apply intelligent filtering based on user preferences
                if user_state:
                    result["data"] = self._filter_products_by_preferences(result["data"], user_state)
                
                # Cache the result
                self.cache[cache_key] = {
                    "data": result,
                    "timestamp": datetime.now()
                }
                
                return result
            else:
                logger.warning(f"Products API returned status {response.status_code}: {response.text}")
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}",
                    "fallback": True
                }
                
        except Exception as e:
            logger.error(f"Products API error: {str(e)}")
            return {
                "success": False,
                "error": f"Products API error: {str(e)}",
                "fallback": True
            }
    
    def _enhance_outlet_query(self, query: str, user_state: AdvancedUserState) -> str:
        """Enhance outlet query with user context."""
        enhanced = query
        
        if user_state and user_state.preferred_location:
            # Add location context if not already in query
            location_terms = user_state.preferred_location.lower()
            if not any(term in query.lower() for term in location_terms.split()):
                enhanced = f"{query} near {user_state.preferred_location}"
        
        return enhanced
    
    def _enhance_product_query(self, query: str, user_state: AdvancedUserState) -> str:
        """Enhance product query with user preferences."""
        enhanced = query
        
        if user_state:
            # Add material preference
            if user_state.user_preferences.get('preferred_material'):
                material = user_state.user_preferences['preferred_material']
                if material.lower() not in query.lower():
                    enhanced = f"{enhanced} {material}"
            
            # Add capacity preference
            if user_state.user_preferences.get('preferred_capacity'):
                capacity = user_state.user_preferences['preferred_capacity']
                if capacity.lower() not in query.lower():
                    enhanced = f"{enhanced} {capacity}"
            
            # Add budget consideration
            if user_state.budget_range:
                min_price, max_price = user_state.budget_range
                enhanced = f"{enhanced} price range RM{min_price:.0f} to RM{max_price:.0f}"
        
        return enhanced
    
    def _filter_products_by_preferences(self, products: Dict, user_state: AdvancedUserState) -> Dict:
        """Filter and rank products based on user preferences."""
        if not isinstance(products, dict) or 'results' not in products:
            return products
        
        results = products.get('results', [])
        if not results or not user_state:
            return products
        
        # Score products based on user preferences
        scored_products = []
        for product in results:
            score = 0.0
            
            # Material preference scoring
            material_pref = user_state.user_preferences.get('preferred_material')
            if material_pref:
                product_material = product.get('material', '').lower()
                if material_pref.lower() in product_material:
                    score += 2.0
            
            # Capacity preference scoring
            capacity_pref = user_state.user_preferences.get('preferred_capacity')
            if capacity_pref:
                capacity = product.get('capacity', '').lower()
                if capacity_pref == 'large' and any(term in capacity for term in ['600ml', '650ml', '20oz', '22oz']):
                    score += 1.5
                elif capacity_pref == 'medium' and any(term in capacity for term in ['500ml', '16oz', '17oz']):
                    score += 1.5
                elif capacity_pref == 'small' and any(term in capacity for term in ['350ml', '12oz', '14oz']):
                    score += 1.5
            
            # Budget scoring
            if user_state.budget_range:
                product_price = float(product.get('sale_price', 0) or 
                                    product.get('price', '0').replace('RM ', '').replace(',', ''))
                min_price, max_price = user_state.budget_range
                if min_price <= product_price <= max_price:
                    score += 1.0
            
            # Sale/promotion scoring
            if product.get('on_sale') or product.get('promotion'):
                score += 0.5
            
            scored_products.append((product, score))
        
        # Sort by score (descending) and return
        scored_products.sort(key=lambda x: x[1], reverse=True)
        products['results'] = [product for product, score in scored_products]
        
        return products
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid."""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]["timestamp"]
        return datetime.now() - cache_time < self.cache_expiry

class AdvancedAgenticChatbot:
    """
    Advanced Intelligent Chatbot Controller - Production Ready
    This orchestrates everything with sophisticated intelligence, context awareness, and natural conversation flow.
    """
    
    def __init__(self):
        self.intent_detector = AdvancedIntentDetector()
        self.api_service = EnhancedAPIService()
        self.calculation_engine = SmartCalculationEngine()
        self.user_sessions: Dict[str, AdvancedUserState] = {}
    
    def get_or_create_session(self, session_id: str = None) -> AdvancedUserState:
        """Get or create advanced user session."""
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        if session_id not in self.user_sessions:
            self.user_sessions[session_id] = AdvancedUserState(session_id)
        
        return self.user_sessions[session_id]
    
    async def process_message(self, message: str, session_id: str = None) -> Dict[str, Any]:
        """
        Advanced message processing with full intelligence and context awareness.
        This is the main entry point that handles all user interactions.
        """
        try:
            # Get or create user session with advanced state
            user_state = self.get_or_create_session(session_id)
            
            # Add user message to conversation history
            user_state.add_message("user", message)
            
            logger.info(f"Processing message for session {user_state.session_id}: '{message[:100]}...'")
            logger.info(f"Session context: {user_state.get_conversation_summary()}")
            
            # Advanced intent detection with context
            intent, confidence = self.intent_detector.detect_intent(message, user_state)
            
            logger.info(f"Detected intent: {intent.value} (confidence: {confidence:.2f})")
            
            # Check for missing information with intelligent prompting
            missing_info_prompt = self.check_missing_info(intent, message, user_state)
            if missing_info_prompt:
                response = missing_info_prompt
                response_type = "clarification"
            else:
                # Generate intelligent response
                response, response_type = await self._generate_intelligent_response(intent, message, user_state, confidence)
            
            # Add assistant response to conversation history
            user_state.add_message("assistant", response, intent, {
                "confidence": confidence,
                "response_type": response_type
            })
            
            return {
                "response": response,
                "intent": intent.value,
                "confidence": confidence,
                "session_id": user_state.session_id,
                "response_type": response_type,
                "conversation_context": user_state.get_conversation_summary()
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return self._handle_error_response(str(e), session_id)
    
    async def _generate_intelligent_response(self, intent: Intent, message: str, user_state: AdvancedUserState, 
                                           confidence: float) -> Tuple[str, str]:
        """Generate sophisticated, context-aware responses."""
        
        try:
            if intent == Intent.GREETING:
                return self._handle_greeting(user_state), "greeting"
            
            elif intent == Intent.FAREWELL:
                return self._handle_farewell(user_state), "farewell"
            
            elif intent in [Intent.OUTLET_INQUIRY, Intent.OUTLET_DIRECTIONS, Intent.OUTLET_HOURS, Intent.OUTLET_CONTACT]:
                return await self._handle_smart_outlet_inquiry(message, user_state, intent), "outlet_info"
            
            elif intent in [Intent.PRODUCT_INQUIRY, Intent.PRODUCT_RECOMMENDATION, Intent.AVAILABILITY_CHECK]:
                return await self._handle_smart_product_inquiry(message, user_state, intent), "product_info"
            
            elif intent == Intent.PRODUCT_COMPARISON:
                return await self._handle_product_comparison(message, user_state), "product_comparison"
            
            elif intent in [Intent.PRICE_INQUIRY, Intent.CART_CALCULATION, Intent.TAX_CALCULATION]:
                return await self._handle_smart_pricing(message, user_state, intent), "pricing_calculation"
            
            elif intent in [Intent.DISCOUNT_INQUIRY, Intent.PROMOTION_INQUIRY]:
                return await self._handle_promotion_inquiry(message, user_state), "promotion_info"
            
            elif intent == Intent.CALCULATION:
                return self._handle_advanced_math(message, user_state), "math_calculation"
            
            elif intent == Intent.COMPLAINT:
                return self._handle_complaint(user_state), "complaint_handling"
            
            elif intent == Intent.COMPLIMENT:
                return self._handle_compliment(user_state), "compliment_response"
            
            elif intent == Intent.GENERAL_QUESTION:
                return await self._handle_general_question(message, user_state), "general_response"
            
            else:  # Intent.UNCLEAR
                return self._handle_unclear_intent(message, user_state, confidence), "clarification"
                
        except Exception as e:
            logger.error(f"Error generating response for intent {intent}: {str(e)}")
            return self._get_fallback_response(intent, str(e)), "error_fallback"
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


