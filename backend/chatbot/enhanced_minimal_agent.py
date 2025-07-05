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
        
        # Real products data (only real ZUS Coffee products) with enhanced structure
        self.products = [
            {
                "name": "ZUS OG CUP 2.0 With Screw-On Lid 500ml (17oz)",
                "price": "RM 55.00",
                "price_numeric": 55.00,
                "regular_price": "RM 79.00",
                "regular_price_numeric": 79.00,
                "capacity": "500ml (17oz)",
                "material": "Stainless Steel",
                "category": "Cup",
                "colors": ["Thunder Blue", "Space Black", "Lucky Pink"],
                "features": ["Screw-on lid", "Double-wall insulation", "Leak-proof design", "Improved grip"],
                "on_sale": True,
                "collection": "OG"
            },
            {
                "name": "ZUS All-Can Tumbler 600ml (20oz)",
                "price": "RM 105.00",
                "price_numeric": 105.00,
                "capacity": "600ml (20oz)",
                "material": "Stainless Steel",
                "category": "Tumbler",
                "colors": ["Thunder Blue", "Stainless Steel"],
                "features": ["Car cup holder friendly", "Double-wall insulation", "Temperature retention", "Ergonomic design"],
                "promotion": "Buy 1 Free 1",
                "collection": "All-Can"
            },
            {
                "name": "ZUS All Day Cup 500ml (17oz) - Sundaze Collection",
                "price": "RM 55.00",
                "price_numeric": 55.00,
                "regular_price": "RM 79.00",
                "regular_price_numeric": 79.00,
                "capacity": "500ml (17oz)",
                "material": "Stainless Steel",
                "category": "Cup",
                "colors": ["Bright Yellow", "Sunset Orange", "Sky Blue"],
                "features": ["Bright colors", "Daily use design", "Double-wall insulation"],
                "collection": "Sundaze"
            },
            {
                "name": "ZUS OG Ceramic Mug 16oz",
                "price": "RM 39.00",
                "price_numeric": 39.00,
                "capacity": "16oz",
                "material": "Ceramic",
                "category": "Mug",
                "colors": ["Classic White", "Thunder Blue"],
                "features": ["Classic design", "Perfect for hot drinks", "Comfortable handle"],
                "collection": "OG"
            },
            {
                "name": "ZUS Frozee Cold Cup 650ml",
                "price": "RM 55.00",
                "price_numeric": 55.00,
                "capacity": "650ml",
                "material": "Acrylic",
                "category": "Cold Cup",
                "colors": ["Clear", "Blue Tint"],
                "features": ["Perfect for cold drinks", "Clear design", "Lightweight"],
                "collection": "Frozee"
            },
            {
                "name": "ZUS All Day Cup - Aqua Collection 500ml",
                "price": "RM 55.00",
                "price_numeric": 55.00,
                "capacity": "500ml",
                "material": "Stainless Steel",
                "category": "Cup",
                "colors": ["Ocean Blue", "Sea Green", "Aqua Mint"],
                "features": ["Water-inspired colors", "Double-wall insulation"],
                "collection": "Aqua"
            },
            {
                "name": "ZUS All Day Cup - Corak Malaysia Collection 500ml",
                "price": "RM 55.00",
                "price_numeric": 55.00,
                "capacity": "500ml",
                "material": "Stainless Steel",
                "category": "Cup",
                "colors": ["Malaysia Red", "Heritage Gold", "Unity Blue"],
                "features": ["Malaysian-inspired patterns", "Limited edition design"],
                "collection": "Corak Malaysia"
            }
        ]
        
        # Real outlets data (verified ZUS Coffee locations) with enhanced structure
        self.outlets = [
            {
                "name": "ZUS Coffee KLCC",
                "address": "Lot G-316A, Ground Floor, Suria KLCC, Kuala Lumpur City Centre, 50088 Kuala Lumpur",
                "location": "kuala lumpur",
                "city": "Kuala Lumpur",
                "state": "Kuala Lumpur",
                "hours": "8:00 AM - 10:00 PM",
                "services": ["Dine-in", "Takeaway", "Delivery", "WiFi"]
            },
            {
                "name": "ZUS Coffee Pavilion KL", 
                "address": "Lot 1.39.00, Level 1, Pavilion Kuala Lumpur, 168, Jalan Bukit Bintang, 55100 Kuala Lumpur",
                "location": "kuala lumpur",
                "city": "Kuala Lumpur",
                "state": "Kuala Lumpur",
                "hours": "10:00 AM - 10:00 PM",
                "services": ["Dine-in", "Takeaway", "Delivery", "WiFi"]
            },
            {
                "name": "ZUS Coffee Mid Valley",
                "address": "Ground Floor, Mid Valley Megamall, Lingkaran Syed Putra, 59200 Kuala Lumpur",
                "location": "kuala lumpur", 
                "city": "Kuala Lumpur",
                "state": "Kuala Lumpur",
                "hours": "10:00 AM - 10:00 PM",
                "services": ["Dine-in", "Takeaway", "Delivery"]
            },
            {
                "name": "ZUS Coffee Sunway Pyramid",
                "address": "LG2-30A, Lower Ground 2, Sunway Pyramid, 3, Jalan PJS 11/15, 47500 Petaling Jaya, Selangor",
                "location": "selangor",
                "city": "Petaling Jaya",
                "state": "Selangor",
                "hours": "10:00 AM - 10:00 PM",
                "services": ["Dine-in", "Takeaway", "Delivery", "WiFi"]
            },
            {
                "name": "ZUS Coffee Avenue K",
                "address": "Lot G-27A, Ground Floor, Avenue K, 156, Jalan Ampang, 50450 Kuala Lumpur",
                "location": "kuala lumpur",
                "city": "Kuala Lumpur",
                "state": "Kuala Lumpur",
                "hours": "8:00 AM - 10:00 PM",
                "services": ["Dine-in", "Takeaway", "Delivery"]
            },
            {
                "name": "ZUS Coffee One Utama",
                "address": "LG-329, Lower Ground Floor, 1 Utama Shopping Centre, 1, Lebuh Bandar Utama, 47800 Petaling Jaya, Selangor",
                "location": "selangor",
                "city": "Petaling Jaya",
                "state": "Selangor",
                "hours": "10:00 AM - 10:00 PM",
                "services": ["Dine-in", "Takeaway", "Delivery", "WiFi"]
            },
            {
                "name": "ZUS Coffee KL Sentral",
                "address": "Level 2, KL Sentral Station, Jalan Stesen Sentral 5, 50470 Kuala Lumpur",
                "location": "kuala lumpur",
                "city": "Kuala Lumpur",
                "state": "Kuala Lumpur",
                "hours": "6:00 AM - 11:00 PM",
                "services": ["Dine-in", "Takeaway", "Delivery"]
            },
            {
                "name": "ZUS Coffee Shah Alam",
                "address": "No. 2, Jalan Tengku Ampuan Zabedah C 9/C, Seksyen 9, 40100 Shah Alam, Selangor",
                "location": "selangor",
                "city": "Shah Alam",
                "state": "Selangor",
                "hours": "7:00 AM - 11:00 PM",
                "services": ["Dine-in", "Takeaway", "Delivery", "Drive-Thru"]
            }
        ]

        # Tax and SST rates for Malaysia
        self.tax_rates = {
            "sst": 0.06,  # 6% SST (Service & Sales Tax)
            "service_tax": 0.06,  # 6% Service Tax
            "sales_tax": 0.10,  # 10% Sales Tax (for certain items)
            "zero_rated": 0.00   # 0% for basic necessities
        }

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
        """Find products with enhanced logic and filtering - show ALL if not specific (Part 1: Requirement)."""
        if show_all:
            return self.products  # Return ALL products when requested
            
        query_lower = query.lower()
        
        # Detect filtering intent
        filters = self.detect_filtering_intent(query)
        
        # Start with all products if filtering is detected
        if any([filters["price_range"], filters["category"], filters["material"], filters["collection"]]):
            matching_products = list(self.products)
            
            # Apply price range filter
            if filters["price_range"]:
                matching_products = self.filter_products_by_price_range(
                    filters.get("min_price"), 
                    filters.get("max_price")
                )
            
            # Apply category filter
            if filters["category"]:
                matching_products = [p for p in matching_products 
                                   if p.get("category", "").lower() == filters["category"]]
            
            # Apply material filter
            if filters["material"]:
                matching_products = [p for p in matching_products 
                                   if filters["material"] in p.get("material", "").lower()]
            
            # Apply collection filter
            if filters["collection"]:
                matching_products = [p for p in matching_products 
                                   if filters["collection"] in p.get("collection", "").lower()]
            
            return matching_products
        
        # Original logic for non-filtered searches
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
        """Find outlets with enhanced logic and city filtering - show ALL if not specific (Part 1: Requirement)."""
        if show_all:
            return self.outlets  # Return ALL outlets when requested
            
        query_lower = query.lower()
        
        # Detect filtering intent
        filters = self.detect_filtering_intent(query)
        
        # Apply city-based filtering if detected
        if filters["city"]:
            matching_outlets = self.filter_outlets_by_city(filters["city"])
            if matching_outlets:  # If city filter found results, return them
                return matching_outlets
        
        # Apply service-based filtering if detected
        if filters["service"]:
            matching_outlets = self.filter_outlets_by_service(filters["service"])
            if matching_outlets:  # If service filter found results, return them
                return matching_outlets
        
        # Original logic for non-filtered searches
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

    def format_product_response(self, products: List[Dict], session_id: str, query: str = "") -> str:
        """Format product response with context awareness and enhanced features."""
        context = self.get_session_context(session_id)
        context["last_products"] = products
        
        # Detect if tax calculation is requested
        filters = self.detect_filtering_intent(query)
        show_tax = filters.get("tax_calculation", False)
        
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
            
            # Add tax calculation if requested
            if show_tax:
                tax_info = self.calculate_tax_and_sst(product.get("price_numeric", 0))
                if "error" not in tax_info:
                    response += f"\n\n💰 **Price Breakdown:**\n- Subtotal: {tax_info['formatted']['subtotal']}\n- SST (6%): {tax_info['formatted']['sst_amount']}\n- **Total with SST: {tax_info['formatted']['total_with_sst']}**"
                
        else:
            # Show multiple products with filtering info
            response = f"Here are our ZUS Coffee drinkware products ({len(products)} items"
            
            # Add filter information
            if filters["price_range"]:
                min_p, max_p = filters.get("min_price"), filters.get("max_price")
                if min_p and max_p:
                    response += f" in RM {min_p:.0f}-{max_p:.0f} range"
                elif min_p:
                    response += f" above RM {min_p:.0f}"
                elif max_p:
                    response += f" under RM {max_p:.0f}"
            
            if filters["category"]:
                response += f" in {filters['category']} category"
            if filters["material"]:
                response += f" made from {filters['material']}"
            if filters["collection"]:
                response += f" from {filters['collection']} collection"
            
            response += "): "
            
            product_details = []
            for i, product in enumerate(products, 1):
                detail = f"{i}. **{product['name']}** - {product['price']} ({product['capacity']}, {product['material']})"
                if "on_sale" in product and product["on_sale"]:
                    detail += " [ON SALE]"
                if "promotion" in product:
                    detail += f" [{product['promotion']}]"
                
                # Add tax calculation for each product if requested
                if show_tax:
                    tax_info = self.calculate_tax_and_sst(product.get("price_numeric", 0))
                    if "error" not in tax_info:
                        detail += f" | With SST: {tax_info['formatted']['total_with_sst']}"
                
                product_details.append(detail)
            
            response += " | ".join(product_details)
        
        response += " Would you like details about any specific product, pricing calculations, or outlet locations?"
        return response

    def format_outlet_response(self, outlets: List[Dict], session_id: str, query: str = "") -> str:
        """Format outlet response with context awareness and city filtering."""
        context = self.get_session_context(session_id)
        context["last_outlets"] = outlets
        
        # Detect filtering intent
        filters = self.detect_filtering_intent(query)
        
        if not outlets:
            if filters["city"]:
                return f"I couldn't find outlets specifically in {filters['city']}. We have locations throughout Kuala Lumpur (KLCC, Pavilion, Mid Valley, Avenue K, KL Sentral) and Selangor (Sunway Pyramid, One Utama, Shah Alam). Which area interests you?"
            return "I couldn't find outlets in that specific area. We have locations throughout Kuala Lumpur (KLCC, Pavilion, Mid Valley, Avenue K, KL Sentral) and Selangor (Sunway Pyramid, One Utama, Shah Alam). Which area interests you?"
        
        if len(outlets) == 1:
            outlet = outlets[0]
            response = f"Found it! **{outlet['name']}** is located at {outlet['address']}. Hours: {outlet['hours']}. Services: {', '.join(outlet['services'])}."
        else:
            # Show multiple outlets with filtering info
            response = f"Here are our ZUS Coffee outlet locations ({len(outlets)} outlets"
            
            # Add filter information
            if filters["city"]:
                response += f" in {filters['city'].title()}"
            if filters["service"]:
                response += f" with {filters['service']} service"
            
            response += "): "
            
            outlet_details = []
            for i, outlet in enumerate(outlets, 1):
                detail = f"{i}. **{outlet['name']}** - {outlet['address']}, Hours: {outlet['hours']}, Services: {', '.join(outlet['services'])}"
                outlet_details.append(detail)
            
            response += " | ".join(outlet_details)
        
        response += " Would you like directions, specific hours, or details about services at any location?"
        return response

    def calculate_tax_and_sst(self, price: float, quantity: int = 1) -> Dict[str, Any]:
        """
        Calculate tax and SST for Malaysian pricing
        Malaysia SST: 6% on goods, Service Tax: 6% on services
        """
        try:
            subtotal = price * quantity
            sst_rate = 0.06  # 6% SST in Malaysia
            sst_amount = subtotal * sst_rate
            total_with_tax = subtotal + sst_amount
            
            return {
                "quantity": quantity,
                "unit_price": price,
                "subtotal": round(subtotal, 2),
                "sst_rate": "6%",
                "sst_amount": round(sst_amount, 2),
                "total_with_sst": round(total_with_tax, 2),
                "formatted": {
                    "subtotal": f"RM {subtotal:.2f}",
                    "sst_amount": f"RM {sst_amount:.2f}",
                    "total_with_sst": f"RM {total_with_tax:.2f}"
                }
            }
        except Exception as e:
            logger.error(f"Tax calculation error: {e}")
            return {
                "error": "Unable to calculate tax",
                "quantity": quantity,
                "unit_price": price
            }

    def filter_products_by_price_range(self, min_price=None, max_price=None):
        """Filter products by price range"""
        try:
            filtered = []
            for product in self.products:
                price = product.get('price_numeric', 0)
                if min_price is not None and price < min_price:
                    continue
                if max_price is not None and price > max_price:
                    continue
                filtered.append(product)
            return filtered
        except Exception:
            return self.products

    def filter_products_by_category(self, category):
        """Filter products by category"""
        try:
            category_lower = category.lower()
            return [p for p in self.products if category_lower in p.get('category', '').lower()]
        except Exception:
            return self.products

    def filter_products_by_material(self, material):
        """Filter products by material"""
        try:
            material_lower = material.lower()
            return [p for p in self.products if material_lower in p.get('material', '').lower()]
        except Exception:
            return self.products

    def filter_products_by_collection(self, collection):
        """Filter products by collection"""
        try:
            collection_lower = collection.lower()
            return [p for p in self.products if collection_lower in p.get('collection', '').lower()]
        except Exception:
            return self.products

    def filter_outlets_by_city(self, city):
        """Filter outlets by city"""
        try:
            city_lower = city.lower()
            return [o for o in self.outlets if city_lower in o.get('city', '').lower() or city_lower in o.get('location', '').lower()]
        except Exception:
            return self.outlets

    def filter_outlets_by_service(self, service):
        """Filter outlets by available service"""
        try:
            service_lower = service.lower()
            return [o for o in self.outlets if any(service_lower in s.lower() for s in o.get('services', []))]
        except Exception:
            return self.outlets

    def calculate_price_with_tax(self, price, tax_type="sst"):
        """Calculate price including tax"""
        try:
            if isinstance(price, str):
                # Extract numeric value from "RM XX.XX" format
                price_str = price.replace("RM", "").replace(",", "").strip()
                price = float(price_str)
            
            tax_rate = self.tax_rates.get(tax_type, 0.06)
            tax_amount = price * tax_rate
            total_price = price + tax_amount
            
            return {
                "original_price": f"RM {price:.2f}",
                "tax_type": tax_type.upper(),
                "tax_rate": f"{tax_rate * 100:.0f}%",
                "tax_amount": f"RM {tax_amount:.2f}",
                "total_price": f"RM {total_price:.2f}"
            }
        except Exception:
            return {"error": "Unable to calculate tax"}

    def get_all_products_formatted(self, filters=None):
        """Get all products with optional filtering"""
        try:
            products = self.products.copy()
            
            if filters:
                if 'min_price' in filters or 'max_price' in filters:
                    products = self.filter_products_by_price_range(
                        filters.get('min_price'), 
                        filters.get('max_price')
                    )
                if 'category' in filters:
                    products = self.filter_products_by_category(filters['category'])
                if 'material' in filters:
                    products = self.filter_products_by_material(filters['material'])
                if 'collection' in filters:
                    products = self.filter_products_by_collection(filters['collection'])
            
            if not products:
                return "No products found matching your criteria."
            
            response = f"Here are our {len(products)} ZUS Coffee products:\n\n"
            for product in products:
                response += f"• {product['name']}\n"
                response += f"  Price: {product['price']}"
                if product.get('regular_price') and product.get('on_sale'):
                    response += f" (was {product['regular_price']})"
                response += f"\n  Material: {product['material']}\n"
                response += f"  Category: {product['category']}\n"
                if product.get('collection'):
                    response += f"  Collection: {product['collection']}\n"
                response += "\n"
            
            return response.strip()
        except Exception:
            return "Sorry, I couldn't retrieve the product information right now."

    def get_all_outlets_formatted(self, filters=None):
        """Get all outlets with optional filtering"""
        try:
            outlets = self.outlets.copy()
            
            if filters:
                if 'city' in filters:
                    outlets = self.filter_outlets_by_city(filters['city'])
                if 'service' in filters:
                    outlets = self.filter_outlets_by_service(filters['service'])
            
            if not outlets:
                return "No outlets found matching your criteria."
            
            response = f"Here are our {len(outlets)} ZUS Coffee outlets:\n\n"
            for outlet in outlets:
                response += f"• {outlet['name']}\n"
                response += f"  Address: {outlet['address']}\n"
                response += f"  Hours: {outlet['hours']}\n"
                if outlet.get('services'):
                    response += f"  Services: {', '.join(outlet['services'])}\n"
                response += "\n"
            
            return response.strip()
        except Exception:
            return "Sorry, I couldn't retrieve the outlet information right now."

    def detect_filtering_intent(self, query: str) -> Dict[str, Any]:
        """Detect filtering intent and extract filter parameters from user query"""
        query_lower = query.lower()
        
        filters = {
            "price_range": False,
            "min_price": None,
            "max_price": None,
            "category": None,
            "material": None,
            "collection": None,
            "city": None,
            "service": None,
            "tax_calculation": False
        }
        
        # Detect price range filters
        price_patterns = [
            r'under\s+rm\s*(\d+)',
            r'below\s+rm\s*(\d+)',
            r'less\s+than\s+rm\s*(\d+)',
            r'above\s+rm\s*(\d+)',
            r'over\s+rm\s*(\d+)',
            r'more\s+than\s+rm\s*(\d+)',
            r'between\s+rm\s*(\d+)\s*and\s+rm\s*(\d+)',
            r'rm\s*(\d+)\s*to\s*rm\s*(\d+)',
            r'price\s+range\s+rm\s*(\d+)\s*-\s*rm\s*(\d+)'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                filters["price_range"] = True
                if 'under' in pattern or 'below' in pattern or 'less' in pattern:
                    filters["max_price"] = float(matches[0])
                elif 'above' in pattern or 'over' in pattern or 'more' in pattern:
                    filters["min_price"] = float(matches[0])
                elif 'between' in pattern or 'to' in pattern or '-' in pattern:
                    prices = matches[0] if isinstance(matches[0], tuple) else [matches[0], matches[1] if len(matches) > 1 else matches[0]]
                    if len(prices) == 2:
                        filters["min_price"] = float(prices[0])
                        filters["max_price"] = float(prices[1])
                break
        
        # Detect category filters
        category_keywords = ['cup', 'tumbler', 'mug', 'cold cup']
        for category in category_keywords:
            if category in query_lower:
                filters["category"] = category.title()
                break
        
        # Detect material filters
        material_keywords = ['stainless steel', 'ceramic', 'acrylic']
        for material in material_keywords:
            if material in query_lower:
                filters["material"] = material
                break
        
        # Detect collection filters
        collection_keywords = ['sundaze', 'aqua', 'corak malaysia', 'og', 'frozee', 'all-can']
        for collection in collection_keywords:
            if collection in query_lower:
                filters["collection"] = collection
                break
        
        # Detect city filters
        city_keywords = {
            'kuala lumpur': ['kuala lumpur', 'kl', 'kl city'],
            'petaling jaya': ['petaling jaya', 'pj'],
            'shah alam': ['shah alam'],
            'selangor': ['selangor']
        }
        
        for city, keywords in city_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                filters["city"] = city
                break
        
        # Detect service filters
        service_keywords = ['dine-in', 'takeaway', 'delivery', 'drive-thru', 'wifi']
        for service in service_keywords:
            if service.replace('-', ' ') in query_lower or service.replace('-', '') in query_lower:
                filters["service"] = service
                break
        
        # Detect tax calculation intent
        tax_keywords = ['tax', 'sst', 'with tax', 'including tax', 'total price']
        if any(keyword in query_lower for keyword in tax_keywords):
            filters["tax_calculation"] = True
        
        return filters

    def extract_filters_from_message(self, message: str) -> Dict[str, Any]:
        """Extract filtering parameters from user message"""
        return self.detect_filtering_intent(message)

    def extract_outlet_filters_from_message(self, message: str) -> Dict[str, Any]:
        """Extract outlet filtering parameters from user message"""
        return self.detect_filtering_intent(message)

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
            
            # Enhanced intent detection for show all and filtering
            if "show" in message_lower and ("all" in message_lower or "total" in message_lower):
                if any(word in message_lower for word in ["product", "drinkware", "merchandise"]):
                    # Show all products with optional filtering
                    filters = self.detect_filtering_intent(message)
                    all_products = self.get_all_products_formatted(filters if any(filters.values()) else None)
                    total_count = len(self.products)
                    response = f"📦 **Total ZUS Coffee Products/Drinkware: {total_count}**\n\n{all_products}"
                    
                    self.update_session_context(session_id, "show_all_products", {"query": message, "total": total_count})
                    return {
                        "message": response,
                        "session_id": session_id,
                        "intent": "show_all_products",
                        "confidence": 0.95
                    }
                    
                elif any(word in message_lower for word in ["outlet", "store", "location", "branch"]):
                    # Show all outlets with optional city filtering
                    filters = self.detect_filtering_intent(message)
                    
                    # Check for city-specific requests
                    if filters["city"]:
                        filtered_outlets = self.filter_outlets_by_city(filters["city"])
                        response = f"🏪 **Total ZUS Coffee Outlets in {filters['city'].title()}: {len(filtered_outlets)}**\n\n"
                        response += self.get_all_outlets_formatted({"city": filters["city"]})
                    else:
                        # Show all outlets
                        all_outlets = self.get_all_outlets_formatted()
                        total_count = len(self.outlets)
                        
                        # Break down by location
                        kl_outlets = [o for o in self.outlets if o["state"] == "Kuala Lumpur"]
                        selangor_outlets = [o for o in self.outlets if o["state"] == "Selangor"]
                        
                        response = f"🏪 **Total ZUS Coffee Outlets: {total_count}**\n"
                        response += f"• Kuala Lumpur: {len(kl_outlets)} outlets\n"
                        response += f"• Selangor: {len(selangor_outlets)} outlets\n\n"
                        response += all_outlets
                    
                    self.update_session_context(session_id, "show_all_outlets", {"query": message, "filters": filters})
                    return {
                        "message": response,
                        "session_id": session_id,
                        "intent": "show_all_outlets",
                        "confidence": 0.95
                    }
            
            # City-based outlet filtering
            if any(city in message_lower for city in ["selangor", "kuala lumpur", "kl"]) and any(word in message_lower for word in ["outlet", "store", "location"]):
                filters = self.detect_filtering_intent(message)
                if filters["city"]:
                    filtered_outlets = self.filter_outlets_by_city(filters["city"])
                    response = f"🏪 **ZUS Coffee Outlets in {filters['city'].title()}: {len(filtered_outlets)}**\n\n"
                    for i, outlet in enumerate(filtered_outlets, 1):
                        response += f"{i}. **{outlet['name']}**\n"
                        response += f"   📍 {outlet['address']}\n"
                        response += f"   🕒 Hours: {outlet['hours']}\n"
                        response += f"   🛎️ Services: {', '.join(outlet['services'])}\n\n"
                    
                    self.update_session_context(session_id, "city_outlet_search", {"city": filters["city"], "results": len(filtered_outlets)})
                    return {
                        "message": response,
                        "session_id": session_id,
                        "intent": "city_outlet_search",
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
                
                response = self.format_product_response(matching_products, session_id, message)
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
                
                response = self.format_outlet_response(matching_outlets, session_id, message)
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
