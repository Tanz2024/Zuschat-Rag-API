#!/usr/bin/env python3
"""
Check ZUS Coffee products for any dummy or invalid data
"""
import json

def check_products_for_dummy_data():
    """Check products.json for any dummy or invalid entries"""
    
    # Read products
    with open('data/products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"📊 Total products: {len(products)}")
    print("=" * 60)
    
    dummy_indicators = [
        "dummy", "test", "placeholder", "example", "sample",
        "lorem ipsum", "xxx", "tbd", "todo", "temp"
    ]
    
    valid_products = []
    dummy_products = []
    
    for i, product in enumerate(products):
        is_dummy = False
        
        # Check for dummy indicators in key fields
        name = product.get('name', '').lower()
        description = product.get('description', '').lower()
        category = product.get('category', '').lower()
        
        # Check for dummy text
        for indicator in dummy_indicators:
            if (indicator in name or indicator in description or indicator in category):
                is_dummy = True
                break
        
        # Check for invalid pricing
        price_str = product.get('price', '')
        sale_price = product.get('sale_price', 0)
        
        if (not price_str or 
            not isinstance(sale_price, (int, float)) or 
            sale_price <= 0):
            is_dummy = True
        
        # Check for missing essential fields
        if (not product.get('name') or 
            not product.get('description') or 
            not product.get('category')):
            is_dummy = True
        
        if is_dummy:
            dummy_products.append(product)
            print(f"🗑️  Found dummy product #{i+1}:")
            print(f"    Name: {product.get('name')}")
            print(f"    Price: {product.get('price')}")
            print(f"    Description: {product.get('description')[:100]}...")
            print()
        else:
            valid_products.append(product)
    
    print(f"✅ Analysis complete!")
    print(f"📊 Valid products: {len(valid_products)}")
    print(f"📊 Dummy products: {len(dummy_products)}")
    
    if len(dummy_products) == 0:
        print("🎉 No dummy products found! All products are valid.")
    else:
        # Save cleaned products
        with open('data/products_cleaned.json', 'w', encoding='utf-8') as f:
            json.dump(valid_products, f, indent=2, ensure_ascii=False)
        print(f"💾 Cleaned products saved to products_cleaned.json")
    
    # Show sample of valid products
    print(f"\n📍 Sample valid products:")
    for i, product in enumerate(valid_products[:3], 1):
        print(f"{i}. {product['name']} - {product['price']}")
        print(f"   Category: {product['category']}")
        print(f"   Description: {product['description'][:80]}...")
        print()

if __name__ == "__main__":
    check_products_for_dummy_data()
