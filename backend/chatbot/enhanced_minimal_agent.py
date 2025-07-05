#!/usr/bin/env python3
"""
Enhanced minimal chatbot agent with proper keyword matching - FIXED VERSION
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
        
        response += " Would you like directions, contact information, or details about specific services?"
        return response

    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """Process message with ADVANCED pattern detection and routing."""
        try:
            # Store session
            if session_id not in self.sessions:
                self.sessions[session_id] = {"count": 0}
            
            self.sessions[session_id]["count"] += 1
            message_lower = message.lower()
            
            # ADVANCED PATTERN DETECTION
            patterns = self.detect_advanced_patterns(message)
            
            # PRIORITY 1: Greeting detection (but not 24-hour queries)
            if (any(word in message_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon"]) and
                not any(word in message_lower for word in ["24", "hour", "outlet", "open"])):
                response = "Hello and welcome to ZUS Coffee! I'm your AI assistant ready to help you explore our drinkware collection, find outlet locations with hours and services, calculate pricing, or answer questions about ZUS Coffee. What would you like to know today?"
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "greeting",
                    "confidence": 0.9
                }
            
            # PRIORITY 2: Advanced Pattern Responses (What's new, promotions, best-selling, etc.)
            if patterns['patterns']['whats_new']:
                response = self.get_whats_new_response()
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "whats_new",
                    "confidence": 0.95
                }
            
            if patterns['patterns']['promotions']:
                response = self.get_promotions_response()
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "promotions",
                    "confidence": 0.95
                }
            
            if patterns['patterns']['best_selling'] and not patterns['has_location']:
                response = self.get_best_selling_response()
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "best_selling",
                    "confidence": 0.95
                }
            
            if patterns['patterns']['collections'] and not patterns['has_location']:
                response = self.get_collections_response()
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "collections",
                    "confidence": 0.95
                }
            
            if patterns['patterns']['eco_friendly'] and not patterns['has_location']:
                response = self.get_eco_friendly_response()
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "eco_friendly",
                    "confidence": 0.95
                }
            
            # PRIORITY 3: Outlet/location queries with advanced detection
            outlet_indicators = ['outlet', 'location', 'store', 'branch', 'klcc', 'pavilion', 'sunway', 'mid valley', 
                               'selangor', 'kuala lumpur', 'kl', 'shah alam', 'avenue k', 'one utama', 'sentral',
                               'drive-thru', 'drive thru', '24 hour', '24/7', 'open', 'hours', 'dine-in', 'takeaway',
                               'delivery', 'wifi', 'service', 'where', 'find', 'near', 'all outlets', 'show outlets',
                               'locations', 'which outlets', 'outlet locations']
            
            is_outlet_query = (any(indicator in message_lower for indicator in outlet_indicators) or
                             'outlet' in message_lower or 'location' in message_lower or patterns['has_location'])
            
            if is_outlet_query:
                matching_outlets = self.find_matching_outlets(message)
                
                # Handle specific advanced queries
                if patterns['patterns']['near_location'] and 'klcc' in message_lower:
                    klcc_outlets = [o for o in self.outlets if 'KLCC' in o['name'] or 'klcc' in o['address'].lower()]
                    if klcc_outlets:
                        response = f"Perfect! **ZUS Coffee KLCC** is right in Suria KLCC at {klcc_outlets[0]['address']}. Open {klcc_outlets[0]['hours']} with services: {', '.join(klcc_outlets[0]['services'])}. It's conveniently located on the Ground Floor, perfect for shopping breaks or quick coffee runs!"
                    else:
                        response = "ZUS Coffee KLCC is located in Suria KLCC shopping center, perfect for your visit to the twin towers area!"
                    return {
                        "message": response,
                        "session_id": session_id,
                        "intent": "outlet_search_klcc",
                        "confidence": 0.9
                    }
                
                if patterns['patterns']['drive_thru']:
                    drive_thru_outlets = [o for o in self.outlets if 'Drive-Thru' in o['services']]
                    if drive_thru_outlets:
                        response = f"For drive-thru convenience, visit **{drive_thru_outlets[0]['name']}** at {drive_thru_outlets[0]['address']}. Open {drive_thru_outlets[0]['hours']} with full drive-thru service plus {', '.join([s for s in drive_thru_outlets[0]['services'] if s != 'Drive-Thru'])}. Perfect for busy days when you need your ZUS Coffee on the go!"
                        matching_outlets = drive_thru_outlets
                    else:
                        response = "Currently, our **Shah Alam outlet** offers Drive-Thru service for ultimate convenience. Most other ZUS Coffee outlets provide Dine-in, Takeaway, and Delivery options. Would you like to see all our outlet locations?"
                    return {
                        "message": response,
                        "session_id": session_id,
                        "intent": "outlet_search_drive_thru",
                        "confidence": 0.9
                    }
                    
                if patterns['patterns']['hours_24']:
                    response = "Most ZUS Coffee outlets operate from early morning to late evening (typically 6:00 AM - 11:00 PM). **KL Sentral** opens earliest at 6:00 AM and some locations stay open until 11:00 PM for late-night coffee lovers. While we don't currently have 24-hour outlets, our extended hours cover most of your coffee needs. Would you like specific outlet hours?"
                    return {
                        "message": response,
                        "session_id": session_id,
                        "intent": "outlet_search_24hours",
                        "confidence": 0.9
                    }
                
                # Handle "all outlets" queries with enhanced response
                if patterns['patterns']['all_outlets'] or (any(phrase in message_lower for phrase in ['all outlets', 'show outlets', 'all locations', 'show me all', 'outlet locations']) 
                    and not matching_outlets):
                    matching_outlets = self.outlets[:6]  # Show first 6 outlets
                    response = "Here are our ZUS Coffee outlet locations: "
                    outlet_details = []
                    for i, outlet in enumerate(matching_outlets, 1):
                        detail = f"{i}. **{outlet['name']}** - {outlet['address']}, Hours: {outlet['hours']}"
                        outlet_details.append(detail)
                    response += " | ".join(outlet_details)
                    response += " Each outlet offers unique ambiance with consistent ZUS quality. Which location interests you most?"
                    return {
                        "message": response,
                        "session_id": session_id,
                        "intent": "outlet_search_all",
                        "confidence": 0.9
                    }
                
                response = self.format_outlet_response(matching_outlets)
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "outlet_search",
                    "confidence": 0.9
                }
            
            # PRIORITY 4: Product/drinkware queries with advanced pattern detection
            product_indicators = ['product', 'tumbler', 'cup', 'mug', 'bottle', 'drinkware', 'collection', 
                                'stainless steel', 'ceramic', 'acrylic', 'steel', 'sundaze', 'aqua', 
                                'corak malaysia', 'og cup', 'all-can', 'all day', 'frozee', 'cold cup',
                                '500ml', '600ml', '16oz', 'under rm', 'price range', 'eco-friendly',
                                'insulation', 'leak proof', 'car holder', 'blue', 'black', 'pink',
                                'green', 'orange', 'what products', 'collections', 'available', 'options',
                                'drinks', 'best selling', 'popular']
            
            is_product_query = (any(indicator in message_lower for indicator in product_indicators) and 
                              not is_outlet_query) or patterns['has_product']
            is_pure_calculation = (any(op in message for op in ['+', '-', '*', '/']) and 
                                 not any(indicator in message_lower for indicator in product_indicators))
            
            if is_product_query and not is_pure_calculation:
                # Handle price range queries with advanced detection
                if patterns['patterns']['price_range'] and patterns['price_limit']:
                    max_price = patterns['price_limit']
                    matching_products = []
                    for p in self.products:
                        try:
                            product_price = float(p['price'].replace('RM ', '').replace(',', ''))
                            if product_price <= max_price:
                                matching_products.append(p)
                        except:
                            continue
                    
                    if matching_products:
                        response = f"Perfect! Here are ZUS Coffee products under RM{max_price}: "
                        product_details = []
                        for i, product in enumerate(matching_products, 1):
                            detail = f"{i}. **{product['name']}** - {product['price']} ({product['material']}, {product['capacity']})"
                            if 'on_sale' in product and product['on_sale']:
                                detail += " [ON SALE - Great Deal!]"
                            product_details.append(detail)
                        response += " | ".join(product_details)
                        response += f" All these options offer excellent value under your RM{max_price} budget!"
                    else:
                        response = f"Looking for drinkware under RM{max_price}? Our **ZUS OG Ceramic Mug** at RM39.00 is perfect for your budget! It's great for hot drinks with classic design and comfortable handle."
                    
                    return {
                        "message": response,
                        "session_id": session_id,
                        "intent": "product_search_price_range",
                        "confidence": 0.95
                    }
                
                # Material-specific queries
                if patterns['patterns']['material_specific']:
                    if 'steel' in message_lower or 'stainless' in message_lower:
                        steel_products = [p for p in self.products if 'Stainless Steel' in p['material']]
                        response = "Our premium **stainless steel collection** offers the best in durability and insulation: "
                        product_details = []
                        for i, product in enumerate(steel_products, 1):
                            detail = f"{i}. **{product['name']}** - {product['price']} ({product['capacity']})"
                            if 'on_sale' in product and product['on_sale']:
                                detail += " [ON SALE]"
                            if 'promotion' in product:
                                detail += f" [{product['promotion']}]"
                            product_details.append(detail)
                        response += " | ".join(product_details)
                        response += " All feature double-wall insulation and leak-proof design for the ultimate coffee experience!"
                        return {
                            "message": response,
                            "session_id": session_id,
                            "intent": "product_search_steel",
                            "confidence": 0.95
                        }
                
                # Standard product search
                matching_products = self.find_matching_products(message)
                
                # Handle "all products" with enhanced response
                if patterns['patterns']['all_products'] and not matching_products:
                    matching_products = self.products[:5]
                    response = "Here's our complete ZUS Coffee drinkware collection: "
                    product_details = []
                    for i, product in enumerate(matching_products, 1):
                        detail = f"{i}. **{product['name']}** - {product['price']} ({product['material']}, {product['capacity']})"
                        if 'on_sale' in product and product['on_sale']:
                            detail += " [ON SALE]"
                        if 'promotion' in product:
                            detail += f" [{product['promotion']}]"
                        product_details.append(detail)
                    response += " | ".join(product_details)
                    response += " Each product is crafted for quality, style, and functionality. What catches your eye?"
                    return {
                        "message": response,
                        "session_id": session_id,
                        "intent": "product_search_all",
                        "confidence": 0.9
                    }
                
                response = self.format_product_response(matching_products)
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "product_search",
                    "confidence": 0.9
                }
            
            # PRIORITY 4: Pure calculation queries (only when no product/outlet context)
            if is_pure_calculation or ('calculate' in message_lower and not is_product_query):
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
            
            # PRIORITY 5: Farewell detection
            elif any(word in message_lower for word in ["thank", "thanks", "bye", "goodbye", "see you"]):
                response = "Thank you for choosing ZUS Coffee! Have a wonderful day and we look forward to serving you again soon. Don't forget to check out our latest products and visit our outlets!"
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "farewell",
                    "confidence": 0.9
                }
            
            # PRIORITY 6: Empty or very short messages
            elif len(message.strip()) < 2:
                response = "I'd love to help you! I can assist with outlet locations and hours, product recommendations and details, pricing calculations, or general ZUS Coffee information. What interests you most?"
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "clarification",
                    "confidence": 0.7
                }
            
            # PRIORITY 7: Security check for malicious content
            elif any(word in message_lower for word in ["drop", "delete", "script", "sql", "injection", "hack"]):
                response = "I can't process that type of request for security reasons. I'm here to help with ZUS Coffee products, outlet locations, calculations, and general inquiries. What would you like to know?"
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "security",
                    "confidence": 0.9
                }
            
            # PRIORITY 8: Default helpful response with suggestions
            else:
                response = "I want to help you! I can assist with ZUS Coffee product information (tumblers, cups, mugs), outlet locations and hours, pricing calculations, or general inquiries. For example, try asking: 'Show me tumblers', 'Find outlets in KLCC', or 'Calculate 25 + 15'. What would you like to know?"
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "general",
                    "confidence": 0.6
                }
                
        except Exception as e:
            logger.error(f"Error in enhanced minimal agent: {e}")
            return {
                "message": "I'm experiencing some technical difficulties right now. Please try again in a moment, and I'll be happy to help you with ZUS Coffee information!",
                "session_id": session_id,
                "error": str(e)
            }

    def detect_advanced_patterns(self, message: str) -> Dict[str, Any]:
        """Detect advanced patterns and intentions in user messages."""
        message_lower = message.lower()
        patterns = {
            'whats_new': any(phrase in message_lower for phrase in ['what\'s new', 'whats new', 'new at zus', 'latest', 'this month', 'recent']),
            'best_selling': any(phrase in message_lower for phrase in ['best selling', 'bestselling', 'popular', 'top selling', 'most popular']),
            'promotions': any(phrase in message_lower for phrase in ['promotion', 'promo', 'sale', 'discount', 'offer', 'deal', 'special', 'available today']),
            'price_range': any(phrase in message_lower for phrase in ['under rm', 'below rm', 'less than rm', 'price range', 'budget']),
            'collections': any(phrase in message_lower for phrase in ['collection', 'collections', 'what collections', 'drinkware collections']),
            'eco_friendly': any(phrase in message_lower for phrase in ['eco-friendly', 'sustainable', 'environmentally friendly', 'green']),
            'material_specific': any(phrase in message_lower for phrase in ['steel', 'stainless steel', 'ceramic', 'acrylic']),
            'near_location': any(phrase in message_lower for phrase in ['near', 'nearby', 'close to', 'around']),
            'drive_thru': any(phrase in message_lower for phrase in ['drive-thru', 'drive thru', 'drive through']),
            'hours_24': any(phrase in message_lower for phrase in ['24 hours', '24/7', 'open 24', 'all night']),
            'all_products': any(phrase in message_lower for phrase in ['all products', 'what products', 'show me products', 'what do you have']),
            'all_outlets': any(phrase in message_lower for phrase in ['all outlets', 'all locations', 'show outlets', 'outlet locations'])
        }
        
        # Extract price range if specified
        price_match = re.search(r'under rm\s*(\d+)|below rm\s*(\d+)|less than rm\s*(\d+)', message_lower)
        price_limit = None
        if price_match:
            price_limit = float(price_match.group(1) or price_match.group(2) or price_match.group(3))
        
        return {
            'patterns': patterns,
            'price_limit': price_limit,
            'has_location': any(patterns[key] for key in ['near_location', 'drive_thru', 'hours_24', 'all_outlets']),
            'has_product': any(patterns[key] for key in ['best_selling', 'collections', 'eco_friendly', 'material_specific', 'all_products'])
        }

    def get_whats_new_response(self) -> str:
        """Generate response about what's new at ZUS Coffee."""
        return ("Here's what's exciting at ZUS Coffee this month! Our **ZUS OG Cup 2.0** is currently on sale for RM 55.00 (regular RM 79.00) with improved screw-on lid and better grip. The **All-Can Tumbler** has a special Buy 1 Free 1 promotion. We also have our beautiful collections: **Sundaze** with bright vibrant colors, **Aqua** with water-inspired tones, and **Corak Malaysia** celebrating our heritage. All feature premium stainless steel construction and double-wall insulation. What catches your interest?")

    def get_best_selling_response(self) -> str:
        """Generate response about best-selling products."""
        best_sellers = [
            "**ZUS OG Cup 2.0** - Our flagship 500ml stainless steel cup with screw-on lid, currently on sale!",
            "**ZUS All-Can Tumbler** - Perfect 600ml car-friendly tumbler with Buy 1 Free 1 promotion",
            "**ZUS All Day Cup Sundaze Collection** - Bright, cheerful colors perfect for daily use"
        ]
        return f"Our best-selling drinkware includes: {' | '.join(best_sellers)}. These are customer favorites for their quality, design, and functionality. Would you like detailed information about any of these?"

    def get_promotions_response(self) -> str:
        """Generate response about current promotions."""
        return ("Current ZUS Coffee promotions: **ZUS OG Cup 2.0** is on sale for RM 55.00 (regular RM 79.00) - that's 30% off! Plus our **ZUS All-Can Tumbler** has a special Buy 1 Free 1 offer. These deals won't last long, so grab yours today! All our products come with premium features like double-wall insulation and leak-proof design. Which promotion interests you most?")

    def get_collections_response(self) -> str:
        """Generate response about drinkware collections."""
        collections = [
            "**Sundaze Collection** - Bright, vibrant colors (Bright Yellow, Sunset Orange, Sky Blue) perfect for energetic days",
            "**Aqua Collection** - Water-inspired tones (Ocean Blue, Sea Green, Aqua Mint) for a refreshing feel", 
            "**Corak Malaysia Collection** - Heritage-inspired patterns (Malaysia Red, Heritage Gold, Unity Blue) celebrating our culture"
        ]
        return f"ZUS Coffee has three beautiful drinkware collections: {' | '.join(collections)}. All collections feature premium 500ml stainless steel construction with double-wall insulation. Which collection speaks to you?"

    def get_eco_friendly_response(self) -> str:
        """Generate response about eco-friendly options."""
        eco_products = [p for p in self.products if 'Stainless Steel' in p['material']]
        response = "Great choice for the environment! Our **stainless steel drinkware** is the most eco-friendly option - reusable, durable, and plastic-free. Featured eco-friendly products: "
        
        eco_details = []
        for product in eco_products[:3]:
            detail = f"**{product['name']}** - {product['price']} (premium stainless steel, double-wall insulation)"
            if 'on_sale' in product and product['on_sale']:
                detail += " [ON SALE]"
            eco_details.append(detail)
        
        response += " | ".join(eco_details)
        response += " By choosing ZUS drinkware, you're reducing single-use cup waste and supporting sustainability!"
        return response

# Global instance
_enhanced_minimal_agent = None

def get_chatbot():
    """Get the enhanced minimal agent instance."""
    global _enhanced_minimal_agent
    if _enhanced_minimal_agent is None:
        _enhanced_minimal_agent = EnhancedMinimalAgent()
    return _enhanced_minimal_agent
