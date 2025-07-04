#!/usr/bin/env python3
"""
Count and verify products in JSON file
"""
import json

def count_products_in_json():
    """Count products in the JSON file"""
    with open('data/products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"📊 Products in JSON file: {len(products)}")
    print("\n📋 Product List:")
    for i, product in enumerate(products, 1):
        print(f"   {i}. {product['name']} ({product['category']})")
    
    return len(products)

if __name__ == "__main__":
    count_products_in_json()
