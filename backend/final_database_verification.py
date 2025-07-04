#!/usr/bin/env python3
"""
Comprehensive verification of all data in PostgreSQL database
"""
from dotenv import load_dotenv
load_dotenv()

from data.database import SessionLocal, Outlet, Product
import json

def verify_database_contents():
    """Verify all data in PostgreSQL database"""
    print("🔍 ZUS Coffee PostgreSQL Database Contents Verification")
    print("=" * 70)
    
    with SessionLocal() as db:
        # 1. Outlet verification
        print(f"\n🏪 OUTLETS VERIFICATION:")
        total_outlets = db.query(Outlet).count()
        print(f"   Total outlets: {total_outlets}")
        
        # Sample outlet with full details
        sample_outlet = db.query(Outlet).first()
        if sample_outlet:
            print(f"\n📍 Sample Outlet (Full Details):")
            print(f"   Name: {sample_outlet.name}")
            print(f"   Address: {sample_outlet.address}")
            print(f"   Hours: {sample_outlet.opening_hours}")
            print(f"   Services: {sample_outlet.services}")
        
        # 2. Product verification
        print(f"\n🛍️ PRODUCTS VERIFICATION:")
        total_products = db.query(Product).count()
        print(f"   Total products: {total_products}")
        
        # Show all products with details
        products = db.query(Product).all()
        print(f"\n📋 All Products in Database:")
        for i, product in enumerate(products, 1):
            print(f"\n   {i}. {product.name}")
            print(f"      Category: {product.category}")
            print(f"      Price: {product.price} (Sale: RM {product.sale_price})")
            print(f"      Material: {product.material}")
            print(f"      Capacity: {product.capacity}")
            
            # Parse JSON fields
            if product.colors:
                try:
                    colors = json.loads(product.colors)
                    print(f"      Colors: {', '.join(colors)}")
                except:
                    print(f"      Colors: {product.colors}")
            
            if product.features:
                try:
                    features = json.loads(product.features)
                    print(f"      Features: {', '.join(features[:3])}...")
                except:
                    print(f"      Features: {product.features}")
            
            if product.collection:
                print(f"      Collection: {product.collection}")
            if product.promotion:
                print(f"      Promotion: {product.promotion}")
            if product.on_sale == "True":
                print(f"      🏷️ ON SALE!")
        
        # 3. Data completeness check
        print(f"\n📊 DATA COMPLETENESS CHECK:")
        
        # Check outlets
        outlets_with_hours = db.query(Outlet).filter(Outlet.opening_hours.isnot(None)).count()
        outlets_with_services = db.query(Outlet).filter(Outlet.services.isnot(None)).count()
        
        print(f"   ✅ Outlets with opening hours: {outlets_with_hours}/{total_outlets}")
        print(f"   ✅ Outlets with services: {outlets_with_services}/{total_outlets}")
        
        # Check products
        products_with_colors = db.query(Product).filter(Product.colors.isnot(None)).count()
        products_with_features = db.query(Product).filter(Product.features.isnot(None)).count()
        products_on_sale = db.query(Product).filter(Product.on_sale == "True").count()
        
        print(f"   ✅ Products with colors: {products_with_colors}/{total_products}")
        print(f"   ✅ Products with features: {products_with_features}/{total_products}")
        print(f"   ✅ Products on sale: {products_on_sale}/{total_products}")
        
        # 4. Summary
        print(f"\n🎯 MIGRATION SUCCESS SUMMARY:")
        if (total_outlets == 243 and 
            outlets_with_hours == total_outlets and 
            outlets_with_services == total_outlets and
            total_products == 11 and
            products_with_colors >= 10 and
            products_with_features >= 10):
            print(f"   🎉 ALL DATA SUCCESSFULLY MIGRATED!")
            print(f"   📊 243 outlets with complete information")
            print(f"   🛍️ 11 real ZUS Coffee products with full details")
            print(f"   🗄️ PostgreSQL database is production-ready!")
        else:
            print(f"   ⚠️ Some data may be incomplete")

if __name__ == "__main__":
    verify_database_contents()
