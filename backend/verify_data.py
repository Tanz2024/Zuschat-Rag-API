#!/usr/bin/env python3
"""
Comprehensive script to verify all data in PostgreSQL
"""
from dotenv import load_dotenv
load_dotenv()

from data.database import SessionLocal, Outlet, Product

def verify_complete_data():
    """Verify all data in PostgreSQL"""
    with SessionLocal() as db:
        # Count total outlets
        total_outlets = db.query(Outlet).count()
        print(f"🏪 Total outlets in PostgreSQL: {total_outlets}")
        
        # Count outlets by state/location
        kl_outlets = db.query(Outlet).filter(
            Outlet.address.ilike('%kuala lumpur%') | 
            Outlet.address.ilike('%wilayah persekutuan%') |
            Outlet.address.ilike('% kl %')
        ).count()
        
        selangor_outlets = db.query(Outlet).filter(
            Outlet.address.ilike('%selangor%')
        ).count()
        
        print(f"   📍 KL outlets: {kl_outlets}")
        print(f"   📍 Selangor outlets: {selangor_outlets}")
        print(f"   📍 Other locations: {total_outlets - kl_outlets - selangor_outlets}")
        
        # Count total products
        total_products = db.query(Product).count()
        print(f"\n🛍️ Total products in PostgreSQL: {total_products}")
        
        # Count products by category
        categories = db.query(Product.category).distinct().all()
        for (category,) in categories:
            count = db.query(Product).filter(Product.category == category).count()
            print(f"   📦 {category}: {count} products")
        
        # Show sample outlets
        print(f"\n📋 Sample outlets:")
        sample_outlets = db.query(Outlet).limit(3).all()
        for outlet in sample_outlets:
            print(f"   • {outlet.name}")
            print(f"     {outlet.address[:60]}...")
        
        # Show sample products
        print(f"\n🛒 Sample products:")
        sample_products = db.query(Product).limit(5).all()
        for product in sample_products:
            print(f"   • {product.name} ({product.category})")
            print(f"     Price: {product.price}, Description: {product.description[:50]}...")

if __name__ == "__main__":
    print("🔍 ZUS Coffee Complete Data Verification")
    print("=" * 50)
    verify_complete_data()
    print("\n✅ Data verification complete!")
