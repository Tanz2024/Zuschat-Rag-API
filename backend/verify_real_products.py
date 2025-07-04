#!/usr/bin/env python3
"""
Verify real ZUS Coffee products in PostgreSQL
"""
from dotenv import load_dotenv
load_dotenv()

from data.database import SessionLocal, Product
import json

def verify_real_products():
    """Verify real product data in PostgreSQL"""
    with SessionLocal() as db:
        # Count total products
        total_products = db.query(Product).count()
        print(f"🛍️ Total products in PostgreSQL: {total_products}")
        
        # Show all products with details
        products = db.query(Product).all()
        
        print(f"\n📋 All Real ZUS Coffee Products:")
        print("=" * 80)
        
        for i, product in enumerate(products, 1):
            print(f"\n{i}. {product.name}")
            print(f"   Category: {product.category}")
            print(f"   Price: {product.price} (Sale: {product.sale_price})")
            if product.regular_price:
                print(f"   Regular Price: {product.regular_price}")
            print(f"   Capacity: {product.capacity}")
            print(f"   Material: {product.material}")
            
            # Parse colors JSON
            if product.colors:
                try:
                    colors = json.loads(product.colors)
                    print(f"   Colors: {', '.join(colors)}")
                except:
                    pass
            
            # Parse features JSON  
            if product.features:
                try:
                    features = json.loads(product.features)
                    print(f"   Features: {', '.join(features[:2])}...")
                except:
                    pass
                    
            if product.collection:
                print(f"   Collection: {product.collection}")
            if product.promotion:
                print(f"   Promotion: {product.promotion}")
            if product.on_sale == "True":
                print(f"   ⚡ ON SALE!")
            
            print(f"   Description: {product.description[:60]}...")
        
        # Summary by collection
        print(f"\n📊 Products by Collection:")
        collections = {}
        for product in products:
            col = product.collection or "Standard"
            collections[col] = collections.get(col, 0) + 1
        
        for collection, count in collections.items():
            print(f"   {collection}: {count} products")
        
        # Count promotions
        on_sale_count = len([p for p in products if p.on_sale == "True"])
        promotion_count = len([p for p in products if p.promotion])
        
        print(f"\n🏷️ Promotions:")
        print(f"   On Sale: {on_sale_count} products")
        print(f"   Special Promotions: {promotion_count} products")

if __name__ == "__main__":
    print("🔍 ZUS Coffee Real Products Verification")
    print("=" * 50)
    verify_real_products()
    print("\n✅ Real product verification complete!")
