#!/usr/bin/env python3
"""
File-based Data Loader for ZUS Coffee Chatbot
Loads products and outlets from JSON files and SQLite when database is not available
"""

import json
import sqlite3
import os
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class FileDataLoader:
    """Load data from local files when database is not available"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent
        self.products_file = self.data_dir / "products.json"
        self.outlets_db = self.data_dir / "outlets.db"
        
    def get_products(self) -> List[Dict[str, Any]]:
        """Load products from JSON file with error handling"""
        try:
            if not self.products_file.exists():
                logger.warning(f"Products file not found: {self.products_file}")
                return self._get_fallback_products()
                
            with open(self.products_file, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
                
            # Process products to ensure consistent format
            processed_products = []
            for product in products_data:
                try:
                    processed_product = {
                        "name": product.get("name", "Unknown Product"),
                        "price": product.get("price", "RM 0.00"),
                        "sale_price": product.get("sale_price", 0.0),  # Add sale_price field
                        "regular_price": product.get("regular_price"),
                        "category": product.get("category", "Drinkware"),
                        "capacity": product.get("capacity", ""),
                        "material": product.get("material", ""),
                        "colors": product.get("colors", []),
                        "features": product.get("features", []),
                        "collection": product.get("collection"),
                        "promotion": product.get("promotion"),
                        "on_sale": product.get("on_sale", False),
                        "description": product.get("description", ""),
                        "price_numeric": self._extract_numeric_price(product.get("price", "RM 0.00"))
                    }
                    processed_products.append(processed_product)
                except Exception as e:
                    logger.warning(f"Error processing product: {e}")
                    continue
                    
            logger.info(f"Loaded {len(processed_products)} products from JSON file")
            return processed_products
            
        except Exception as e:
            logger.error(f"Error loading products from file: {e}")
            return self._get_fallback_products()
    
    def get_outlets(self) -> List[Dict[str, Any]]:
        """Load outlets from SQLite database with error handling"""
        try:
            if not self.outlets_db.exists():
                logger.warning(f"Outlets database not found: {self.outlets_db}")
                return self._get_fallback_outlets()
                
            conn = sqlite3.connect(str(self.outlets_db))
            cursor = conn.cursor()
            
            # Query outlets
            cursor.execute("SELECT name, address, opening_hours, services FROM outlets")
            outlets_data = cursor.fetchall()
            conn.close()
            
            # Process outlets to ensure consistent format
            processed_outlets = []
            for outlet_row in outlets_data:
                try:
                    name, address, hours, services = outlet_row
                    
                    # Parse services string to list
                    services_list = []
                    if services:
                        services_list = [s.strip() for s in services.split(',')]
                    
                    processed_outlet = {
                        "name": name or "ZUS Coffee Outlet",
                        "address": address or "Address not available",
                        "hours": hours or "Hours not available",
                        "services": services_list
                    }
                    processed_outlets.append(processed_outlet)
                except Exception as e:
                    logger.warning(f"Error processing outlet: {e}")
                    continue
            
            logger.info(f"Loaded {len(processed_outlets)} outlets from SQLite database")
            return processed_outlets
            
        except Exception as e:
            logger.error(f"Error loading outlets from database: {e}")
            return self._get_fallback_outlets()
    
    def _extract_numeric_price(self, price_str: str) -> float:
        """Extract numeric price from price string"""
        try:
            if not price_str:
                return 0.0
            # Remove "RM" and any commas, convert to float
            numeric_str = price_str.replace("RM", "").replace(",", "").strip()
            return float(numeric_str)
        except (ValueError, AttributeError):
            return 0.0
    
    def _get_fallback_products(self) -> List[Dict[str, Any]]:
        """Fallback products when file loading fails"""
        return [
            {
                "name": "ZUS OG CUP 2.0 With Screw-On Lid 500ml",
                "price": "RM 55.00",
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
            },
            {
                "name": "ZUS Sundaze Cold Cup 500ml",
                "price": "RM 55.00",
                "regular_price": "RM 79.00",
                "category": "Cold Cup",
                "capacity": "500ml",
                "material": "Acrylic",
                "colors": ["Sunny Yellow", "Ocean Blue", "Sunset Orange"],
                "features": ["Bright colors", "Summer vibes", "Perfect for cold drinks"],
                "collection": "Sundaze",
                "promotion": None,
                "on_sale": True,
                "description": "Bright and vibrant colors inspired by sunny days",
                "price_numeric": 55.0
            }
        ]
    
    def _get_fallback_outlets(self) -> List[Dict[str, Any]]:
        """Fallback outlets when database loading fails"""
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
                "name": "ZUS Coffee Sunway Pyramid",
                "address": "Sunway Pyramid, Level LG2, 3 Jalan PJS 11/15, 47500 Petaling Jaya, Selangor",
                "hours": "10:00 AM - 10:00 PM",
                "services": ["Dine-in", "Takeaway", "Delivery", "WiFi"]
            },
            {
                "name": "ZUS Coffee Shah Alam",
                "address": "No 5 Ground Floor, Jalan Eserina AA U16/AA, 40150 Shah Alam, Selangor",
                "hours": "8:00 AM - 10:00 PM",
                "services": ["Dine-in", "Takeaway", "Delivery"]
            }
        ]

# Global instance
_file_loader = None

def get_file_data_loader():
    """Get file data loader instance (singleton)"""
    global _file_loader
    if _file_loader is None:
        _file_loader = FileDataLoader()
    return _file_loader

def load_products_from_file() -> List[Dict[str, Any]]:
    """Convenience function to load products"""
    return get_file_data_loader().get_products()

def load_outlets_from_file() -> List[Dict[str, Any]]:
    """Convenience function to load outlets"""
    return get_file_data_loader().get_outlets()
