#!/usr/bin/env python3
"""
ZUS Coffee Chatbot Agent - Production Implementation
Integrated chatbot system with conversation state management, intent planning, 
math calculations, and database integration for product/outlet queries.
"""

import logging
import re
import json

import math
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Database components import with fallback handling
DATABASE_AVAILABLE = False
SessionLocal = None
Product = None
Outlet = None

try:
    try:
        from backend.data.database import SessionLocal, Product, Outlet
    except ImportError:
        from data.database import SessionLocal, Product, Outlet
    DATABASE_AVAILABLE = True
    logger.info("Database components imported successfully")
except Exception as e:
    logger.warning(f"Database not available, using file-based data: {e}")

# File data loader for fallback when database is unavailable
FILE_LOADER_AVAILABLE = False
load_products_from_file = None
load_outlets_from_file = None

try:
    try:
        from backend.data.file_data_loader import load_products_from_file, load_outlets_from_file
    except ImportError:
        from data.file_data_loader import load_products_from_file, load_outlets_from_file
    FILE_LOADER_AVAILABLE = True
    logger.info("File data loader imported successfully")
except Exception as e:
    logger.warning(f"File data loader not available: {e}")

class EnhancedMinimalAgent:
    def __init__(self):
        self.sessions = {}  # Conversation state storage
        
        # Intent planning keywords and patterns
        self.product_keywords = {
            'categories': ['tumbler', 'cup', 'mug', 'cold cup', 'drinkware'],
            'materials': ['stainless steel', 'ceramic', 'acrylic', 'glass'],
            'features': ['leak-proof', 'dishwasher safe', 'double wall', 'insulated'],
            'collections': ['sundaze', 'aqua', 'corak malaysia', 'og', 'frozee', 'all-can'],
            'general': ['product', 'item', 'drinkware', 'collection']
        }
        
        # Text2SQL for natural language outlet queries (Part 4)
        self.outlet_keywords = {
            'locations': ['location', 'outlet', 'store', 'branch', 'address', 'where'],
            'cities': ['kl', 'kuala lumpur', 'petaling jaya', 'pj', 'selangor', 'klcc', 'pavilion', 'mid valley', 'ss2'],
            'services': ['drive-thru', 'dine-in', 'takeaway', '24 hours', '24/7', 'wifi', 'parking'],
            'hours': ['open', 'hours', 'timing', '24 hours', 'late night', 'early morning']
        }

        # Tax and calculation keywords (Part 3 + SST/Tax support)
        self.tax_keywords = ['tax', 'sst', 'gst', 'total', 'calculate tax', 'with tax', 'including tax']
        self.tax_rates = {
            'sst': 0.06,  # 6% SST in Malaysia
            'gst': 0.06,  # If GST returns
            'service': 0.10  # 10% service charge
        }
        
        # Math calculation patterns
        self.math_operators = ['+', '-', '*', '/', 'x', '×', '÷', '^', '**', 'sqrt', '%', 'of']
        self.math_keywords = ['calculate', 'math', 'compute', 'what is', 'plus', 'minus', 'times', 'divided by', 'power', 'square root', 'percent']

    # --- Advanced: Hybrid Search (Semantic + Fuzzy + Keyword) ---
    def hybrid_search_products(self, query: str, top_k: int = 5, lang: str = "en") -> List[Dict]:
        """
        Hybrid search: translate, semantic, fuzzy, and keyword fallback for products.
        Returns unique, best-matching products.
        """
        translated_query = self.translate_query(query, target_lang=lang)
        seen = set()
        results = []
        # Semantic search
        try:
            for p in self.semantic_search_products(translated_query, top_k=top_k):
                if p['name'] not in seen:
                    seen.add(p['name'])
                    results.append(p)
        except Exception:
            pass
        # Fuzzy search
        try:
            for p in self.fuzzy_match_products(translated_query, top_k=top_k):
                if p['name'] not in seen:
                    seen.add(p['name'])
                    results.append(p)
        except Exception:
            pass
        # Keyword fallback
        for p in self.find_matching_products(translated_query):
            if p['name'] not in seen:
                seen.add(p['name'])
                results.append(p)
        return results[:top_k]

    def hybrid_search_outlets(self, query: str, top_k: int = 5, lang: str = "en") -> List[Dict]:
        """
        Hybrid search: translate, semantic, fuzzy, and keyword fallback for outlets.
        Returns unique, best-matching outlets.
        """
        translated_query = self.translate_query(query, target_lang=lang)
        seen = set()
        results = []
        # Semantic search
        try:
            for o in self.semantic_search_outlets(translated_query, top_k=top_k):
                if o['name'] not in seen:
                    seen.add(o['name'])
                    results.append(o)
        except Exception:
            pass
        # Fuzzy search
        try:
            for o in self.fuzzy_match_outlets(translated_query, top_k=top_k):
                if o['name'] not in seen:
                    seen.add(o['name'])
                    results.append(o)
        except Exception:
            pass
        # Keyword fallback
        for o in self.find_matching_outlets(translated_query):
            if o['name'] not in seen:
                seen.add(o['name'])
                results.append(o)
        return results[:top_k]
    # --- Advanced: Fuzzy Matching and Synonym Support ---
    def fuzzy_match_products(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Fuzzy match products by name and description using rapidfuzz for typos and synonyms.
        """
        try:
            from rapidfuzz import process, fuzz
            products = self.get_products()
            product_texts = [p['name'] + ' ' + (p.get('description') or '') for p in products]
            matches = process.extract(query, product_texts, scorer=fuzz.token_sort_ratio, limit=top_k)
            indices = [m[2] for m in matches if m[1] > 60]  # Only strong matches
            return [products[i] for i in indices]
        except Exception as e:
            logger.warning(f"Fuzzy match unavailable, falling back to keyword search: {e}")
            return self.find_matching_products(query)

    def fuzzy_match_outlets(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Fuzzy match outlets by name and address using rapidfuzz for typos and synonyms.
        """
        try:
            from rapidfuzz import process, fuzz
            outlets = self.get_outlets()
            outlet_texts = [o['name'] + ' ' + (o.get('address') or '') for o in outlets]
            matches = process.extract(query, outlet_texts, scorer=fuzz.token_sort_ratio, limit=top_k)
            indices = [m[2] for m in matches if m[1] > 60]
            return [outlets[i] for i in indices]
        except Exception as e:
            logger.warning(f"Fuzzy match unavailable, falling back to keyword search: {e}")
            return self.find_matching_outlets(query)

    # --- Advanced: Multi-language Support (Translation) ---
    def translate_query(self, query: str, target_lang: str = "en") -> str:
        """
        Simple language detection and basic translation fallback.
        For production, consider using a dedicated translation service.
        """
        try:
            # Simple language detection based on common patterns
            # For now, just return the original query since most users use English/Malay
            # In future, can integrate with cloud translation services
            logger.info(f"Translation requested for: {query}")
            return query
        except Exception as e:
            logger.warning(f"Translation unavailable, using original query: {e}")
            return query
    # --- Semantic Search Integration (Vector Store) ---
    def semantic_search_products(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Perform semantic search for products using a vector store (e.g., FAISS).
        Falls back to keyword search if vector store is unavailable.
        """
        try:
            from sentence_transformers import SentenceTransformer, util
            import numpy as np
            # Load or cache model (in production, use a singleton or DI)
            if not hasattr(self, '_embedder'):
                self._embedder = SentenceTransformer('all-MiniLM-L6-v2')
            embedder = self._embedder
            products = self.get_products()
            product_texts = [p['name'] + ' ' + (p.get('description') or '') for p in products]
            product_embeddings = embedder.encode(product_texts, convert_to_tensor=True)
            query_embedding = embedder.encode([query], convert_to_tensor=True)
            cos_scores = util.pytorch_cos_sim(query_embedding, product_embeddings)[0].cpu().numpy()
            top_indices = np.argsort(-cos_scores)[:top_k]
            return [products[i] for i in top_indices]
        except Exception as e:
            logger.warning(f"Semantic search unavailable, falling back to keyword search: {e}")
            return self.find_matching_products(query)

    def semantic_search_outlets(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Perform semantic search for outlets using a vector store (e.g., FAISS).
        Falls back to keyword search if vector store is unavailable.
        """
        try:
            from sentence_transformers import SentenceTransformer, util
            import numpy as np
            if not hasattr(self, '_embedder'):
                self._embedder = SentenceTransformer('all-MiniLM-L6-v2')
            embedder = self._embedder
            outlets = self.get_outlets()
            outlet_texts = [o['name'] + ' ' + (o.get('address') or '') for o in outlets]
            outlet_embeddings = embedder.encode(outlet_texts, convert_to_tensor=True)
            query_embedding = embedder.encode([query], convert_to_tensor=True)
            cos_scores = util.pytorch_cos_sim(query_embedding, outlet_embeddings)[0].cpu().numpy()
            top_indices = np.argsort(-cos_scores)[:top_k]
            return [outlets[i] for i in top_indices]
        except Exception as e:
            logger.warning(f"Semantic search unavailable, falling back to keyword search: {e}")
            return self.find_matching_outlets(query)
    """
    ZUS Coffee chatbot implementation with the following features:
    - Conversation state management and memory tracking
    - Intent detection and response planning
    - Mathematical calculations with error handling
    - Product and outlet database integration
    - Robust error handling and fallback mechanisms
    """
    

    def get_products(self) -> List[Dict]:
        """Fetch all products from the database as dicts. Always returns a safe fallback if DB is down."""
        try:
            # Try database first if available
            if DATABASE_AVAILABLE and SessionLocal and Product:
                with SessionLocal() as db:
                    products = db.query(Product).all()
                    result = []
                    for p in products:
                        # Parse JSON fields if needed
                        colors = []
                        features = []
                        try:
                            if p.colors:
                                colors = json.loads(p.colors) if isinstance(p.colors, str) else p.colors
                        except Exception:
                            colors = []
                        try:
                            if p.features:
                                features = json.loads(p.features) if isinstance(p.features, str) else p.features
                        except Exception:
                            features = []
                        result.append({
                            "name": p.name,
                            "price": p.price,
                            "sale_price": float(p.price.replace("RM", "").replace(",", "").strip()) if p.price else 0.0,
                            "regular_price": p.regular_price,
                            "category": p.category,
                            "capacity": p.capacity,
                            "material": p.material,
                            "colors": colors,
                            "features": features,
                            "collection": p.collection,
                            "promotion": p.promotion,
                            "on_sale": p.on_sale == "True" if p.on_sale is not None else False,
                            "description": p.description,
                            "price_numeric": float(p.price.replace("RM", "").replace(",", "").strip()) if p.price else None
                        })
                    logger.info(f"Loaded {len(result)} products from database")
                    return result
            
            # Try file loader if database not available
            if FILE_LOADER_AVAILABLE and load_products_from_file:
                logger.info("Database not available, loading products from file")
                return load_products_from_file()
            
            # Ultimate fallback if both fail
            raise Exception("Both database and file loader unavailable")
            
        except Exception as e:
            logger.error(f"Error in get_products: {e}")
            # Fallback: return a minimal hardcoded product list
            return [
                {
                    "name": "ZUS OG CUP 2.0 With Screw-On Lid 500ml",
                    "price": "RM 55.00",
                    "sale_price": 55.0,
                    "regular_price": "RM 79.00",
                    "category": "Tumbler",
                    "capacity": "500ml",
                    "material": "Stainless Steel",
                    "colors": ["Thunder Blue", "Space Black", "Lucky Pink"],
                    "features": ["Screw-on lid", "Double-wall insulation", "Leak-proof design"],
                    "collection": "OG",
                    "promotion": None,
                    "on_sale": True,
                    "description": "The iconic ZUS OG Cup 2.0 with improved screw-on lid design",
                    "price_numeric": 55.0
                },
                {
                    "name": "ZUS All-Can Tumbler 600ml",
                    "price": "RM 105.00",
                    "sale_price": 105.0,
                    "regular_price": None,
                    "category": "Tumbler",
                    "capacity": "600ml",
                    "material": "Stainless Steel",
                    "colors": ["Thunder Blue", "Stainless Steel"],
                    "features": ["Car cup holder friendly", "Double-wall insulation"],
                    "collection": "All-Can",
                    "promotion": "Buy 1 Free 1",
                    "on_sale": False,
                    "description": "Universal tumbler that fits perfectly in your car cup holder",
                    "price_numeric": 105.0
                }
            ]

    def get_outlets(self) -> List[Dict]:
        """Fetch all outlets from the database as dicts. Always returns a safe fallback if DB is down."""
        try:
            # Try database first if available
            if DATABASE_AVAILABLE and SessionLocal and Outlet:
                with SessionLocal() as db:
                    outlets = db.query(Outlet).all()
                    result = []
                    for o in outlets:
                        # Parse JSON fields if needed
                        services = []
                        try:
                            if o.services:
                                services = json.loads(o.services) if isinstance(o.services, str) else o.services
                        except Exception:
                            services = []
                        result.append({
                            "name": o.name,
                            "address": o.address,
                            "hours": o.opening_hours,
                            "services": services
                        })
                    logger.info(f"Loaded {len(result)} outlets from database")
                    return result
            
            # Try file loader if database not available
            if FILE_LOADER_AVAILABLE and load_outlets_from_file:
                logger.info("Database not available, loading outlets from file")
                return load_outlets_from_file()
            
            # Ultimate fallback if both fail
            raise Exception("Both database and file loader unavailable")
            
        except Exception as e:
            logger.error(f"Error in get_outlets: {e}")
            # Fallback: return a minimal hardcoded outlet list
            return [
                {
                    "name": "ZUS Coffee KLCC",
                    "address": "Suria KLCC, Level 4, Kuala Lumpur City Centre, 50088 Kuala Lumpur",
                    "hours": "8:00 AM - 10:00 PM",
                    "services": ["Dine-in", "Takeaway", "Delivery", "WiFi"]
                },
                {
                    "name": "ZUS Coffee Pavilion KL",
                    "address": "Pavilion Kuala Lumpur, Level 6, 168 Jalan Bukit Bintang, 55100 Kuala Lumpur",
                    "hours": "10:00 AM - 10:00 PM",
                    "services": ["Dine-in", "Takeaway", "Delivery", "WiFi"]
                },
                {
                    "name": "ZUS Coffee Mid Valley",
                    "address": "Mid Valley Megamall, Level 3, Lingkaran Syed Putra, 59200 Kuala Lumpur",
                    "hours": "10:00 AM - 10:00 PM",
                    "services": ["Dine-in", "Takeaway", "Delivery"]
                },
                {
                    "name": "ZUS Coffee Shah Alam",
                    "address": "No 5 Ground Floor, Jalan Eserina AA U16/AA, 40150 Shah Alam, Selangor",
                    "hours": "8:00 AM - 10:00 PM",
                    "services": ["Dine-in", "Takeaway", "Delivery"]
                }
            ]

    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get or create session context with memory storage."""
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
        """Update session context with current turn data."""
        context = self.get_session_context(session_id)
        context["count"] += 1
        
        # Only update last_intent for actual user intents, not status messages
        actual_intents = ["greeting", "product_search", "outlet_search", "calculation", 
                         "promotion_inquiry", "collection_inquiry", "eco_friendly", "farewell", "follow_up", "general"]
        if intent in actual_intents:
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
        Intent parsing and action planning system.
        
        Analyzes user input to determine intent and plan appropriate response actions.
        Handles multiple intents and determines missing information for follow-up questions.
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
        
        # FIRST: Enhanced context-aware follow-up detection (highest priority)
        if context["last_intent"] and context["count"] >= 1:
            # Check for location-based follow-ups
            if context["last_intent"] == "outlet_search":
                # Handle "What about [location]?" follow-ups
                if any(phrase in message_lower for phrase in ["what about", "how about", "what of"]):
                    intent_scores["outlet_search"] = 0.98
                # Handle pronoun references to outlets
                elif any(pronoun in message_lower for pronoun in ["they", "them", "it", "those"]):
                    if any(service in message_lower for service in ["dine-in", "takeaway", "delivery", "wifi", "parking", "hours", "services"]):
                        intent_scores["outlet_search"] = 0.98
                # Handle location names (SS15, areas, etc.)
                elif any(location in message_lower for location in ["ss15", "ss2", "damansara", "bangsar", "pj", "klcc"]):
                    intent_scores["outlet_search"] = 0.98
            
            # Check for product-based follow-ups
            elif context["last_intent"] == "product_search":
                if any(pronoun in message_lower for pronoun in ["they", "them", "it", "those"]):
                    intent_scores["product_search"] = 0.98
            
            # General follow-up patterns
            if any(word in message_lower for word in ["more", "details", "other", "else", "also"]):
                intent_scores["follow_up"] = 0.7

        # Calculate intent confidence scores with better priority handling
        greeting_words = ["hello", "hi", "hey", "good morning", "good afternoon", "welcome"]
        # Use word boundaries to avoid substring matches (e.g., "hi" in "this")
        import re
        has_greeting = any(re.search(r'\b' + re.escape(word) + r'\b', message_lower) for word in greeting_words)
        if has_greeting:
            intent_scores["greeting"] = 0.9
        
        # Check for irrelevant queries first to avoid false positives
        irrelevant_keywords = ['weather', 'politics', 'sports', 'news', 'movie', 'music', 'game', 'cooking', 'recipe', 'travel', 'job', 'work', 'school', 'study', 'homework', 'dating', 'relationship', 'fashion', 'clothes', 'car', 'house', 'rent', 'insurance', 'health', 'medicine', 'doctor', 'hospital']
        if any(keyword in message_lower for keyword in irrelevant_keywords):
            intent_scores["general"] = 0.95  # Mark as general for special handling
            
        # Outlet search detection - PRIORITIZE outlet intent over product intent with better keywords
        outlet_keywords = ["outlet", "outlets", "location", "locations", "store", "stores", "branch", "branches", 
                          "hours", "address", "where", "near", "klcc", "find", "nearest", "seating",
                          "opening hours", "open", "close", "timing", "contact", "phone", "services",
                          "pavilion", "mid valley", "sunway", "shah alam", "kl", "kuala lumpur", "petaling jaya", "pj"]
        outlet_exclusive_keywords = ["outlet", "outlets", "location", "locations", "store", "stores", "branch", "branches",
                                    "hours", "opening hours", "address", "where", "find outlet", "find location"]
        
        # Service-specific outlet queries (these should get high priority)
        service_specific_patterns = [
            "drive-thru", "drive thru", "wifi", "wi-fi", "delivery", "dine-in", "takeaway", 
            "24 hours", "24/7", "parking", "service", "services"
        ]
        has_service_query = any(service in message_lower for service in service_specific_patterns)
        
        # Check for outlet-specific queries first
        has_outlet_exclusive = any(word in message_lower for word in outlet_exclusive_keywords)
        has_outlet_keyword = any(word in message_lower for word in outlet_keywords)
        
        # Enhanced outlet detection with service priority
        if has_outlet_exclusive or (has_outlet_keyword and not any(word in message_lower for word in ["product", "tumbler", "cup", "mug", "drinkware"])):
            if has_service_query:
                intent_scores["outlet_search"] = 0.99  # HIGHEST priority for service-specific outlet searches
            else:
                intent_scores["outlet_search"] = 0.98  # Very high priority for general outlet searches
            
        # Product search detection - enhanced with better category detection
        product_keywords = ["product", "products", "tumbler", "tumblers", "cup", "cups", "mug", "mugs", 
                           "drinkware", "collection", "show me", "what products", "drinks", "coffee", 
                           "best-selling", "cheapest", "food", "items", "all products", "all tumblers",
                           "cold cup", "cold cups", "stainless steel", "acrylic", "ceramic", "bottle", "bottles",
                           "what kind", "buy", "purchase", "get", "available", "sell", "have"]
        
        # Only classify as product search if not clearly outlet-related
        if any(word in message_lower for word in product_keywords) and intent_scores["outlet_search"] < 0.5:
            intent_scores["product_search"] = 0.85
            
        # Price/filtering related queries - should be product search, not calculation or promotion
        if any(phrase in message_lower for phrase in ["priced between", "under rm", "cost under", "price difference", "compare prices", "cheapest", "most expensive"]):
            intent_scores["product_search"] = 0.95  # Higher priority than promotion_inquiry
            
        # Material + price queries should definitely be product search
        material_keywords = ["ceramic", "stainless steel", "acrylic", "glass", "steel"]
        price_keywords = ["cheapest", "most expensive", "cheap", "expensive", "price", "cost"]
        if any(mat in message_lower for mat in material_keywords) and any(price in message_lower for price in price_keywords):
            intent_scores["product_search"] = 0.98  # Very high priority
            
        # Enhanced calculation detection - distinguish between pure math and product calculations
        calculation_keywords = ["math", "compute", "plus", "minus", "times", "divided by", "power", "square root", "percent", "percentage"]
        calculation_operators = any(op in message for op in ['+', '-', '*', '/', '×', '÷', '='])
        calculation_patterns = (re.search(r'\d+\s*[\+\-\*\/\×\÷\^]\s*\d+', message) or
                              re.search(r'\d+\s*(?:to\s+the\s+power\s+of|[\^\*]{2}|\^)\s*\d+', message_lower) or
                              re.search(r'(?:square\s+root|sqrt)\s+of\s+\d+', message_lower) or
                              re.search(r'\d+\s*%\s*of\s*\d+', message_lower))
        
        # Tax/SST calculations - pure calculation intent
        if any(keyword in message_lower for keyword in ["sst", "tax", "service charge"]) and re.search(r'\d+', message):
            intent_scores["calculation"] = 0.95
        
        # Product-related calculations (cost, total, pricing) - should be product search, not calculation
        has_product_calc_keywords = any(word in message_lower for word in ["cost", "total", "price", "calculate total", "calculate cost", "calculate price"])
        has_product_keywords = any(word in message_lower for word in ["product", "tumbler", "cup", "drink", "coffee", "cappuccino", "latte", "americano", "croissant", "meal", "combo"])
        
        # Only classify as pure calculation if it's clearly mathematical and doesn't involve products
        if has_product_calc_keywords and has_product_keywords:
            intent_scores["product_search"] = 0.9  # Product calculation queries go to product search
        elif (calculation_operators or any(word in message_lower for word in calculation_keywords) or calculation_patterns):
            # Check if it's a pure math query without product context
            has_non_math_keywords = any(word in message_lower for word in ["product", "outlet", "tumbler", "cup", "drink", "location", "store", "find", "show", "cheapest", "expensive"])
            if not has_non_math_keywords:
                intent_scores["calculation"] = 0.9
        elif message_lower.startswith(("what is", "compute")) and calculation_operators and not has_product_keywords:
            intent_scores["calculation"] = 0.95  # Strong calculation intent for explicit requests
            
        # Enhanced promotion inquiry detection - BUT NOT for specific product queries
        promotion_keywords = ["promotion", "promotions", "sale", "sales", "discount", "discounts", "offer", "offers", 
                             "deal", "deals", "special", "specials", "new", "latest", "month", "today", "available",
                             "what's new", "whats new", "this month", "current", "ongoing"]
        
        # Check if this is a specific product query (cheapest, most expensive, specific product name)
        is_specific_product_query = any(term in message_lower for term in ["cheapest", "most expensive", "ceramic", "stainless steel", "acrylic", "tumbler", "cup", "mug", "show me", "find"])
        
        if any(word in message_lower for word in promotion_keywords) and not is_specific_product_query:
            # Boost score for explicit promotion queries
            if any(explicit in message_lower for explicit in ["promotion", "promotions", "deal", "deals", "offer", "offers", "discount"]):
                intent_scores["promotion_inquiry"] = 0.98  # Higher than product_search
            # Medium score for implicit promotion queries
            elif any(implicit in message_lower for implicit in ["new", "latest", "month", "today", "available", "special"]):
                intent_scores["promotion_inquiry"] = 0.92  # Higher than product_search
            
        if any(word in message_lower for word in ["eco-friendly", "sustainable", "environment"]):
            intent_scores["eco_friendly"] = 0.8
            
        if any(word in message_lower for word in ["thank", "thanks", "bye", "goodbye"]):
            intent_scores["farewell"] = 0.9
            
        # Smart fallback detection - if confidence is too low, try to detect from context
        max_confidence = max(intent_scores.values())
        if max_confidence < 0.5:
            # Check for implicit product queries
            if any(word in message_lower for word in ["new", "best", "top", "expensive", "cheap", "size", "combo", "meal", "family"]):
                intent_scores["product_search"] = 0.6
            # Check for implicit outlet queries  
            elif any(word in message_lower for word in ["capacity", "seating", "largest", "count", "how many"]) and ("outlet" in message_lower or "coffee" in message_lower):
                intent_scores["outlet_search"] = 0.6
            # Check for promotions/general ZUS queries
            elif any(word in message_lower for word in ["promotion", "new", "month", "today", "available"]):
                intent_scores["promotion_inquiry"] = 0.6
        
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
            # Check if this is specifically asking for all products (not filtered queries)
            if ("all products" in message_lower or "show me products" in message_lower) and not any(phrase in message_lower for phrase in ["under", "above", "between", "cheap", "expensive", "price", "rm"]):
                action_plan["action"] = "show_all_products"
            elif not any(keyword in message_lower for keyword_list in self.product_keywords.values() for keyword in keyword_list):
                action_plan["missing_info"].append("specific_product_type")
                action_plan["follow_up_needed"] = True
                
        elif intent_name == "outlet_search":
            # Check for specific service or location queries before deciding to show all
            filters = self.detect_filtering_intent(message)
            if ("all outlets" in message_lower or "show all outlets" in message_lower) and not (filters.get("city") or filters.get("service")):
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
        """Find products with enhanced logic and filtering using real DB data."""
        products = self.get_products()
        if not products:  # Handle case where products is None or empty
            return []
        
        if show_all:
            return products
            
        query_lower = query.lower()
        filters = self.detect_filtering_intent(query)
        
        # Start with all products
        matching_products = products

        # --- Improved: Apply material filter before product type for accuracy ---
        filters = self.detect_filtering_intent(query)
        if filters["material"]:
            matching_products = [p for p in matching_products if filters["material"] in p.get("material", "").lower()]

        # Now apply product type filter (e.g., mug, cup, tumbler)
        product_type_keywords = {
            "mug": ["mug"],
            "cup": ["cup"],
            "tumbler": ["tumbler"]
        }
        for product_type, keywords in product_type_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                matching_products = [p for p in matching_products if any(keyword in p.get("name", "").lower() for keyword in keywords)]
                break
        
        # Apply filters if specified
        if filters["price_range"] or filters["category"] or filters["material"] or filters["collection"]:
            if filters["price_range"]:
                min_p, max_p = filters.get("min_price"), filters.get("max_price")
                price_filtered = []
                for p in matching_products:
                    price = p.get("sale_price", 0)
                    if price > 0:  # Only consider products with valid prices
                        if (min_p is None or price >= min_p) and (max_p is None or price <= max_p):
                            price_filtered.append(p)
                matching_products = price_filtered
            
            if filters["category"]:
                matching_products = [p for p in matching_products 
                                   if p.get("category", "").lower() == filters["category"]]
            
            if filters["material"]:
                matching_products = [p for p in matching_products 
                                   if filters["material"] in p.get("material", "").lower()]
            
            if filters["collection"]:
                matching_products = [p for p in matching_products 
                                   if filters["collection"] in (p.get("collection", "") or "").lower()]
            
            # Sort by price for better organization
            matching_products.sort(key=lambda p: p.get("sale_price", 0))
            
            # Handle price-based queries AFTER filtering by material/category/collection
            if any(term in query_lower for term in ["cheapest", "cheap", "lowest price", "least expensive"]):
                # Return cheapest matching products
                return matching_products[:3]  # Return top 3 cheapest that match filters
            elif any(term in query_lower for term in ["most expensive", "expensive", "highest price", "priciest"]):
                # Return most expensive matching products
                return sorted(matching_products, key=lambda p: p.get("sale_price", 0), reverse=True)[:3]
            
            return matching_products
        
        # Handle price-based queries (cheapest, most expensive, etc.) WITHOUT specific filters
        if any(term in query_lower for term in ["cheapest", "cheap", "lowest price", "least expensive"]):
            # Sort by price ascending and return cheapest products
            sorted_products = sorted(matching_products, key=lambda p: p.get("sale_price", 0))
            return sorted_products[:3]  # Return top 3 cheapest
        
        if any(term in query_lower for term in ["most expensive", "expensive", "highest price", "priciest"]):
            # Sort by price descending and return most expensive products
            sorted_products = sorted(matching_products, key=lambda p: p.get("sale_price", 0), reverse=True)
            return sorted_products[:3]  # Return top 3 most expensive
        
        # Handle specific category searches
        category_terms = {
            "tumbler": "drinkware",
            "tumblers": "drinkware", 
            "cup": "drinkware",
            "cups": "drinkware",
            "mug": "drinkware",
            "mugs": "drinkware",
            "drinkware": "drinkware",
            "cold cup": "drinkware",
            "cold cups": "drinkware"
        }
        
        # Check if this is a category-specific search
        for term, category in category_terms.items():
            if term in query_lower and len(query_lower.split()) <= 3:
                # Return all products in this category
                return [p for p in products if p.get("category", "").lower() == category]
        
        # General queries that should return all products
        general_product_terms = ["products", "what products", "show me products", "available", "all products", "show all", "show products"]
        if any(term in query_lower for term in general_product_terms):
            return products
        
        # Handle AI-based keyword matching with fuzzy search
        result = []
        
        # Smart keyword matching - look for any word that could be a product feature
        query_words = [w for w in query_lower.split() if len(w) > 2]
        
        for product in products:
            product_name_lower = (product.get("name", "") or "").lower()
            product_description = (product.get("description", "") or "").lower()
            product_material = (product.get("material", "") or "").lower()
            product_collection = (product.get("collection", "") or "").lower()
            product_colors = [c.lower() for c in product.get("colors", [])]
            product_features = [f.lower() for f in product.get("features", [])]
            
            # Check if any query word matches product attributes
            match_found = False
            for query_word in query_words:
                if (query_word in product_name_lower or 
                    query_word in product_description or
                    query_word in product_material or
                    query_word in product_collection or
                    any(query_word in color for color in product_colors) or
                    any(query_word in feature for feature in product_features)):
                    match_found = True
                    break
            
            if match_found:
                result.append(product)
        
        # Remove duplicates
        seen = set()
        unique_products = []
        for product in result:
            if product.get("name") not in seen:
                seen.add(product.get("name"))
                unique_products.append(product)

        # If no specific matches found but query contains general terms, return all products
        if not unique_products and any(term in query_lower for term in ["show", "display", "list", "available"]):
            return products
        
        # STRICT: If no matches for specific product names, return empty (no hallucination)
        if not unique_products and any(len(w) > 4 for w in query_words):
            return []
        
        return unique_products

    def find_matching_outlets(self, query: str, show_all: bool = False) -> List[Dict]:
        """Find outlets with enhanced logic and city filtering using real DB data."""
        outlets = self.get_outlets()
        if not outlets:  # Handle case where outlets is None or empty
            return []
        
        if show_all:
            return outlets
            
        query_lower = query.lower()
        filters = self.detect_filtering_intent(query)
          # Apply filtering in sequence: first city, then service
        filtered_outlets = outlets
        
        # Apply location/city filtering first if specified
        if filters["city"]:
            city = filters["city"]
            # Only match if city is present as a whole word in the address (not as a substring)
            city_filtered = []
            for o in filtered_outlets:
                address = (o.get("address", "") or "").lower()
                # Strict: match city as a whole word, or as a substring with clear boundaries (space, comma, start/end)
                if (
                    address == city
                    or address.startswith(city + ' ')
                    or address.endswith(' ' + city)
                    or f' {city} ' in address
                    or f',{city} ' in address
                    or f' {city},' in address
                    or f',{city},' in address
                    or address.endswith(',' + city)
                    or address.startswith(city + ',')
                    or city in [w.strip() for w in address.replace(',', ' ').replace('-', ' ').split()]
                ):
                    city_filtered.append(o)
            # STRICT: If no outlets match the city, return empty
            if not city_filtered:
                return []
            filtered_outlets = city_filtered

        # Apply service filtering on the already filtered results (IMPROVED: Better service matching)
        if filters["service"]:
            service_to_find = filters["service"]
            service_filtered = []
            for o in filtered_outlets:  # Apply to already filtered results
                outlet_services = o.get("services", [])
                # Check if the requested service matches any of the outlet's services
                service_match = False
                for outlet_service in outlet_services:
                    if outlet_service and service_to_find.lower() in outlet_service.lower():
                        service_match = True
                        break
                    # Special cases for common service terms
                    elif service_to_find == "wifi" and outlet_service and "wifi" in outlet_service.lower():
                        service_match = True
                        break
                    elif service_to_find == "drive-thru" and outlet_service and ("drive" in outlet_service.lower() or "thru" in outlet_service.lower()):
                        service_match = True
                        break
                
                if service_match:
                    service_filtered.append(o)
            
            # Return filtered results (could be empty if no service matches)
            filtered_outlets = service_filtered
        
        # Return the filtered results (if any filters were applied)
        if filters["city"] or filters["service"]:
            return filtered_outlets
        
        # General outlet queries - return all outlets (BUT NOT if specific filters are present)
        general_outlet_terms = ["all outlets", "show outlets", "show all outlets", 
                               "outlet locations", "list outlets", "find outlets"]
        # Check for very specific "show all" patterns that shouldn't be filtered
        show_all_patterns = ["all outlets", "show all outlets", "list all outlets", "outlet locations"]
        
        # Only return all outlets if:
        # 1. Query matches show-all patterns AND no specific filters, OR
        # 2. Query is generic like "where" or "branches" with no filters
        if ((any(term in query_lower for term in show_all_patterns) and not (filters["city"] or filters["service"])) or
            (any(term in query_lower for term in ["where", "branches", "stores"]) and not (filters["city"] or filters["service"]) and len(query_lower.split()) <= 2)):
            return outlets
        
        # Hours/timing queries - return all outlets with hours info
        timing_terms = ["hours", "open", "close", "timing", "opening hours", "what time"]
        if any(term in query_lower for term in timing_terms):
            return outlets
        
        # Specific outlet name or location matching
        result = []
        for outlet in outlets:
            outlet_name_lower = (outlet.get("name", "") or "").lower()
            outlet_address_lower = (outlet.get("address", "") or "").lower()
            outlet_services = outlet.get("services", [])
            
            # Split names and addresses into words for better matching
            outlet_words = outlet_name_lower.replace('-', ' ').split()
            address_words = outlet_address_lower.replace(',', ' ').replace('-', ' ').split()
            
            # Check if query matches outlet name, address, or services
            if (any(word in query_lower for word in outlet_words if len(word) > 2) or
                any(word in query_lower for word in address_words if len(word) > 3) or
                any((service or "").lower() in query_lower for service in outlet_services)):
                result.append(outlet)
                continue
        
        # Remove duplicates
        seen = set()
        unique_outlets = []
        for outlet in result:
            if outlet.get("name") not in seen:
                seen.add(outlet.get("name"))
                unique_outlets.append(outlet)

        # STRICT: If no matches, return empty (no hallucination, no fallback)
        if not unique_outlets:
            return []
        return unique_outlets

    def handle_advanced_calculation(self, message: str) -> str:
        """
        Advanced calculator with error handling and SST/Tax support.
        Handles: basic math, percentages, square roots, powers, tax calculations
        Never hallucinates - only works with real mathematical expressions.
        """
        try:
            # Normalize multiplication and division symbols and strip currency symbols for calculation
            original_message = message
            message = message.replace('×', '*').replace('÷', '/')
            
            # Remove RM symbols for calculation but remember if they were present
            has_currency = 'rm' in message.lower() or 'ringgit' in message.lower()
            message = re.sub(r'\bRM\s*', '', message, flags=re.IGNORECASE)
            
            # Check for natural language division by zero first
            if re.search(r'(?:divided|divide)\s+by\s+(?:zero|0)', message.lower()):
                return "Error: Cannot divide by zero. Please adjust your calculation and try again."
            
            # Extract mathematical expressions with strict validation
            math_pattern = r'[\d\+\-\*\/\(\)\.\s%×÷]+'
            expressions = re.findall(math_pattern, message)
            
            # Security check - reject non-mathematical queries (NO DUMMY DATA)
            non_math_terms = ["banana", "apple", "fruit", "product", "outlet", "coffee", "zus", "cappuccino", "latte", "americano", "croissant", "muffin", "sandwich", "cookie", "cake", "tumbler", "cup", "mug", "drinkware"]
            if any(term in message.lower() for term in non_math_terms):
                return "I can only calculate mathematical expressions with numbers and operators (+, -, *, /). I don't calculate combinations of products or non-mathematical items. For product information, please ask me to show you our available products."
            
            # Handle percentage calculations (e.g., "15% of 200")
            percentage_match = re.search(r'(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)', message.lower())
            if percentage_match:
                percent, number = float(percentage_match.group(1)), float(percentage_match.group(2))
                result = (percent / 100) * number
                if has_currency:
                    return f"Here's your percentage calculation: **{percent}% of RM {number} = RM {result:.2f}**. Need more calculations or ZUS Coffee information?"
                else:
                    return f"Here's your percentage calculation: **{percent}% of {number} = {result:.2f}**. Need more calculations or ZUS Coffee information?"
            
            # Handle square root (e.g., "square root of 25")
            sqrt_match = re.search(r'square\s+root\s+of\s+(\d+(?:\.\d+)?)', message.lower())
            if sqrt_match:
                number = float(sqrt_match.group(1))
                result = math.sqrt(number)
                return f"Here's your square root calculation: **√{number} = {result:.2f}**. Need more calculations?"
            
            # Handle powers (e.g., "2 to the power of 3" or "2^3")
            power_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:to\s+the\s+power\s+of|[\^\*]{2}|\^)\s*(\d+(?:\.\d+)?)', message.lower())
            if power_match:
                base, exponent = float(power_match.group(1)), float(power_match.group(2))
                result = base ** exponent
                return f"Here's your power calculation: **{base}^{exponent} = {result:.2f}**. Need more calculations?"
            
            # Handle SST/Tax calculations (check for tax keywords BEFORE general calculation)
            if any(keyword in original_message.lower() for keyword in self.tax_keywords):
                return self.handle_tax_calculation(original_message)
            
            if not expressions:
                return "I couldn't find a mathematical expression in your message. Please provide numbers and operators like '25 + 15', '(100 * 2) - 50', or '200 / 4'."
            
            # Take the longest valid expression
            expression = max(expressions, key=len).strip()
            
            # Strict security validation - only mathematical characters (including × ÷)
            safe_chars = set('0123456789+-*/().,=×÷ ')
            if not all(c in safe_chars for c in expression):
                return "For security reasons, I can only calculate expressions with numbers and basic operators (+, -, *, /, ×, ÷, parentheses). Please try again."
            
            # Clean and validate expression - normalize symbols
            expression = expression.replace('=', '').replace(' ', '').replace('×', '*').replace('÷', '/')
            if not expression or not re.match(r'^[\d\+\-\*\/\(\)\.]+$', expression):
                return "Please provide a valid mathematical expression using numbers and operators. For example: '25.5 + 18.2' or '(100 - 20) * 3'."
            
            # Check for division by zero before evaluation
            if re.search(r'/\s*0(?:\s|$|\+|\-|\*|/|\))', expression + ' ') or expression.endswith('/0'):
                return "Error: Cannot divide by zero. Please adjust your calculation and try again."
            
            # Safe evaluation with error handling
            try:
                result = eval(expression)
                
                # Validate result
                if not isinstance(result, (int, float)) or math.isnan(result) or math.isinf(result):
                    return "That calculation resulted in an invalid number. Please check your expression and try again."
                
                # Enhanced result formatting with currency detection
                original_expression = expression
                
                # Check if the original message contained RM to format as currency
                has_currency = 'rm' in message.lower() or 'ringgit' in message.lower()
                
                # Format result appropriately
                if isinstance(result, float):
                    if result.is_integer():
                        result_display = int(result)
                    else:
                        result_display = f"{result:.2f}"
                else:
                    result_display = result
                
                # Add currency formatting if detected
                if has_currency:
                    return f"Here's your calculation: **{original_expression} = RM {result_display}**. Need more calculations or ZUS Coffee information?"
                else:
                    return f"Here's your calculation: **{original_expression} = {result_display}**. Need more calculations or ZUS Coffee information?"
                
            except ZeroDivisionError:
                return "Error: Cannot divide by zero. Please adjust your calculation and try again."
            except Exception as calc_error:
                return f"I couldn't calculate that expression. Please check your math syntax. Error: {str(calc_error)[:50]}"
                
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            return "I'm having trouble with that calculation. Please try a simpler mathematical expression like '25 + 15' or '100 / 4'."

    def handle_tax_calculation(self, message: str) -> str:
        """Handle SST/tax calculations for Malaysian pricing"""
        try:
            # Extract price from message
            price_match = re.search(r'(\d+(?:\.\d+)?)', message)
            if not price_match:
                return "Please specify a price amount for tax calculation. Example: 'Calculate tax for RM 100' or 'What's the SST on 50?'"
            
            price = float(price_match.group(1))
            
            # Determine tax type
            if 'sst' in message.lower():
                tax_rate = self.tax_rates['sst']
                tax_name = "SST"
            elif 'service' in message.lower():
                tax_rate = self.tax_rates['service']
                tax_name = "Service Charge"
            else:
                tax_rate = self.tax_rates['sst']  # Default to SST
                tax_name = "SST"
            
            tax_amount = price * tax_rate
            total = price + tax_amount
            
            return f"**Tax Calculation:** Subtotal: RM {price:.2f} | {tax_name} ({tax_rate*100:.0f}%): RM {tax_amount:.2f} | **Total: RM {total:.2f}**. Malaysia's current SST is 6% on goods and services."
            
        except Exception as e:
            return "I couldn't calculate the tax. Please try: 'Calculate SST for RM 100' or 'What's the tax on 50?'"
    
    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Message processing with state management and error handling.
        Implements conversation memory, intent detection, tool integration, and API calls.
        """
        # Initialize session context
        try:
            context = self.get_session_context(session_id)
            message_lower = str(message).lower().strip() if message is not None else ""
            # Store message in context without overriding last_intent
            context["last_message"] = message
        except Exception as e:
            return {
                "message": "Sorry, I'm having trouble keeping track of your session. Please try again later.",
                "session_id": session_id,
                "intent": "unknown",
                "error": str(e)
            }

        # Security and malicious input filtering
        try:
            dangerous_words = ["drop", "delete", "script", "sql", "injection", "hack", "admin"]
            # Don't flag "root" as it might be in "square root"
            if any(word in message_lower for word in dangerous_words):
                self.update_session_context(session_id, "security_violation", {"message": message})
                return {
                    "message": "For security reasons, I cannot process requests containing potentially harmful content. I'm here to help with ZUS Coffee products, outlets, calculations, and general inquiries. How can I assist you today?",
                    "session_id": session_id,
                    "intent": "general_chat",
                    "confidence": 0.99
                }
        except Exception:
            pass

        # Handle empty or short messages
        try:
            if not message_lower or len(message_lower) < 2:
                self.update_session_context(session_id, "clarification", {"message": message})
                return {
                    "message": "I'd love to help you! I can assist with outlet locations and hours, product recommendations and details, pricing calculations, or general ZUS Coffee information. What interests you most?",
                    "session_id": session_id,
                    "intent": "help",
                    "confidence": 0.7
                }
        except Exception:
            pass

        # Intent parsing and action planning
        try:
            action_plan = self.parse_intent_and_plan_action(message, session_id)
            # Store the detected intent for context continuity (regardless of execution result)
            detected_intent = action_plan["intent"]
        except Exception as e:
            self.update_session_context(session_id, "intent_parse_error", {"message": message, "error": str(e)})
            return {
                "message": "Sorry, I couldn't understand your request. Please try rephrasing or ask about ZUS Coffee products, outlets, or calculations.",
                "session_id": session_id,
                "intent": "unknown",
                "error": str(e)
            }

        # Multi-intent detection and handling
        try:
            product_intent = action_plan["intent"] == "product_search" or action_plan.get("action") == "show_all_products"
            outlet_intent = action_plan["intent"] == "outlet_search" or action_plan.get("action") == "show_all_outlets"
            calc_intent = action_plan["intent"] == "calculation" and action_plan.get("requires_tool")

            has_product_kw = any(kw in message_lower for kw in ["product", "tumbler", "cup", "mug", "drinkware"])
            has_outlet_kw = any(kw in message_lower for kw in ["outlet", "location", "store", "branch", "address"])
            # Improved calculation detection to avoid false positives from hyphens in words
            has_calc_operators = any(op in message for op in ['+', '*', '/', '=']) or any(f' {op} ' in message for op in ['-']) or any(kw in message_lower for kw in ['calculate', 'math'])
            has_calc_kw = has_calc_operators or any(kw in message_lower for kw in self.math_keywords)
            multi_intent = (has_product_kw and has_outlet_kw) or (has_product_kw and has_calc_kw) or (has_outlet_kw and has_calc_kw)

            if multi_intent:
                response_parts = []
                # Product answer
                try:
                    if has_product_kw:
                        matching_products = self.find_matching_products(message, show_all=True)
                        if matching_products:
                            response_parts.append(self.format_product_response(matching_products, session_id, message))
                        else:
                            response_parts.append("Sorry, I couldn't find any products matching your request.")
                except Exception:
                    response_parts.append("Sorry, there was an error fetching product info.")
                # Outlet answer
                try:
                    if has_outlet_kw:
                        matching_outlets = self.find_matching_outlets(message, show_all=True)
                        if matching_outlets:
                            response_parts.append(self.format_outlet_response(matching_outlets, session_id, message))
                        else:
                            response_parts.append("Sorry, I couldn't find any outlets matching your request.")
                except Exception:
                    response_parts.append("Sorry, there was an error fetching outlet info.")
                # Calculation answer
                try:
                    if has_calc_kw:
                        result = self.handle_advanced_calculation(message)
                        response_parts.append(result)
                except Exception:
                    response_parts.append("Sorry, I couldn't complete the calculation due to an error.")
                
                self.update_session_context(session_id, "multi_intent", {"message": message})
                return {
                    "message": "\n\n".join(response_parts),
                    "session_id": session_id,
                    "intent": "general_chat",
                    "confidence": 0.95
                }
        except Exception:
            pass

        # Calculator integration
        if calc_intent:
            try:
                result = self.handle_advanced_calculation(message)
                self.update_session_context(session_id, "calculation", {"expression": message, "result": result})
                return {
                    "message": result,
                    "session_id": session_id,
                    "intent": "calculation",
                    "confidence": action_plan["confidence"]
                }
            except Exception as e:
                self.update_session_context(session_id, "calculation_error", {"expression": message, "error": str(e)})
                return {
                    "message": "Sorry, I couldn't complete the calculation due to an error. Please check your input or try again later.",
                    "session_id": session_id,
                    "intent": "calculation",
                    "confidence": 0.2
                }

        # Product search processing
        if product_intent:
            try:
                show_all = action_plan.get("action") == "show_all_products" or ("all products" in message_lower and not any(phrase in message_lower for phrase in ["under", "above", "between", "cheap", "expensive", "price", "rm"]))
                matching_products = self.find_matching_products(message, show_all=show_all)
                if not matching_products:
                    self.update_session_context(session_id, "no_product_results", {"query": message})
                    return {
                        "message": "Sorry, I couldn't find any products matching your request. Please try a different query or ask about our drinkware collection!",
                        "session_id": session_id,
                        "intent": "product_search",
                        "confidence": 0.3
                    }
                response = self.format_product_response(matching_products, session_id, message)
                self.update_session_context(session_id, "product_search", {"query": message, "results_count": len(matching_products)})
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "product_search",
                    "confidence": action_plan["confidence"]
                }
            except Exception as e:
                self.update_session_context(session_id, "product_search_error", {"query": message, "error": str(e)})
                return {
                    "message": "Sorry, there was an error fetching product information. Please try again later.",
                    "session_id": session_id,
                    "intent": "product_search",
                    "confidence": 0.1,
                    "error": str(e)
                }

        # Outlet search processing
        if outlet_intent:
            try:
                # Check if this should show all outlets (only if no specific filters)
                filters = self.detect_filtering_intent(message)
                show_all = (action_plan.get("action") == "show_all_outlets" or 
                           ("all outlets" in message_lower or "show all outlet" in message_lower)) and not (filters.get("city") or filters.get("service"))
                matching_outlets = self.find_matching_outlets(message, show_all=show_all)
                if (filters.get("city") and not matching_outlets) or not matching_outlets:
                    self.update_session_context(session_id, "no_outlet_results", {"query": message})
                    return {
                        "message": "Sorry, I couldn't find any outlets matching your request. Please try a different location or ask about our outlets in KL or Selangor!",
                        "session_id": session_id,
                        "intent": "outlet_search",
                        "confidence": 0.3
                    }
                response = self.format_outlet_response(matching_outlets, session_id, message)
                self.update_session_context(session_id, "outlet_search", {"query": message, "results_count": len(matching_outlets)})
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "outlet_search",
                    "confidence": action_plan["confidence"]
                }
            except Exception as e:
                self.update_session_context(session_id, "outlet_search_error", {"query": message, "error": str(e)})
                return {
                    "message": "Sorry, there was an error fetching outlet information. Please try again later.",
                    "session_id": session_id,
                    "intent": "outlet_search",
                    "error": str(e)
                }

        # Greeting
        if action_plan["intent"] == "greeting":
            try:
                response = "Hello and welcome to ZUS Coffee! I'm your AI assistant ready to help you explore our drinkware collection, find outlet locations with hours and services, calculate pricing including SST/tax, or answer questions about ZUS Coffee. What would you like to know today?"
                self.update_session_context(session_id, "greeting", {"message": message})
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "greeting",
                    "confidence": action_plan["confidence"]
                }
            except Exception as e:
                return {
                    "message": "Hello! Welcome to ZUS Coffee!",
                    "session_id": session_id,
                    "intent": "greeting",
                    "error": str(e)
                }

        # Farewell
        if action_plan["intent"] == "farewell":
            try:
                response = "Thank you for choosing ZUS Coffee! Have a wonderful day and we look forward to serving you again soon. Don't forget to check out our latest products and visit our outlets!"
                self.update_session_context(session_id, "farewell", {"message": message})
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "goodbye",
                    "confidence": action_plan["confidence"]
                }
            except Exception as e:
                return {
                    "message": "Thank you for choosing ZUS Coffee!",
                    "session_id": session_id,
                    "intent": "goodbye",
                    "error": str(e)
                }

        # Promotion Inquiry
        if action_plan["intent"] == "promotion_inquiry":
            try:
                response = "🎉 **Current ZUS Coffee Promotions & What's New:**\n\n"
                response += "• **Featured Products:** Check out our latest drinkware collections including the ZUS All-Can Tumbler and ZUS Frozee Cold Cup series!\n"
                response += "• **Special Bundles:** Corak Malaysia Tiga Sekawan Bundle at RM 133.90\n"
                response += "• **Limited Edition:** Mountain Collection and Aqua Collection All Day Cups\n"
                response += "• **Eco-Friendly Options:** Sustainable tumblers and reusable cups for environmentally conscious coffee lovers\n\n"
                response += "For the latest promotions and seasonal offers, visit our outlets or check our official channels. I can also help you find specific products or calculate pricing including SST!"
                
                self.update_session_context(session_id, "promotion_inquiry", {"message": message})
                return {
                    "message": response,
                    "session_id": session_id,
                    "intent": "general_chat",
                    "confidence": action_plan["confidence"]
                }
            except Exception as e:
                return {
                    "message": "I'd be happy to help you learn about ZUS Coffee's current promotions and new products! Please try asking again or let me know what specific products interest you.",
                    "session_id": session_id,
                    "intent": "general_chat",
                    "error": str(e)
                }

        # Default fallback for unmatched queries
        try:
            # Check if it's completely irrelevant (weather, politics, etc.)
            irrelevant_keywords = ['weather', 'politics', 'sports', 'news', 'movie', 'music', 'game', 'cooking', 'recipe', 'travel', 'job', 'work', 'school', 'study', 'homework', 'dating', 'relationship', 'fashion', 'clothes', 'car', 'house', 'rent', 'insurance', 'health', 'medicine', 'doctor', 'hospital']
            if any(keyword in message_lower for keyword in irrelevant_keywords):
                return {
                    "message": "I'm your ZUS Coffee assistant, specialized in helping with our drinkware products, outlet locations, and pricing calculations. I can help you with:\n\n🥤 **Product Info:** 'Show all products', 'cheapest tumbler', 'stainless steel cups'\n🏪 **Outlet Locations:** 'ZUS outlets in KL', 'opening hours', 'drive-thru locations'\n🧮 **Calculations:** 'Calculate 25 + 15', 'What's 6% SST on RM100?'\n\nHow can I help you with ZUS Coffee today?",
                    "session_id": session_id,
                    "intent": "general_chat",
                    "confidence": 0.8
                }
            
            # Check if it looks like a product query that we should suggest alternatives for
            if any(word in message_lower for word in ['product', 'item', 'buy', 'purchase', 'show', 'display', 'available']):
                return {
                    "message": "I can help you explore our ZUS Coffee collection! Try asking:\n\n🥤 **Show Products:** 'Show all products' (see all 11 items)\n💰 **By Price:** 'Cheapest products', 'Most expensive products', 'Products under RM50'\n🎨 **By Collection:** 'Sundaze collection', 'Aqua collection', 'Mountain collection'\n🔧 **By Material:** 'Stainless steel tumblers', 'Ceramic mugs', 'Acrylic cups'\n\nWhat would you like to explore?",
                    "session_id": session_id,
                    "intent": "product_search",
                    "confidence": 0.7
                }
            
            # Check if it looks like an outlet query
            if any(word in message_lower for word in ['outlet', 'location', 'store', 'branch', 'where', 'address', 'find']):
                return {
                    "message": "I can help you find ZUS Coffee outlets! Try asking:\n\n📍 **All Outlets:** 'Show all outlets', 'ZUS locations'\n🏙️ **By Area:** 'Outlets in KL', 'Outlets in Selangor', 'Outlets in PJ'\n🕐 **Operating Hours:** 'Opening hours', 'What time do you open?'\n🚗 **Services:** 'Drive-thru outlets', 'Outlets with parking', 'WiFi locations'\n\nWhat location information do you need?",
                    "session_id": session_id,
                    "intent": "outlet_search",
                    "confidence": 0.7
                }
            
            # Check if it looks like a calculation that wasn't caught
            if any(op in message for op in ['+', '-', '*', '/', '×', '÷', '=']) or any(word in message_lower for word in ["calculate", "math", "compute", "what is", "percent", "percentage", "of", "sst", "tax"]):
                try:
                    result = self.handle_advanced_calculation(message)
                    self.update_session_context(session_id, "calculation_fallback", {"expression": message, "result": result})
                    return {
                        "message": result,
                        "session_id": session_id,
                        "intent": "calculation",
                        "confidence": 0.7
                    }
                except Exception:
                    pass
            
            self.update_session_context(session_id, "general", {"message": message})
            return {
                "message": "I'm your ZUS Coffee assistant! I can help you with:\n\n🥤 **Products:** 'Show all products', 'Cheapest tumbler', 'Stainless steel cups'\n🏪 **Outlets:** 'Find outlets in KL', 'Opening hours', 'Drive-thru locations'\n🧮 **Calculations:** 'Calculate 25 + 15', 'What's 6% SST on RM100?'\n\nTry asking about our products, outlet locations, or any calculations you need!",
                "session_id": session_id,
                "intent": "general_chat",
                "confidence": 0.5
            }
        except Exception as e:
            return {
                "message": "Sorry, I'm having technical difficulties. Please try again later.",
                "session_id": session_id,
                "intent": "unknown",
                "error": str(e)
            }
    
    def detect_filtering_intent(self, query: str) -> Dict[str, Any]:
        """
        Detect filtering intent from user query (price range, category, material, etc.)
        Returns dict with filter criteria
        """
        query_lower = query.lower()
        filters = {
            "price_range": False,
            "min_price": None,
            "max_price": None,
            "category": None,
            "material": None,
            "collection": None,
            "city": None,
            "service": None
        }
        
        # Enhanced price range detection with better patterns
        import re
        
        # Pattern for "under RM50", "below RM100", "less than RM75"
        under_pattern = r'(?:under|below|less than|<|cheaper than|lower than)\s*rm?\s*(\d+(?:\.\d+)?)'
        # Pattern for "above RM50", "over RM100", "more than RM75"  
        over_pattern = r'(?:above|over|more than|>|expensive than|higher than)\s*rm?\s*(\d+(?:\.\d+)?)'
        # Pattern for "RM50 to RM100", "RM50-RM100", "between RM50 and RM100"
        range_pattern = r'(?:rm?\s*(\d+(?:\.\d+)?)\s*(?:to|-|and)\s*rm?\s*(\d+(?:\.\d+)?)|between\s*rm?\s*(\d+(?:\.\d+)?)\s*and\s*rm?\s*(\d+(?:\.\d+)?))'
        
        # Check for price ranges
        under_match = re.search(under_pattern, query_lower)
        over_match = re.search(over_pattern, query_lower)
        range_match = re.search(range_pattern, query_lower)
        
        if under_match:
            filters["price_range"] = True
            filters["max_price"] = float(under_match.group(1))
        elif over_match:
            filters["price_range"] = True
            filters["min_price"] = float(over_match.group(1))
        elif range_match:
            filters["price_range"] = True
            if range_match.group(1) and range_match.group(2):
                filters["min_price"] = float(range_match.group(1))
                filters["max_price"] = float(range_match.group(2))
            elif range_match.group(3) and range_match.group(4):
                filters["min_price"] = float(range_match.group(3))
                filters["max_price"] = float(range_match.group(4))
        
        # Material detection with better matching
        materials = {
            'stainless steel': ['stainless steel', 'stainless', 'steel', 'metal'],
            'ceramic': ['ceramic', 'porcelain'],
            'acrylic': ['acrylic', 'plastic'],
            'glass': ['glass']
        }
        
        for material_key, material_terms in materials.items():
            if any(term in query_lower for term in material_terms):
                filters["material"] = material_key
                break
        
        # Collection detection - updated with correct collections from products.json
        collections = {
            'sundaze': ['sundaze', 'sun daze'],
            'aqua': ['aqua', 'ocean', 'blue'],
            'mountain': ['mountain', 'forest', 'green', 'nature'],
            'kopi patah hati': ['kopi patah hati', 'patah hati', 'sabrina', 'olivia'],
            'corak malaysia': ['corak malaysia', 'corak', 'malaysia', 'malaysian']
        }
        
        for collection_key, collection_terms in collections.items():
            if any(term in query_lower for term in collection_terms):
                filters["collection"] = collection_key
                break
        
        # Enhanced city detection for outlets (more specific matching)
        cities = {
            'kuala lumpur': ['kuala lumpur', 'kl '],  # More specific to avoid false matches
            'petaling jaya': ['petaling jaya', 'pj '],
            'selangor': ['selangor', 'shah alam'],
            'cheras': ['cheras'],  # Added Cheras as it appears in outlet data
            'ampang': ['ampang'],  # Added Ampang 
            'sentul': ['sentul'],  # Added Sentul
            'wangsa maju': ['wangsa maju'],  # Added Wangsa Maju
            'putrajaya': ['putrajaya']  # Added Putrajaya
        }
        
        for city_key, city_terms in cities.items():
            if any(term in query_lower for term in city_terms):
                filters["city"] = city_key
                break
        
        # Enhanced service detection for outlets
        services = {
            'drive-thru': ['drive-thru', 'drive thru', 'drive through', 'drive'],
            'dine-in': ['dine-in', 'dine in', 'dining', 'eat in'],
            'takeaway': ['takeaway', 'take away', 'pickup', 'take out'],
            '24 hours': ['24 hours', '24/7', '24 hour', 'all night', 'late night'],
            'wifi': ['wifi', 'wi-fi', 'internet', 'wireless'],
            'parking': ['parking', 'park', 'car park'],
            'delivery': ['delivery', 'deliver', 'food delivery']
        }
        
        for service_key, service_terms in services.items():
            if any(term in query_lower for term in service_terms):
                filters["service"] = service_key
                break
        
        return filters
        
    def extract_product_price(self, product: Dict) -> float:
        """Extract price from product data with fallback logic"""
        try:
            # Try sale_price first
            if "sale_price" in product and product["sale_price"]:
                return float(product["sale_price"])
            
            # Try to parse price string
            if "price" in product and product["price"]:
                price_str = product["price"]
                if isinstance(price_str, str):
                    # Remove "RM " and convert to float
                    price_clean = price_str.replace("RM ", "").replace(",", "").strip()
                    return float(price_clean)
                elif isinstance(price_str, (int, float)):
                    return float(price_str)
            
            # If no price found, return 0
            return 0.0
            
        except (ValueError, TypeError):
            return 0.0

    def format_product_response(self, products: List[Dict], session_id: str, query: str) -> str:
        """Format product search results into a user-friendly response"""
        try:
            if not products:
                return "I couldn't find any products matching your request. Try asking about our available drinkware, tumblers, cups, mugs, or ask me to 'show all products' to see our complete collection!"
            
            # Check if this is a calculation query (e.g., "Calculate total cost for 2 Cappuccino")
            query_lower = query.lower()
            is_calculation_query = any(keyword in query_lower for keyword in ["calculate", "total", "cost", "price", "how much"])
            
            # Extract quantities from calculation queries
            quantity_matches = re.findall(r'(\d+)\s*([a-zA-Z\s]+)', query)
            requested_items = {}
            
            if is_calculation_query and quantity_matches:
                # Try to match quantities with product names
                for qty_str, item_name in quantity_matches:
                    qty = int(qty_str)
                    item_name = item_name.strip().lower()
                    
                    # Find matching products
                    for product in products:
                        product_name = product.get("name", "").lower()
                        if any(word in product_name for word in item_name.split()) or item_name in product_name:
                            unit_price = product.get("sale_price", 0)
                            if unit_price > 0:  # Only include products with valid prices
                                requested_items[product["name"]] = {
                                    "quantity": qty,
                                    "product": product,
                                    "unit_price": unit_price
                                }
                            break
                
                # If we found matching items, provide calculation
                if requested_items:
                    return self.format_calculation_response(requested_items, query)
            
            # Check for "show all products" requests - display all 11 products
            if any(term in query_lower for term in ["show all", "all products", "show products", "list all"]):
                max_display = len(products)  # Show all products
            else:
                # Regular product listing - show more products for drinkware queries
                max_display = 8 if any(term in query_lower for term in ["drinkware", "tumbler", "cup", "all"]) else 5
            
            display_products = products[:max_display]
            
            response_parts = []
            
            # Check what type of query this is
            is_category_query = any(term in query_lower for term in ["tumbler", "tumblers", "cup", "cups", "drinkware", "mug", "mugs"])
            is_collection_query = any(term in query_lower for term in ["sundaze", "aqua", "corak", "mountain", "kopi patah hati"])
            is_price_query = any(term in query_lower for term in ["cheap", "expensive", "price", "cost", "rm", "under", "above", "cheapest", "most expensive"])
            
            # Customize header based on query type
            if any(term in query_lower for term in ["show all", "all products", "show products", "list all"]):
                response_parts.append(f"**Here are all {len(products)} products in our ZUS Coffee collection:**\n")
            elif is_price_query:
                if "cheap" in query_lower or "cheapest" in query_lower:
                    response_parts.append(f"**Here are our most affordable products ({len(products)} item{'s' if len(products) != 1 else ''}):**\n")
                elif "expensive" in query_lower or "most expensive" in query_lower:
                    response_parts.append(f"**Here are our premium products ({len(products)} item{'s' if len(products) != 1 else ''}):**\n")
                else:
                    response_parts.append(f"**Products matching your price criteria ({len(products)} item{'s' if len(products) != 1 else ''}):**\n")
            elif is_category_query:
                category_name = "drinkware"
                if "tumbler" in query_lower:
                    category_name = "tumblers"
                elif "cup" in query_lower:
                    category_name = "cups"
                elif "mug" in query_lower:
                    category_name = "mugs"
                response_parts.append(f"**Here are our {category_name} ({len(products)} item{'s' if len(products) != 1 else ''}):**\n")
            elif is_collection_query:
                response_parts.append(f"**Products from our collections ({len(products)} item{'s' if len(products) != 1 else ''}):**\n")
            else:
                response_parts.append(f"**Found {len(products)} product{'s' if len(products) != 1 else ''} matching your request:**\n")
            
            for i, product in enumerate(display_products, 1):
                name = product.get("name", "Unknown Product")
                price = product.get("price", "Price not available")
                sale_price = product.get("sale_price", 0)
                category = product.get("category", "")
                capacity = product.get("capacity", "")
                material = product.get("material", "")
                colors = product.get("colors", [])
                features = product.get("features", [])
                promotion = product.get("promotion")
                on_sale = product.get("on_sale", False)
                regular_price = product.get("regular_price")
                collection = product.get("collection", "")
                
                # Format product info with better layout
                product_info = f"**{i}. {name}**\n"
                
                # Price with sale indicator
                if on_sale and regular_price:
                    product_info += f"💰 **Price:** {price} ~~{regular_price}~~ 🔥 **ON SALE!**\n"
                elif promotion:
                    product_info += f"💰 **Price:** {price} 🎁 **{promotion}**\n"
                else:
                    product_info += f"💰 **Price:** {price}\n"
                
                # Essential details
                if capacity:
                    product_info += f"📏 **Capacity:** {capacity}\n"
                if material:
                    product_info += f"🔧 **Material:** {material}\n"
                if collection:
                    product_info += f"🎨 **Collection:** {collection}\n"
                if colors:
                    colors_text = ", ".join(colors[:3])  # Show first 3 colors
                    if len(colors) > 3:
                        colors_text += f" (+{len(colors)-3} more)"
                    product_info += f"� **Colors:** {colors_text}\n"
                if features:
                    features_text = ", ".join(features[:2])  # Show first 2 features
                    if len(features) > 2:
                        features_text += f" (+{len(features)-2} more)"
                    product_info += f"✨ **Features:** {features_text}\n"
                
                response_parts.append(product_info)
            
            if len(products) > max_display:
                response_parts.append(f"\n... and {len(products) - max_display} more products available! Ask me to 'show all products' to see everything.")
            
            # Add helpful footer based on query type
            if is_price_query:
                response_parts.append("\n **Price Tips:** Ask me about 'cheapest products', 'most expensive products', or 'products under RM50' for better filtering!")
            elif is_category_query:
                response_parts.append("\n **Category Tips:** Try asking about specific collections like 'Sundaze', 'Aqua', 'Mountain', or 'Kopi Patah Hati'!")
            elif any(term in query_lower for term in ["show all", "all products"]):
                response_parts.append("\n **Complete Collection:** This is our entire drinkware collection! Need help choosing? Ask about specific features, prices, or collections.")
            else:
                response_parts.append("\n **Need more details?** Ask me about specific products, collections, price ranges, or say 'show all products' to see everything!")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Error formatting product response: {e}")
            return "I found some products but encountered an error displaying them. Please try again or ask for specific product information."

    def format_calculation_response(self, requested_items: Dict, query: str) -> str:
        """Format calculation response for product orders"""
        try:
            if not requested_items:
                # If no specific products found in our database, don't provide dummy data
                return "I can only calculate prices for products we have in our ZUS Coffee collection. Please ask me to show you our available products first, or try searching for specific items like 'tumbler', 'cup', or 'mug'."
            
            response_parts = []
            response_parts.append("**Order Calculation:**\n")
            
            subtotal = 0
            for product_name, item_info in requested_items.items():
                qty = item_info["quantity"]
                price = item_info["unit_price"]
                line_total = qty * price
                subtotal += line_total
                
                response_parts.append(f"• {qty}x {product_name} @ RM {price:.2f} = RM {line_total:.2f}")
            
            # Add tax calculation (6% SST)
            tax_rate = 0.06
            tax_amount = subtotal * tax_rate
            total = subtotal + tax_amount
            
            response_parts.append(f"\n**Subtotal:** RM {subtotal:.2f}")
            response_parts.append(f"**SST (6%):** RM {tax_amount:.2f}")
            response_parts.append(f"**Total:** RM {total:.2f}")
            
            response_parts.append("\nPrices may vary by location. Visit your nearest ZUS Coffee outlet for the most accurate pricing!")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Error formatting calculation response: {e}")
            return "I found the products but encountered an error calculating the total. Please try again."

    def handle_product_calculation_fallback(self, query: str) -> str:
        """Handle calculation queries for products not in our database - NO DUMMY DATA"""
        return "I can only calculate prices for products we have in our ZUS Coffee collection. Our current inventory includes drinkware items like tumblers, cups, and mugs. Please ask me to show you our available products first, or search for specific items we carry."

    def format_outlet_response(self, outlets: List[Dict], session_id: str, query: str) -> str:
        """Format outlet search results into a user-friendly response with complete outlet data"""
        try:
            if not outlets:
                return "Sorry, I couldn't find any outlets matching your request. Please try a different location or ask about our outlets in KL, Selangor, or Petaling Jaya!"
            
            # Limit to top 8 outlets for better readability
            display_outlets = outlets[:8]
            
            response_parts = []
            
            # Check if this is a specific query for hours/services
            query_lower = query.lower()
            is_hours_query = any(term in query_lower for term in ["hours", "open", "close", "timing", "what time"])
            is_services_query = any(term in query_lower for term in ["service", "services", "drive-thru", "wifi", "parking", "delivery"])
            
            if len(outlets) == 1:
                response_parts.append(f"**Here's the outlet information:**\n")
            else:
                response_parts.append(f"**Found {len(outlets)} outlet{'s' if len(outlets) != 1 else ''} for you:**\n")
            
            for i, outlet in enumerate(display_outlets, 1):
                name = outlet.get("name", "ZUS Coffee Outlet")
                address = outlet.get("address", "Address not available")
                hours = outlet.get("hours", "Hours not available")
                services = outlet.get("services", [])
                
                # Format outlet information with complete data
                outlet_info = f"**{i}. {name}**\n"
                outlet_info += f"📍 **Address:** {address}\n"
                outlet_info += f"🕐 **Operating Hours:** {hours}\n"
                
                if services:
                    # Format services nicely
                    services_text = ", ".join(services)
                    outlet_info += f"🏪 **Services:** {services_text}\n"
                else:
                    outlet_info += f"🏪 **Services:** Please contact outlet for service details\n"
                
                # Add phone/contact if available (though not in current data structure)
                if outlet.get("phone"):
                    outlet_info += f"📞 **Contact:** {outlet.get('phone')}\n"
                
                response_parts.append(outlet_info)
            
            if len(outlets) > 8:
                response_parts.append(f"\n... and {len(outlets) - 8} more outlets available! Ask me for more specific locations.")
            
            # Add helpful footer based on query type
            if is_hours_query:
                response_parts.append("\n💡 **Note:** Operating hours may vary during holidays and special events. Please call ahead to confirm.")
            elif is_services_query:
                response_parts.append("\n💡 **Tip:** Services may vary by location. Contact the outlet directly for the most up-to-date information.")
            else:
                response_parts.append("\n💡 **Need more info?** Ask me about operating hours, services, or directions to any outlet!")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Error formatting outlet response: {e}")
            return "I found some outlets but encountered an error displaying them. Please try again or ask for specific outlet information."

# Singleton pattern for agent instance
_agent_instance = None

def get_chatbot():
    """Get the enhanced minimal agent instance (singleton pattern)."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = EnhancedMinimalAgent()
    return _agent_instance
