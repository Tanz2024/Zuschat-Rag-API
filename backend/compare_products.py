#!/usr/bin/env python3
"""
Compare products between JSON and PostgreSQL
"""
import json
from dotenv import load_dotenv
load_dotenv()

from data.database import SessionLocal, Product

def compare_products():
    """Compare products between JSON and database"""
    
    # Load from JSON
    with open('data/products.json', 'r', encoding='utf-8') as f:
        json_products = json.load(f)
    
    print(f"📁 Products in JSON file: {len(json_products)}")
    print("JSON Products:")
    for i, product in enumerate(json_products, 1):
        print(f"   {i}. {product['name']}")
    
    # Load from database
    with SessionLocal() as db:
        db_products = db.query(Product).all()
        print(f"\n🗄️ Products in PostgreSQL: {len(db_products)}")
        print("Database Products:")
        for i, product in enumerate(db_products, 1):
            print(f"   {i}. {product.name}")
    
    # Check for differences
    json_names = {p['name'] for p in json_products}
    db_names = {p.name for p in db_products}
    
    if json_names == db_names:
        print(f"\n✅ All products match between JSON and database!")
    else:
        print(f"\n❌ Mismatch detected:")
        if json_names - db_names:
            print(f"Missing in DB: {json_names - db_names}")
        if db_names - json_names:
            print(f"Extra in DB: {db_names - json_names}")

if __name__ == "__main__":
    compare_products()
