#!/usr/bin/env python3
"""
Production Verification Script for ZUS Coffee Chatbot
Verifies all data is production-ready with no dummy/test data
"""

import os
import sys
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

from data.database import Outlet, Product

def get_database_engine():
    """Get database engine from environment"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        return None
    
    try:
        engine = create_engine(database_url, pool_size=5, max_overflow=10)
        return engine
    except Exception as e:
        print(f"❌ ERROR: Failed to create database engine: {e}")
        return None

def verify_outlets(session):
    """Verify outlet data is production-ready"""
    print("\n🏪 VERIFYING OUTLETS")
    print("=" * 50)
    
    outlets = session.query(Outlet).all()
    print(f"📊 Total outlets: {len(outlets)}")
    
    if len(outlets) == 0:
        print("❌ ERROR: No outlets found in database")
        return False
    
    # Check for dummy/test data patterns
    dummy_patterns = ['test', 'dummy', 'sample', 'placeholder', 'lorem', 'ipsum']
    issues = []
    
    outlets_with_hours = 0
    outlets_with_services = 0
    
    for outlet in outlets:
        # Check for dummy data in name and address
        name_lower = outlet.name.lower()
        address_lower = outlet.address.lower()
        
        for pattern in dummy_patterns:
            if pattern in name_lower or pattern in address_lower:
                issues.append(f"Outlet {outlet.id} contains dummy pattern '{pattern}': {outlet.name}")
        
        # Check opening hours
        if outlet.opening_hours:
            outlets_with_hours += 1
            try:
                hours_data = json.loads(outlet.opening_hours)
                if not isinstance(hours_data, dict) or len(hours_data) == 0:
                    issues.append(f"Outlet {outlet.id} has invalid opening hours format")
            except json.JSONDecodeError:
                issues.append(f"Outlet {outlet.id} has malformed opening hours JSON")
        
        # Check services
        if outlet.services:
            outlets_with_services += 1
            try:
                services_data = json.loads(outlet.services)
                if not isinstance(services_data, list) or len(services_data) == 0:
                    issues.append(f"Outlet {outlet.id} has invalid services format")
            except json.JSONDecodeError:
                issues.append(f"Outlet {outlet.id} has malformed services JSON")
    
    print(f"✅ Outlets with opening hours: {outlets_with_hours}/{len(outlets)}")
    print(f"✅ Outlets with services: {outlets_with_services}/{len(outlets)}")
    
    if issues:
        print(f"⚠️  Found {len(issues)} issues:")
        for issue in issues[:10]:  # Show first 10 issues
            print(f"   - {issue}")
        if len(issues) > 10:
            print(f"   ... and {len(issues) - 10} more issues")
        return False
    
    print("✅ All outlets appear to be production-ready")
    return True

def verify_products(session):
    """Verify product data is production-ready"""
    print("\n🛍️  VERIFYING PRODUCTS")
    print("=" * 50)
    
    products = session.query(Product).all()
    print(f"📊 Total products: {len(products)}")
    
    if len(products) == 0:
        print("❌ ERROR: No products found in database")
        return False
    
    # Check for dummy/test data patterns
    dummy_patterns = ['test', 'dummy', 'sample', 'placeholder', 'lorem', 'ipsum']
    issues = []
    
    real_product_indicators = ['zus', 'coffee', 'tumbler', 'bottle', 'mug', 'flask', 'stainless', 'thermal']
    
    for product in products:
        name_lower = product.name.lower()
        desc_lower = (product.description or "").lower()
        
        # Check for dummy patterns
        for pattern in dummy_patterns:
            if pattern in name_lower or pattern in desc_lower:
                issues.append(f"Product {product.id} contains dummy pattern '{pattern}': {product.name}")
        
        # Check if product seems real (contains ZUS Coffee related terms)
        has_real_indicator = any(indicator in name_lower or indicator in desc_lower 
                               for indicator in real_product_indicators)
        
        if not has_real_indicator:
            issues.append(f"Product {product.id} may not be a real ZUS product: {product.name}")
        
        # Check required fields
        if not product.name or not product.price:
            issues.append(f"Product {product.id} missing required fields")
        
        # Validate price format
        if product.price and not product.price.startswith('RM'):
            issues.append(f"Product {product.id} has invalid price format: {product.price}")
    
    if issues:
        print(f"⚠️  Found {len(issues)} issues:")
        for issue in issues[:10]:  # Show first 10 issues
            print(f"   - {issue}")
        if len(issues) > 10:
            print(f"   ... and {len(issues) - 10} more issues")
        return False
    
    print("✅ All products appear to be production-ready")
    return True

def verify_no_test_files():
    """Verify no test/dummy files exist"""
    print("\n📁 VERIFYING NO TEST FILES")
    print("=" * 50)
    
    test_patterns = [
        'test_*.py', 'dummy_*.py', 'sample_*.py', 
        'test_*.json', 'dummy_*.json', 'sample_*.json',
        '*_test.py', '*_dummy.py', '*_sample.py'
    ]
    
    # Check common locations
    check_dirs = ['backend', 'frontend', 'data']
    test_files = []
    
    for dir_name in check_dirs:
        if os.path.exists(dir_name):
            for root, dirs, files in os.walk(dir_name):
                for file in files:
                    file_lower = file.lower()
                    if any(pattern.replace('*', '') in file_lower for pattern in ['test', 'dummy', 'sample']):
                        # Skip legitimate files
                        if file not in ['test_runner.py', 'requirements.txt']:
                            test_files.append(os.path.join(root, file))
    
    if test_files:
        print(f"⚠️  Found {len(test_files)} potential test files:")
        for file in test_files[:10]:
            print(f"   - {file}")
        if len(test_files) > 10:
            print(f"   ... and {len(test_files) - 10} more files")
        return False
    
    print("✅ No test files found")
    return True

def main():
    print("🔍 ZUS COFFEE CHATBOT - PRODUCTION VERIFICATION")
    print("=" * 60)
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get database engine
    engine = get_database_engine()
    if not engine:
        sys.exit(1)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Run verifications
        outlets_ok = verify_outlets(session)
        products_ok = verify_products(session)
        files_ok = verify_no_test_files()
        
        # Final summary
        print("\n🎯 PRODUCTION READINESS SUMMARY")
        print("=" * 60)
        print(f"✅ Database connection: ✓")
        print(f"{'✅' if outlets_ok else '❌'} Outlets data: {'✓' if outlets_ok else '✗'}")
        print(f"{'✅' if products_ok else '❌'} Products data: {'✓' if products_ok else '✗'}")
        print(f"{'✅' if files_ok else '❌'} No test files: {'✓' if files_ok else '✗'}")
        
        if outlets_ok and products_ok and files_ok:
            print("\n🎉 ALL CHECKS PASSED - PRODUCTION READY! 🎉")
            return True
        else:
            print("\n⚠️  SOME CHECKS FAILED - NEEDS ATTENTION")
            return False
            
    except Exception as e:
        print(f"❌ ERROR during verification: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
