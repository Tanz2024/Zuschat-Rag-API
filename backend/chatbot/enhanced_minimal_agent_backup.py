#!/usr/bin/env python3
"""
Enhanced minimal chatbot agent with proper keyword matching
Handles real ZUS Coffee products and outlets with clean emoji-free responses
"""

import logging
import re
import json
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class EnhancedMinimalAgent:
    """Enhanced minimal chatbot with real data keyword matching."""
    
    def __init__(self):
        self.sessions = {}
        
        # Real product keywords from products.json (comprehensive)
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
        
        # Real outlet locations (comprehensive from database)
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
        
        # Real products data (from products.json)
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
        
        # Real outlets data (from database analysis - verified locations)
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
    
    def find_matching_products(self, query: str) -> List[Dict]:
        """Find products based on comprehensive keywords in query."""
        query_lower = query.lower()
        matching_products = []
        
        # Check each product for keyword matches
        for product in self.products:
            product_name_lower = product["name"].lower()
            
            # Direct name matches (any word from product name)
            product_words = product_name_lower.replace('-', ' ').split()
            if any(word in query_lower for word in product_words if len(word) > 2):
                matching_products.append(product)
                continue
            
            # Material matches
            if product["material"].lower() in query_lower:
                matching_products.append(product)
                continue
                
            # Capacity/size matches
            if product["capacity"].lower() in query_lower:
                matching_products.append(product)
                continue
            
            # Color matches (if available)
            if "colors" in product:
                if any(color.lower() in query_lower for color in product["colors"]):
                    matching_products.append(product)
                    continue
            
            # Collection matches
            if "collection" in product:
                if product["collection"].lower() in query_lower:
                    matching_products.append(product)
                    continue
            
            # Feature matches  
            if any(feature.lower() in query_lower for feature in product["features"]):
                matching_products.append(product)
                continue
            
            # Category keyword matches (comprehensive)
            for category, keywords in self.product_keywords.items():
                if any(keyword in query_lower for keyword in keywords):
                    # Check if this product matches the category
                    if any(keyword in product_name_lower for keyword in keywords):
                        matching_products.append(product)
                        break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_products = []
        for product in matching_products:
            if product["name"] not in seen:
                seen.add(product["name"])
                unique_products.append(product)
        
        return unique_products[:3]  # Return max 3 products
    
    def find_matching_outlets(self, query: str) -> List[Dict]:
        """Find outlets based on comprehensive location keywords in query."""
        query_lower = query.lower()
        matching_outlets = []
        
        # Check each outlet for location/name matches
        for outlet in self.outlets:
            outlet_name_lower = outlet["name"].lower()
            outlet_address_lower = outlet["address"].lower()
            
            # Direct name matches (any word from outlet name)
            outlet_words = outlet_name_lower.replace('-', ' ').split()
            if any(word in query_lower for word in outlet_words if len(word) > 2):
                matching_outlets.append(outlet)
                continue
            
            # Direct address matches (any word from address)
            address_words = outlet_address_lower.replace(',', ' ').replace('-', ' ').split()
            if any(word in query_lower for word in address_words if len(word) > 3):
                matching_outlets.append(outlet)
                continue
            
            # Services matches
            if any(service.lower() in query_lower for service in outlet["services"]):
                matching_outlets.append(outlet)
                continue
            
            # Location keyword matches (comprehensive)
            for location, keywords in self.outlet_keywords.items():
                if any(keyword in query_lower for keyword in keywords):
                    # Check if this outlet matches the location
                    if (outlet["location"] == location or 
                        any(keyword in outlet_address_lower for keyword in keywords) or
                        any(keyword in outlet_name_lower for keyword in keywords)):
                        matching_outlets.append(outlet)
                        break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_outlets = []
        for outlet in matching_outlets:
            if outlet["name"] not in seen:
                seen.add(outlet["name"])
                unique_outlets.append(outlet)
        
        return unique_outlets[:3]  # Return max 3 outlets
    
    def format_product_response(self, products: List[Dict]) -> str:
        """Format product list response without problematic emojis."""
        if not products:
            return "I couldn't find specific products matching your search. Our popular items include the ZUS OG Cup, All-Can Tumbler, Ceramic Mugs, and Frozee Cold Cups. Would you like to see our full collection or search for something specific?"
        
        if len(products) == 1:
            product = products[0]
            response = f"Perfect! Here's the **{product['name']}** for {product['price']} - {product['capacity']}, made from {product['material']}. Features: {', '.join(product['features'])}."
            
            if "colors" in product:
                response += f" Available in {', '.join(product['colors'])}."
            if "on_sale" in product and product["on_sale"]:
                response += f" Currently on sale (regular price: {product.get('regular_price', 'N/A')})."
            if "promotion" in product:
                response += f" Special promotion: {product['promotion']}."
            
        else:
            response = f"Great! Here are {len(products)} ZUS Coffee products for you: "
            product_details = []
            for i, product in enumerate(products, 1):
                detail = f"{i}. **{product['name']}** - {product['price']} ({product['capacity']}, {product['material']})"
                if "on_sale" in product and product["on_sale"]:
                    detail += " [ON SALE]"
                if "promotion" in product:
                    detail += f" [{product['promotion']}]"
                product_details.append(detail)
            
            response += " | ".join(product_details)
        
        response += " Would you like more details about any of these products, pricing calculations, or outlet locations?"
        return response
    
    def format_outlet_response(self, outlets: List[Dict]) -> str:
        """Format outlet list response without problematic emojis."""
        if not outlets:
            return "I couldn't find outlets in that specific area. We have locations in Kuala Lumpur (KLCC, Pavilion, Mid Valley, Avenue K, KL Sentral) and Selangor (Sunway Pyramid, One Utama, Shah Alam). Which area would you like to explore?"
        
        if len(outlets) == 1:
            outlet = outlets[0]
            response = f"Found it! **{outlet['name']}** is located at {outlet['address']}. Hours: {outlet['hours']}. Services: {', '.join(outlet['services'])}."
        else:
            response = f"Great! Here are {len(outlets)} ZUS Coffee outlets for you: "
            outlet_details = []
            for i, outlet in enumerate(outlets, 1):
                detail = f"{i}. **{outlet['name']}** - {outlet['address']}, Hours: {outlet['hours']}"
                outlet_details.append(detail)
            
            response += " | ".join(outlet_details)
        
    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """Process message with enhanced keyword matching and intelligent intent detection."""
        try:
            # Store session
            if session_id not in self.sessions:
                self.sessions[session_id] = {"count": 0}
            
            self.sessions[session_id]["count"] += 1
            message_lower = message.lower()
            
            # PRIORITY 1: Product queries (most specific first)
            product_keywords = ['tumbler', 'cup', 'mug', 'bottle', 'drinkware', 'product', 'steel', 'ceramic', 'acrylic', 
                              'og cup', 'all-can', 'frozee', 'sundaze', 'aqua', 'corak', 'collection', 'rm', 'price', 
                              'under', 'below', 'eco-friendly', 'eco', 'available', 'show me', 'what', 'which']
            
            if any(keyword in message_lower for keyword in product_keywords):
                matching_products = self.find_matching_products(message)
                
                # Handle price filters
                if 'under' in message_lower or 'below' in message_lower:
                    price_match = re.search(r'(under|below).*?rm\s*(\d+)', message_lower)
                    if price_match:
                        max_price = float(price_match.group(2))
                        filtered_products = []
                        for product in matching_products:
                            product_price = float(product['price'].replace('RM ', '').replace(',', ''))
                            if product_price <= max_price:
                                filtered_products.append(product)
                        matching_products = filtered_products
                
                # Handle "all products" or general queries
                if any(word in message_lower for word in ['all', 'what', 'show me', 'available']) and not matching_products:
                    matching_products = self.products[:3]  # Show first 3 products
                
                response = self.format_product_response(matching_products)
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "product_search",
                    "confidence": 0.9
                }
            
            # PRIORITY 2: Outlet/location queries
            outlet_keywords = ['outlet', 'location', 'store', 'branch', 'klcc', 'pavilion', 'sunway', 'mid valley', 
                             'selangor', 'kuala lumpur', 'kl', 'shah alam', 'avenue k', 'one utama', 'sentral',
                             'drive-thru', 'drive thru', '24 hour', '24/7', 'open', 'hours', 'dine-in', 'takeaway',
                             'delivery', 'wifi', 'service']
            
            if any(keyword in message_lower for keyword in outlet_keywords):
                matching_outlets = self.find_matching_outlets(message)
                
                # Handle "all outlets" queries
                if any(word in message_lower for word in ['all', 'show me']) and not matching_outlets:
                    matching_outlets = self.outlets[:4]  # Show first 4 outlets
                
                response = self.format_outlet_response(matching_outlets)
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "outlet_search",
                    "confidence": 0.9
                }
            
            # PRIORITY 3: Calculation queries
            calc_keywords = ['+', '-', '*', '/', 'calculate', 'add', 'multiply', '%', 'percent']
            if any(op in message for op in calc_keywords) or re.search(r'\d+.*\d+', message):
                try:
                    calc_part = message
                    if 'calculate' in message_lower:
                        calc_part = re.sub(r'calculate\s*', '', message_lower)
                    
                    # Handle basic operations
                    if '+' in calc_part:
                        numbers = re.findall(r'\d+\.?\d*', calc_part)
                        if len(numbers) >= 2:
                            result = float(numbers[0]) + float(numbers[1])
                            response = f"Calculation complete! {numbers[0]} + {numbers[1]} = {result}. Anything else I can calculate?"
                        else:
                            response = "I need two numbers to add. Please provide something like '25.50 + 18.90'."
                    elif '*' in calc_part or 'multiply' in calc_part:
                        numbers = re.findall(r'\d+\.?\d*', calc_part)
                        if len(numbers) >= 2:
                            result = float(numbers[0]) * float(numbers[1])
                            response = f"Calculation complete! {numbers[0]} × {numbers[1]} = {result}. Anything else I can calculate?"
                        else:
                            response = "I need two numbers to multiply. Please provide something like '23 * 4'."
                    elif '%' in calc_part or 'percent' in calc_part:
                        percent_match = re.search(r'(\d+\.?\d*).*?percent.*?(\d+\.?\d*)|(\d+\.?\d*).*?%.*?(\d+\.?\d*)', calc_part)
                        if percent_match:
                            groups = percent_match.groups()
                            if groups[0] and groups[1]:
                                percent, value = float(groups[0]), float(groups[1])
                            elif groups[2] and groups[3]:
                                percent, value = float(groups[2]), float(groups[3])
                            else:
                                percent, value = 0, 0
                            
                            if percent > 0 and value > 0:
                                result = (percent / 100) * value
                                response = f"Calculation complete! {percent}% of {value} = {result:.2f}. Anything else I can calculate?"
                            else:
                                response = "Please provide a percentage calculation like '15% of 200'."
                        else:
                            response = "Please provide a percentage calculation like '15% of 200'."
                    else:
                        response = "I can help with calculations! Please provide expressions like '25 + 15', '23 * 4', or '15% of 200'."
                        
                    return {
                        "message": response,
                        "session_id": session_id,
                        "intent": "calculation",
                        "confidence": 0.8
                    }
                except:
                    response = "I had trouble with that calculation. Please use simple expressions like '25 + 15' or '15% of 200'."
                    return {
                        "message": response,
                        "session_id": session_id,
                        "intent": "calculation",
                        "confidence": 0.6
                    }
            
            # PRIORITY 4: Greeting detection
            if any(word in message_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
                response = "Hello and welcome to ZUS Coffee! I'm your AI assistant ready to help you explore our drinkware collection, find outlet locations with hours and services, calculate pricing, or answer questions about ZUS Coffee. What would you like to know today?"
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "greeting",
                    "confidence": 0.9
                }
            
            # PRIORITY 5: Farewell detection
            if any(word in message_lower for word in ["thank", "thanks", "bye", "goodbye", "see you"]):
                response = "Thank you for choosing ZUS Coffee! Have a wonderful day and we look forward to serving you again soon. Don't forget to check out our latest products and visit our outlets!"
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "farewell",
                    "confidence": 0.9
                }
            
            # PRIORITY 6: Empty or very short messages
            if len(message.strip()) < 2:
                response = "I'd love to help you! I can assist with outlet locations and hours, product recommendations and details, pricing calculations, or general ZUS Coffee information. What interests you most?"
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "clarification",
                    "confidence": 0.7
                }
            
            # PRIORITY 7: Security check for malicious content
            if any(word in message_lower for word in ["drop", "delete", "script", "sql", "injection", "hack"]):
                response = "I can't process that type of request for security reasons. I'm here to help with ZUS Coffee products, outlet locations, calculations, and general inquiries. What would you like to know?"
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "security",
                    "confidence": 0.9
                }
            
            # DEFAULT: Helpful fallback response
            response = "I want to help you! I can assist with ZUS Coffee product information (tumblers, cups, mugs), outlet locations and hours, pricing calculations, or general inquiries. Could you please be more specific about what you're looking for?"
            return {
                "message": response,
                "session_id": session_id,
                "intent": "general",
                "confidence": 0.5
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced minimal agent: {e}")
            return {
                "message": "I'm experiencing some technical difficulties right now. Please try again in a moment, and I'll be happy to help you with ZUS Coffee information!",
                "session_id": session_id,
                "error": str(e)
            }

# Global instance
_enhanced_minimal_agent = None

def get_chatbot():
    """Get the enhanced minimal agent instance."""
    global _enhanced_minimal_agent
    if _enhanced_minimal_agent is None:
        _enhanced_minimal_agent = EnhancedMinimalAgent()
    return _enhanced_minimal_agent
