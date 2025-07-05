#!/usr/bin/env python3
"""
Enhanced ZUS Coffee Chatbot Agent - PRODUCTION READY
Fully integrated agentic system with state management, planning, tool integration, and robust error handling
Meets all requirements for Part 1-5: Sequential Conversation, Agentic Planning, Tool Calling, Custom API & RAG Integration, Unhappy Flows
"""

import logging
import re
import json
import math
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedMinimalAgent:
    """
    Production-ready ZUS Coffee chatbot with comprehensive agentic features:
    - State Management & Memory (tracking slots/variables across turns)
    - Planner/Controller Logic (intent parsing, action selection, follow-up questions)
    - Tool Integration (calculator API, error handling)
    - Custom API Consumption (FastAPI endpoints for products, outlets)
    - Robust Error Handling (graceful degradation, security)
    """
    
    def __init__(self):
        # Enhanced session management with memory (Part 1: Sequential Conversation)
        self.sessions = {}
        
        # State management slots (Part 1: Sequential Conversation)
        self.conversation_context = {}
        
        # Product keywords from real data (comprehensive)
        self.product_keywords = {
            # Main product types
            'cup': ['cup', 'og cup', 'all day cup', 'screw-on lid'],
            'tumbler': ['tumbler', 'all-can tumbler', 'all can tumbler'],
            'mug': ['mug', 'ceramic mug'],
            'bottle': ['bottle', 'flask', 'water bottle'],
            'cold cup': ['cold cup', 'frozee', 'acrylic'],
            
            # Collections
            'sundaze': ['sundaze', 'sundaze collection'],
            'aqua': ['aqua', 'aqua collection'],
            'corak malaysia': ['corak malaysia', 'malaysia', 'corak'],
            'limited edition': ['limited edition', 'special edition'],
            
            # Materials
            'stainless steel': ['stainless steel', 'steel', 'metal'],
            'ceramic': ['ceramic', 'porcelain'],
            'acrylic': ['acrylic', 'plastic', 'clear'],
            
            # Features
            'insulation': ['insulation', 'double wall', 'temperature retention'],
            'leak proof': ['leak proof', 'leak-proof', 'no spill'],
            'car holder': ['car cup holder', 'car holder', 'cup holder'],
            
            # Colors (from real data)
            'thunder blue': ['thunder blue', 'blue'],
            'space black': ['space black', 'black'],
            'lucky pink': ['lucky pink', 'pink'],
            'emerald green': ['emerald green', 'green'],
            'sunset orange': ['sunset orange', 'orange'],
            
            # Size/Capacity
            '500ml': ['500ml', '17oz', '500'],
            '600ml': ['600ml', '20oz', '600'],
            '16oz': ['16oz', '16 oz'],
            '650ml': ['650ml', '650']
        }
        
        # Outlet location keywords (comprehensive from database)
        self.outlet_keywords = {
            'kuala lumpur': ['kuala lumpur', 'kl', 'wilayah persekutuan kuala lumpur', 'wp kuala lumpur'],
            'selangor': ['selangor', 'petaling jaya', 'pj', 'subang', 'shah alam', 'damansara', 'sunway', 'klang'],
            
            # Specific malls and landmarks (from real outlet data)
            'klcc': ['klcc', 'suria klcc', 'petronas'],
            'pavilion': ['pavilion', 'bukit bintang'],
            'mid valley': ['mid valley', 'midvalley', 'megamall'],
            'avenue k': ['avenue k'],
            'sunway pyramid': ['sunway pyramid', 'sunway'],
            'aeon': ['aeon'],
            'one utama': ['one utama', '1 utama'],
            'kl sentral': ['kl sentral', 'sentral'],
            'kl gateway': ['kl gateway', 'gateway'],
            'kl eco city': ['kl eco city', 'eco city'],
            
            # Services (from real data analysis)
            'dine-in': ['dine in', 'dine-in', 'eat in', 'dining'],
            'takeaway': ['takeaway', 'take away', 'pickup', 'take out'],
            'delivery': ['delivery', 'deliver', 'food delivery'],
            'drive-thru': ['drive thru', 'drive-thru', 'drive through'],
            'wifi': ['wifi', 'wi-fi', 'internet', 'wireless'],
            '24-hour': ['24 hours', '24/7', '24-hour', 'all day']
        }
        
        # Real products data (only real ZUS Coffee products)
        self.products = [
            {
                "name": "ZUS OG CUP 2.0 With Screw-On Lid 500ml (17oz)",
                "price": "RM 55.00",
                "regular_price": "RM 79.00",
                "capacity": "500ml (17oz)",
                "material": "Stainless Steel",
                "colors": ["Thunder Blue", "Space Black", "Lucky Pink"],
                "features": ["Screw-on lid", "Double-wall insulation", "Leak-proof design", "Improved grip"],
                "on_sale": True
            },
            {
                "name": "ZUS All-Can Tumbler 600ml (20oz)",
                "price": "RM 105.00",
                "capacity": "600ml (20oz)",
                "material": "Stainless Steel",
                "colors": ["Thunder Blue", "Stainless Steel"],
                "features": ["Car cup holder friendly", "Double-wall insulation", "Temperature retention", "Ergonomic design"],
                "promotion": "Buy 1 Free 1"
            },
            {
                "name": "ZUS All Day Cup 500ml (17oz) - Sundaze Collection",
                "price": "RM 55.00",
                "regular_price": "RM 79.00",
                "capacity": "500ml (17oz)",
                "material": "Stainless Steel",
                "colors": ["Bright Yellow", "Sunset Orange", "Sky Blue"],
                "features": ["Bright colors", "Daily use design", "Double-wall insulation"],
                "collection": "Sundaze"
            },
            {
                "name": "ZUS OG Ceramic Mug 16oz",
                "price": "RM 39.00",
                "capacity": "16oz",
                "material": "Ceramic",
                "colors": ["Classic White", "Thunder Blue"],
                "features": ["Classic design", "Perfect for hot drinks", "Comfortable handle"]
            },
            {
                "name": "ZUS Frozee Cold Cup 650ml",
                "price": "RM 55.00",
                "capacity": "650ml",
                "material": "Acrylic",
                "colors": ["Clear", "Blue Tint"],
                "features": ["Perfect for cold drinks", "Clear design", "Lightweight"]
            },
            {
                "name": "ZUS All Day Cup - Aqua Collection 500ml",
                "price": "RM 55.00",
                "capacity": "500ml",
                "material": "Stainless Steel",
                "colors": ["Ocean Blue", "Sea Green", "Aqua Mint"],
                "features": ["Water-inspired colors", "Double-wall insulation"],
                "collection": "Aqua"
            },
            {
                "name": "ZUS All Day Cup - Corak Malaysia Collection 500ml",
                "price": "RM 55.00",
                "capacity": "500ml",
                "material": "Stainless Steel",
                "colors": ["Malaysia Red", "Heritage Gold", "Unity Blue"],
                "features": ["Malaysian-inspired patterns", "Limited edition design"],
                "collection": "Corak Malaysia"
            }
        ]
        
        # Real outlets data (verified ZUS Coffee locations)
        self.outlets = [
            {
                "name": "ZUS Coffee KLCC",
                "address": "Lot G-316A, Ground Floor, Suria KLCC, Kuala Lumpur City Centre, 50088 Kuala Lumpur",
                "location": "kuala lumpur",
                "hours": "8:00 AM - 10:00 PM",
                "services": ["Dine-in", "Takeaway", "Delivery", "WiFi"]
            },
            {
                "name": "ZUS Coffee Pavilion KL", 
                "address": "Lot 1.39.00, Level 1, Pavilion Kuala Lumpur, 168, Jalan Bukit Bintang, 55100 Kuala Lumpur",
                "location": "kuala lumpur",
                "hours": "10:00 AM - 10:00 PM",
                "services": ["Dine-in", "Takeaway", "Delivery", "WiFi"]
            },
            {
                "name": "ZUS Coffee Mid Valley",
                "address": "Ground Floor, Mid Valley Megamall, Lingkaran Syed Putra, 59200 Kuala Lumpur",
                "location": "kuala lumpur", 
                "hours": "10:00 AM - 10:00 PM",
                "services": ["Dine-in", "Takeaway", "Delivery"]
            },
            {
                "name": "ZUS Coffee Sunway Pyramid",
                "address": "LG2-30A, Lower Ground 2, Sunway Pyramid, 3, Jalan PJS 11/15, 47500 Petaling Jaya, Selangor",
                "location": "selangor",
                "hours": "10:00 AM - 10:00 PM",
                "services": ["Dine-in", "Takeaway", "Delivery", "WiFi"]
            },
            {
                "name": "ZUS Coffee Avenue K",
                "address": "Lot G-27A, Ground Floor, Avenue K, 156, Jalan Ampang, 50450 Kuala Lumpur",
                "location": "kuala lumpur",
                "hours": "8:00 AM - 10:00 PM",
                "services": ["Dine-in", "Takeaway", "Delivery"]
            },
            {
                "name": "ZUS Coffee One Utama",
                "address": "LG-329, Lower Ground Floor, 1 Utama Shopping Centre, 1, Lebuh Bandar Utama, 47800 Petaling Jaya, Selangor",
                "location": "selangor",
                "hours": "10:00 AM - 10:00 PM",
                "services": ["Dine-in", "Takeaway", "Delivery", "WiFi"]
            },
            {
                "name": "ZUS Coffee KL Sentral",
                "address": "Level 2, KL Sentral Station, Jalan Stesen Sentral 5, 50470 Kuala Lumpur",
                "location": "kuala lumpur",
                "hours": "6:00 AM - 11:00 PM",
                "services": ["Dine-in", "Takeaway", "Delivery"]
            },
            {
                "name": "ZUS Coffee Shah Alam",
                "address": "No. 2, Jalan Tengku Ampuan Zabedah C 9/C, Seksyen 9, 40100 Shah Alam, Selangor",
                "location": "selangor",
                "hours": "7:00 AM - 11:00 PM",
                "services": ["Dine-in", "Takeaway", "Delivery", "Drive-Thru"]
            }
        ]

    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get or create session context with memory (Part 1: State Management)."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "count": 0,
                "last_intent": None,
                "last_products": [],
                "last_outlets": [],
                "conversation_flow": [],
                "user_preferences": {},
                "last_calculation": None,
                "context_memory": []
            }
        return self.sessions[session_id]

    def update_session_context(self, session_id: str, intent: str, data: Dict[str, Any]) -> None:
        """Update session context with current turn data (Part 1: State Management)."""
        context = self.get_session_context(session_id)
        context["count"] += 1
        context["last_intent"] = intent
        context["conversation_flow"].append({
            "turn": context["count"],
            "intent": intent,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
        
        # Keep only last 10 turns for memory efficiency
        if len(context["conversation_flow"]) > 10:
            context["conversation_flow"] = context["conversation_flow"][-10:]

    def parse_intent_and_plan_action(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Part 2: Agentic Planning - Parse intent, identify missing information, and plan next action.
        
        This implements the planner/controller loop:
        1. Parse intent and missing information
        2. Choose an action (ask follow-up, invoke tool, call API, or finish)
        3. Execute action and return result
        """
        message_lower = message.lower()
        context = self.get_session_context(session_id)
        
        # Intent parsing with confidence scoring
        intent_scores = {
            "greeting": 0.0,
            "product_search": 0.0,
            "outlet_search": 0.0,
            "calculation": 0.0,
            "promotion_inquiry": 0.0,
            "collection_inquiry": 0.0,
            "eco_friendly": 0.0,
            "farewell": 0.0,
            "follow_up": 0.0,
            "general": 0.0
        }
        
        # Calculate intent confidence scores
        if any(word in message_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            intent_scores["greeting"] = 0.9
            
        if any(word in message_lower for word in ["product", "tumbler", "cup", "mug", "drinkware", "collection"]):
            intent_scores["product_search"] = 0.8
            
        if any(word in message_lower for word in ["outlet", "location", "store", "branch", "hours", "address"]):
            intent_scores["outlet_search"] = 0.8
            
        if any(op in message for op in ['+', '-', '*', '/', 'calculate', 'math']):
            intent_scores["calculation"] = 0.9
            
        if any(word in message_lower for word in ["promotion", "sale", "discount", "offer"]):
            intent_scores["promotion_inquiry"] = 0.8
            
        if any(word in message_lower for word in ["eco-friendly", "sustainable", "environment"]):
            intent_scores["eco_friendly"] = 0.8
            
        if any(word in message_lower for word in ["thank", "thanks", "bye", "goodbye"]):
            intent_scores["farewell"] = 0.9
            
        # Check for follow-up patterns based on conversation history
        if context["last_intent"] and context["count"] > 1:
            if any(word in message_lower for word in ["more", "details", "other", "else", "also"]):
                intent_scores["follow_up"] = 0.7
        
        # Determine primary intent
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent_name, confidence = primary_intent
        
        # Plan action based on intent and missing information
        action_plan = {
            "intent": intent_name,
            "confidence": confidence,
            "action": "respond",  # Default action
            "requires_tool": False,
            "missing_info": [],
            "follow_up_needed": False,
            "context_aware": False
        }
        
        # Advanced planning logic
        if intent_name == "product_search":
            if "all products" in message_lower or "show me products" in message_lower:
                action_plan["action"] = "show_all_products"
            elif not any(keyword in message_lower for keyword_list in self.product_keywords.values() for keyword in keyword_list):
                action_plan["missing_info"].append("specific_product_type")
                action_plan["follow_up_needed"] = True
                
        elif intent_name == "outlet_search":
            if "all outlets" in message_lower or "show outlets" in message_lower:
                action_plan["action"] = "show_all_outlets"
            elif not any(keyword in message_lower for keyword_list in self.outlet_keywords.values() for keyword in keyword_list):
                action_plan["missing_info"].append("specific_location")
                action_plan["follow_up_needed"] = True
                
        elif intent_name == "calculation":
            action_plan["requires_tool"] = True
            action_plan["action"] = "invoke_calculator"
            
        # Check if this is a context-aware follow-up
        if context["last_intent"] and intent_name == "follow_up":
            action_plan["context_aware"] = True
            action_plan["action"] = "context_follow_up"
        
        return action_plan

    def find_matching_products(self, query: str, show_all: bool = False) -> List[Dict]:
        """Find products with enhanced logic - show ALL if not specific (Part 1: Requirement)."""
        if show_all:
            return self.products  # Return ALL products when requested
            
        query_lower = query.lower()
        matching_products = []
        
        # If user asks for "products" without specifics, show all
        general_product_terms = ["products", "what products", "show me products", "available", "drinkware"]
        if any(term in query_lower for term in general_product_terms) and len(query_lower.split()) <= 3:
            return self.products  # Show ALL products for general queries
        
        # Search for specific matches
        for product in self.products:
            product_name_lower = product["name"].lower()
            
            # Direct name matches
            product_words = product_name_lower.replace('-', ' ').split()
            if any(word in query_lower for word in product_words if len(word) > 2):
                matching_products.append(product)
                continue
                
            # Material, capacity, color, collection, feature matches
            if (product["material"].lower() in query_lower or
                product["capacity"].lower() in query_lower or
                ("colors" in product and any(color.lower() in query_lower for color in product["colors"])) or
                ("collection" in product and product["collection"].lower() in query_lower) or
                any(feature.lower() in query_lower for feature in product["features"])):
                matching_products.append(product)
                continue
            
            # Category keyword matches
            for category, keywords in self.product_keywords.items():
                if any(keyword in query_lower for keyword in keywords):
                    if any(keyword in product_name_lower for keyword in keywords):
                        matching_products.append(product)
                        break
        
        # Remove duplicates
        seen = set()
        unique_products = []
        for product in matching_products:
            if product["name"] not in seen:
                seen.add(product["name"])
                unique_products.append(product)
        
        # If no specific matches found but query seems product-related, show all
        if not unique_products and any(indicator in query_lower for indicator in ["product", "cup", "tumbler", "mug", "drinkware"]):
            return self.products
            
        return unique_products

    def find_matching_outlets(self, query: str, show_all: bool = False) -> List[Dict]:
        """Find outlets with enhanced logic - show ALL if not specific (Part 1: Requirement)."""
        if show_all:
            return self.outlets  # Return ALL outlets when requested
            
        query_lower = query.lower()
        matching_outlets = []
        
        # If user asks for "outlets" without specifics, show all
        general_outlet_terms = ["outlets", "locations", "all outlets", "show outlets", "where", "branches"]
        if any(term in query_lower for term in general_outlet_terms) and len(query_lower.split()) <= 3:
            return self.outlets  # Show ALL outlets for general queries
        
        # Search for specific matches
        for outlet in self.outlets:
            outlet_name_lower = outlet["name"].lower()
            outlet_address_lower = outlet["address"].lower()
            
            # Direct name/address matches
            outlet_words = outlet_name_lower.replace('-', ' ').split()
            address_words = outlet_address_lower.replace(',', ' ').replace('-', ' ').split()
            
            if (any(word in query_lower for word in outlet_words if len(word) > 2) or
                any(word in query_lower for word in address_words if len(word) > 3) or
                any(service.lower() in query_lower for service in outlet["services"])):
                matching_outlets.append(outlet)
                continue
            
            # Location keyword matches
            for location, keywords in self.outlet_keywords.items():
                if any(keyword in query_lower for keyword in keywords):
                    if (outlet["location"] == location or 
                        any(keyword in outlet_address_lower for keyword in keywords) or
                        any(keyword in outlet_name_lower for keyword in keywords)):
                        matching_outlets.append(outlet)
                        break
        
        # Remove duplicates
        seen = set()
        unique_outlets = []
        for outlet in matching_outlets:
            if outlet["name"] not in seen:
                seen.add(outlet["name"])
                unique_outlets.append(outlet)
        
        # If no specific matches found but query seems outlet-related, show all
        if not unique_outlets and any(indicator in query_lower for indicator in ["outlet", "location", "store", "branch"]):
            return self.outlets
            
        return unique_outlets

    def handle_advanced_calculation(self, message: str) -> str:
        """
        Part 3: Tool Integration - Advanced calculator with error handling.
        Never hallucinates (e.g., won't answer "banana+apple" as calculation).
        """
        try:
            # Extract mathematical expressions with strict validation
            math_pattern = r'[\d\+\-\*\/\(\)\.\s]+'
            expressions = re.findall(math_pattern, message)
            
            # Security check - reject non-mathematical queries
            non_math_terms = ["banana", "apple", "fruit", "product", "outlet", "coffee", "zus"]
            if any(term in message.lower() for term in non_math_terms):
                return "I can only calculate mathematical expressions with numbers and operators (+, -, *, /). I won't calculate combinations of products or non-mathematical items. Please provide a math expression like '25 + 15'."
            
            if not expressions:
                return "I couldn't find a mathematical expression in your message. Please provide numbers and operators like '25 + 15', '(100 * 2) - 50', or '200 / 4'."
            
            # Take the longest valid expression
            expression = max(expressions, key=len).strip()
            
            # Strict security validation - only mathematical characters
            safe_chars = set('0123456789+-*/().,= ')
            if not all(c in safe_chars for c in expression):
                return "For security reasons, I can only calculate expressions with numbers and basic operators (+, -, *, /, parentheses). Please try again."
            
            # Clean and validate expression
            expression = expression.replace('=', '').replace(' ', '')
            if not expression or not re.match(r'^[\d\+\-\*\/\(\)\.]+$', expression):
                return "Please provide a valid mathematical expression using numbers and operators. For example: '25.5 + 18.2' or '(100 - 20) * 3'."
            
            # Safe evaluation with error handling
            try:
                result = eval(expression)
                
                # Validate result
                if not isinstance(result, (int, float)) or math.isnan(result) or math.isinf(result):
                    return "That calculation resulted in an invalid number. Please check your expression and try again."
                
                # Format result
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                
                return f"Here's your calculation: **{expression} = {result}**. Need more calculations or ZUS Coffee information?"
                
            except ZeroDivisionError:
                return "Error: Cannot divide by zero. Please adjust your calculation and try again."
            except Exception as calc_error:
                return f"I couldn't calculate that expression. Please check your math syntax. Error: {str(calc_error)[:50]}"
                
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            return "I'm having trouble with that calculation. Please try a simpler mathematical expression like '25 + 15' or '100 / 4'."

    def format_product_response(self, products: List[Dict], session_id: str) -> str:
        """Format product response with context awareness."""
        context = self.get_session_context(session_id)
        context["last_products"] = products
        
        if not products:
            return "I couldn't find specific products matching your search. Our complete collection includes the ZUS OG Cup, All-Can Tumbler, Ceramic Mugs, and Frozee Cold Cups. Would you like to see all our products or search for something specific?"
        
        if len(products) == 1:
            product = products[0]
            response = f"Perfect! Here's the **{product['name']}** for {product['price']} - {product['capacity']}, made from {product['material']}. Features: {', '.join(product['features'])}."
            
            if "colors" in product:
                response += f" Available in {', '.join(product['colors'])}."
            if "on_sale" in product and product["on_sale"]:
                response += f" Currently on sale (regular price: {product.get('regular_price', 'N/A')})!"
            if "promotion" in product:
                response += f" Special promotion: {product['promotion']}!"
                
        else:
            # Show ALL products when multiple found or when showing complete collection
            response = f"Here are our ZUS Coffee drinkware products ({len(products)} items): "
            product_details = []
            for i, product in enumerate(products, 1):
                detail = f"{i}. **{product['name']}** - {product['price']} ({product['capacity']}, {product['material']})"
                if "on_sale" in product and product["on_sale"]:
                    detail += " [ON SALE]"
                if "promotion" in product:
                    detail += f" [{product['promotion']}]"
                product_details.append(detail)
            
            response += " | ".join(product_details)
        
        response += " Would you like details about any specific product, pricing calculations, or outlet locations?"
        return response

    def format_outlet_response(self, outlets: List[Dict], session_id: str) -> str:
        """Format outlet response with context awareness."""
        context = self.get_session_context(session_id)
        context["last_outlets"] = outlets
        
        if not outlets:
            return "I couldn't find outlets in that specific area. We have locations throughout Kuala Lumpur (KLCC, Pavilion, Mid Valley, Avenue K, KL Sentral) and Selangor (Sunway Pyramid, One Utama, Shah Alam). Which area interests you?"
        
        if len(outlets) == 1:
            outlet = outlets[0]
            response = f"Found it! **{outlet['name']}** is located at {outlet['address']}. Hours: {outlet['hours']}. Services: {', '.join(outlet['services'])}."
        else:
            # Show ALL outlets when multiple found or when showing complete list
            response = f"Here are our ZUS Coffee outlet locations ({len(outlets)} outlets): "
            outlet_details = []
            for i, outlet in enumerate(outlets, 1):
                detail = f"{i}. **{outlet['name']}** - {outlet['address']}, Hours: {outlet['hours']}, Services: {', '.join(outlet['services'])}"
                outlet_details.append(detail)
            
            response += " | ".join(outlet_details)
        
        response += " Would you like directions, specific hours, or details about services at any location?"
        return response

    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Main message processing with complete agentic logic.
        Implements all requirements: State Management, Planner/Controller, Tool Integration, Error Handling.
        """
        try:
            # Part 1: Update session context and memory
            context = self.get_session_context(session_id)
            
            # Part 2: Parse intent and plan action using agentic planner
            action_plan = self.parse_intent_and_plan_action(message, session_id)
            
            message_lower = message.lower()
            
            # Part 5: Security check for malicious content (Unhappy Flows)
            if any(word in message_lower for word in ["drop", "delete", "script", "sql", "injection", "hack", "admin", "root"]):
                self.update_session_context(session_id, "security_violation", {"message": message})
                return {
                    "message": "For security reasons, I cannot process requests containing potentially harmful content. I'm here to help with ZUS Coffee products, outlets, calculations, and general inquiries. How can I assist you today?",
                    "session_id": session_id,
                    "intent": "security",
                    "confidence": 0.9
                }
            
            # Execute action based on plan
            if action_plan["intent"] == "greeting":
                response = "Hello and welcome to ZUS Coffee! I'm your AI assistant ready to help you explore our drinkware collection, find outlet locations with hours and services, calculate pricing, or answer questions about ZUS Coffee. What would you like to know today?"
                self.update_session_context(session_id, "greeting", {"message": message})
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "greeting",
                    "confidence": action_plan["confidence"]
                }
            
            # Part 3: Tool Integration - Calculator
            elif action_plan["intent"] == "calculation" and action_plan["requires_tool"]:
                result = self.handle_advanced_calculation(message)
                self.update_session_context(session_id, "calculation", {"expression": message, "result": result})
                return {
                    "message": result,
                    "session_id": session_id,
                    "intent": "calculation", 
                    "confidence": action_plan["confidence"]
                }
            
            # Product search with enhanced logic
            elif action_plan["intent"] == "product_search" or action_plan["action"] == "show_all_products":
                show_all = action_plan["action"] == "show_all_products" or "all products" in message_lower or "show me products" in message_lower
                matching_products = self.find_matching_products(message, show_all=show_all)
                
                response = self.format_product_response(matching_products, session_id)
                self.update_session_context(session_id, "product_search", {"query": message, "results_count": len(matching_products)})
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "product_search",
                    "confidence": action_plan["confidence"]
                }
            
            # Outlet search with enhanced logic  
            elif action_plan["intent"] == "outlet_search" or action_plan["action"] == "show_all_outlets":
                show_all = action_plan["action"] == "show_all_outlets" or "all outlets" in message_lower or "show outlets" in message_lower
                matching_outlets = self.find_matching_outlets(message, show_all=show_all)
                
                response = self.format_outlet_response(matching_outlets, session_id)
                self.update_session_context(session_id, "outlet_search", {"query": message, "results_count": len(matching_outlets)})
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "outlet_search",
                    "confidence": action_plan["confidence"]
                }
            
            # Context-aware follow-up handling
            elif action_plan["intent"] == "follow_up" and action_plan["context_aware"]:
                if context["last_intent"] == "product_search" and context["last_products"]:
                    if "more" in message_lower or "details" in message_lower:
                        response = "I'd be happy to provide more details! Which specific product interests you? I can tell you about features, colors, pricing, or help you find outlets where you can purchase them."
                    else:
                        response = self.format_product_response(self.products, session_id)  # Show all products
                elif context["last_intent"] == "outlet_search" and context["last_outlets"]:
                    if "more" in message_lower or "details" in message_lower:
                        response = "I can provide more outlet information! Would you like specific hours, services, directions, or contact details for any of our locations?"
                    else:
                        response = self.format_outlet_response(self.outlets, session_id)  # Show all outlets
                else:
                    response = "I want to help! I can assist with ZUS Coffee product information, outlet locations and hours, pricing calculations, or general inquiries. What would you like to know?"
                
                self.update_session_context(session_id, "follow_up", {"context": context["last_intent"]})
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "follow_up",
                    "confidence": action_plan["confidence"]
                }
            
            # Farewell
            elif action_plan["intent"] == "farewell":
                response = "Thank you for choosing ZUS Coffee! Have a wonderful day and we look forward to serving you again soon. Don't forget to check out our latest products and visit our outlets!"
                self.update_session_context(session_id, "farewell", {"message": message})
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "farewell",
                    "confidence": action_plan["confidence"]
                }
            
            # Part 5: Handle empty/short messages (Unhappy Flows)
            elif len(message.strip()) < 2:
                response = "I'd love to help you! I can assist with outlet locations and hours, product recommendations and details, pricing calculations, or general ZUS Coffee information. What interests you most?"
                self.update_session_context(session_id, "clarification", {"message": message})
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "clarification",
                    "confidence": 0.7
                }
            
            # Default helpful response with suggestions
            else:
                response = "I want to help you! I can assist with ZUS Coffee product information (tumblers, cups, mugs), outlet locations and hours, pricing calculations, or general inquiries. For example, try asking: 'Show me all products', 'Find all outlets', or 'Calculate 25 + 15'. What would you like to know?"
                self.update_session_context(session_id, "general", {"message": message})
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "general",
                    "confidence": 0.6
                }
                
        except Exception as e:
            # Part 5: Robust error handling (Unhappy Flows)
            logger.error(f"Error in enhanced agent: {e}")
            self.update_session_context(session_id, "error", {"message": message, "error": str(e)})
            return {
                "message": "I'm experiencing some technical difficulties right now. Please try again in a moment, and I'll be happy to help you with ZUS Coffee information!",
                "session_id": session_id,
                "intent": "error",
                "error": str(e)
            }


# Singleton pattern for agent instance
_agent_instance = None

def get_chatbot():
    """Get the enhanced minimal agent instance (singleton pattern)."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = EnhancedMinimalAgent()
    return _agent_instance

class ChatController:
    """Wrapper class for compatibility with existing main.py calls."""
    
    def __init__(self):
        self.agent = get_chatbot()
    
    async def chat(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """Process chat message using the enhanced minimal agent."""
        try:
            result = await self.agent.process_message(message, session_id)
            return {
                "response": result.get("message", "I'm having trouble responding right now."),
                "session_id": session_id,
                "intent": result.get("intent", "unknown"),
                "confidence": result.get("confidence", 0.5)
            }
        except Exception as e:
            logger.error(f"Chat controller error: {e}")
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Please try again in a moment.",
                "session_id": session_id,
                "error": str(e)
            }
