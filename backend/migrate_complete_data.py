#!/usr/bin/env python3
"""
Complete Migration script for ZUS Coffee data
Migrates outlets from SQLite and products from JSON to PostgreSQL
"""
import sqlite3
import json
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Load environment variables from .env file
load_dotenv()

from data.database import engine, create_tables, Outlet, Product, SessionLocal

def migrate_outlets_from_sqlite():
    """Migrate outlet data from SQLite to PostgreSQL"""
    sqlite_db_path = os.path.join(os.path.dirname(__file__), "data", "outlets.db")
    
    if not os.path.exists(sqlite_db_path):
        print("❌ SQLite database not found, skipping outlet migration")
        return 0
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    cursor = sqlite_conn.cursor()
    
    # Get outlet data from SQLite
    cursor.execute("SELECT name, address, opening_hours, services FROM outlets")
    sqlite_outlets = cursor.fetchall()
    sqlite_conn.close()
    
    if not sqlite_outlets:
        print("❌ No outlets found in SQLite database")
        return 0
    
    print(f"Found {len(sqlite_outlets)} outlets in SQLite database")
    
    # Insert into PostgreSQL
    with SessionLocal() as db:
        # Clear existing outlets
        db.query(Outlet).delete()
        
        for outlet_data in sqlite_outlets:
            outlet = Outlet(
                name=outlet_data[0],
                address=outlet_data[1],
                opening_hours=outlet_data[2],
                services=outlet_data[3]
            )
            db.add(outlet)
        
        db.commit()
        print(f"✅ Successfully migrated {len(sqlite_outlets)} outlets to PostgreSQL")
    
    return len(sqlite_outlets)

def migrate_products_from_json():
    """Migrate product data from JSON to PostgreSQL"""
    products_file = os.path.join(os.path.dirname(__file__), "data", "products.json")
    
    if not os.path.exists(products_file):
        print("❌ Products JSON file not found, skipping product migration")
        return 0
    
    # Load products from JSON
    with open(products_file, 'r', encoding='utf-8') as f:
        products_data = json.load(f)
    
    if not products_data:
        print("❌ No products found in JSON file")
        return 0
    
    print(f"Found {len(products_data)} products in JSON file")
    
    # Insert into PostgreSQL
    with SessionLocal() as db:
        # Clear existing products
        db.query(Product).delete()
        
        for product_data in products_data:
            # Convert arrays to JSON strings if they exist
            features_str = None
            if 'features' in product_data and product_data['features']:
                features_str = json.dumps(product_data['features'])
            
            colors_str = None  
            if 'colors' in product_data and product_data['colors']:
                colors_str = json.dumps(product_data['colors'])
            
            product = Product(
                name=product_data['name'],
                category=product_data['category'],
                price=product_data['price'],
                sale_price=str(product_data.get('sale_price', '')),
                regular_price=product_data.get('regular_price', ''),
                description=product_data.get('description', ''),
                ingredients=product_data.get('ingredients', ''),
                capacity=product_data.get('capacity', ''),
                material=product_data.get('material', ''),
                colors=colors_str,
                features=features_str,
                collection=product_data.get('collection', ''),
                promotion=product_data.get('promotion', ''),
                on_sale=str(product_data.get('on_sale', False)),
                discount=product_data.get('discount', '')
            )
            db.add(product)
        
        db.commit()
        print(f"✅ Successfully migrated {len(products_data)} products to PostgreSQL")
    
    return len(products_data)

def verify_migration():
    """Verify the migration was successful"""
    with SessionLocal() as db:
        outlet_count = db.query(Outlet).count()
        product_count = db.query(Product).count()
        
        print(f"\n📊 Migration Verification:")
        print(f"   ✅ Outlets in PostgreSQL: {outlet_count}")
        print(f"   ✅ Products in PostgreSQL: {product_count}")
        
        if outlet_count > 0:
            # Show sample outlets
            sample_outlets = db.query(Outlet).limit(2).all()
            print(f"\n📍 Sample Outlets:")
            for outlet in sample_outlets:
                print(f"   • {outlet.name}")
        
        if product_count > 0:
            # Show sample products
            sample_products = db.query(Product).limit(3).all()
            print(f"\n🛍️ Sample Products:")
            for product in sample_products:
                print(f"   • {product.name} ({product.category}) - {product.price}")

def main():
    """Main migration function"""
    print("🚀 ZUS Coffee Complete Data Migration to PostgreSQL")
    print("=" * 60)
    
    # Create PostgreSQL tables
    print("Creating PostgreSQL tables...")
    create_tables()
    print("✅ Tables created successfully")
    
    # Migrate outlets
    print("\n📍 Migrating outlets...")
    outlets_migrated = migrate_outlets_from_sqlite()
    
    # Migrate products
    print("\n🛍️ Migrating products...")
    products_migrated = migrate_products_from_json()
    
    # Verify migration
    verify_migration()
    
    print(f"\n🎉 Migration Complete!")
    print(f"   📍 {outlets_migrated} outlets migrated")
    print(f"   🛍️ {products_migrated} products migrated")
    print(f"\n🗄️ Your Render PostgreSQL database now contains all ZUS Coffee data!")

if __name__ == "__main__":
    main()
