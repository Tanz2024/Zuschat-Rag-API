#!/usr/bin/env python3
"""
Database seeder for ZUS Coffee chatbot
Populates PostgreSQL database with real product and outlet data from files
"""

import json
import sqlite3
import logging
from typing import List, Dict
from sqlalchemy.orm import Session
from backend.data.database import SessionLocal, Product, Outlet, engine, Base

logger = logging.getLogger(__name__)

class DatabaseSeeder:
    """Seeds PostgreSQL database with real ZUS Coffee data"""
    
    def __init__(self):
        self.session = None
    
    def load_products_from_json(self) -> List[Dict]:
        """Load products from JSON file"""
        try:
            with open('backend/data/products.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading products.json: {e}")
            return []
    
    def load_outlets_from_sqlite(self) -> List[Dict]:
        """Load outlets from SQLite database"""
        try:
            conn = sqlite3.connect('backend/data/outlets.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name, address, opening_hours, services FROM outlets")
            
            outlets = []
            for row in cursor.fetchall():
                name, address, hours, services = row
                outlets.append({
                    'name': name,
                    'address': address,
                    'opening_hours': hours,
                    'services': services
                })
            
            conn.close()
            return outlets
        except Exception as e:
            logger.error(f"Error loading outlets.db: {e}")
            return []
    
    def seed_products(self, session: Session) -> int:
        """Seed products table"""
        products_data = self.load_products_from_json()
        if not products_data:
            logger.warning("No products data found")
            return 0
        
        # Clear existing products
        session.query(Product).delete()
        
        count = 0
        for product_data in products_data:
            try:
                # Convert lists to JSON strings for database storage
                colors_json = json.dumps(product_data.get('colors', []))
                features_json = json.dumps(product_data.get('features', []))
                
                product = Product(
                    name=product_data.get('name', ''),
                    category=product_data.get('category', ''),
                    price=product_data.get('price', 'RM 0.00'),
                    sale_price=str(product_data.get('sale_price', '')),
                    regular_price=product_data.get('regular_price'),
                    description=product_data.get('description'),
                    capacity=product_data.get('capacity'),
                    material=product_data.get('material'),
                    colors=colors_json,
                    features=features_json,
                    collection=product_data.get('collection'),
                    promotion=product_data.get('promotion'),
                    on_sale=str(product_data.get('on_sale', False)),
                    discount=product_data.get('discount')
                )
                session.add(product)
                count += 1
            except Exception as e:
                logger.error(f"Error adding product {product_data.get('name', 'Unknown')}: {e}")
                continue
        
        session.commit()
        logger.info(f"Seeded {count} products")
        return count
    
    def seed_outlets(self, session: Session) -> int:
        """Seed outlets table"""
        outlets_data = self.load_outlets_from_sqlite()
        if not outlets_data:
            logger.warning("No outlets data found")
            return 0
        
        # Clear existing outlets
        session.query(Outlet).delete()
        
        count = 0
        for outlet_data in outlets_data:
            try:
                outlet = Outlet(
                    name=outlet_data.get('name', ''),
                    address=outlet_data.get('address', ''),
                    opening_hours=outlet_data.get('opening_hours', ''),
                    services=outlet_data.get('services', '')
                )
                session.add(outlet)
                count += 1
            except Exception as e:
                logger.error(f"Error adding outlet {outlet_data.get('name', 'Unknown')}: {e}")
                continue
        
        session.commit()
        logger.info(f"Seeded {count} outlets")
        return count
    
    def seed_database(self) -> Dict[str, int]:
        """Seed the entire database"""
        if not engine:
            logger.error("Database engine not configured")
            return {"error": "Database not configured"}
        
        try:
            # Create tables
            Base.metadata.create_all(bind=engine)
            
            # Seed data
            with SessionLocal() as session:
                products_count = self.seed_products(session)
                outlets_count = self.seed_outlets(session)
                
                return {
                    "products_seeded": products_count,
                    "outlets_seeded": outlets_count,
                    "status": "success"
                }
        
        except Exception as e:
            logger.error(f"Database seeding failed: {e}")
            return {"error": str(e)}

def seed_render_database():
    """Main function to seed Render PostgreSQL database"""
    seeder = DatabaseSeeder()
    result = seeder.seed_database()
    
    if "error" in result:
        print(f"Seeding failed: {result['error']}")
    else:
        print(f"Database seeded successfully!")
        print(f"   Products: {result['products_seeded']}")
        print(f"   Outlets: {result['outlets_seeded']}")
    
    return result
