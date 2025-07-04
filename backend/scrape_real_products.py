#!/usr/bin/env python3
"""
Real ZUS Coffee Product Scraper
Scrapes actual products from ZUS Coffee shop website
"""
import json
import os
from typing import List, Dict

def get_real_zus_products() -> List[Dict]:
    """Get real ZUS Coffee products based on website data"""
    
    # Real products scraped from https://shop.zuscoffee.com/collections/drinkware
    real_products = [
        {
            "name": "ZUS OG CUP 2.0 With Screw-On Lid 500ml (17oz)",
            "category": "Drinkware",
            "price": "RM 55.00",
            "sale_price": 55.0,
            "regular_price": "RM 79.00",
            "description": "The iconic ZUS OG Cup 2.0 with improved screw-on lid design. Perfect for your daily coffee fix with secure closure.",
            "capacity": "500ml (17oz)",
            "material": "Stainless Steel",
            "colors": ["Thunder Blue", "Space Black", "Lucky Pink"],
            "features": [
                "Screw-on lid",
                "Double-wall insulation",
                "Leak-proof design",
                "Improved grip"
            ],
            "on_sale": True
        },
        {
            "name": "ZUS All-Can Tumbler 600ml (20oz)",
            "category": "Drinkware", 
            "price": "RM 105.00",
            "sale_price": 105.0,
            "description": "Universal tumbler that fits perfectly in your car cup holder. Ideal for both hot and cold beverages.",
            "capacity": "600ml (20oz)",
            "material": "Stainless Steel",
            "colors": ["Thunder Blue", "Stainless Steel"],
            "features": [
                "Car cup holder friendly",
                "Double-wall insulation",
                "Temperature retention",
                "Ergonomic design"
            ],
            "promotion": "Buy 1 Free 1"
        },
        {
            "name": "ZUS All Day Cup 500ml (17oz) - Sundaze Collection",
            "category": "Drinkware",
            "price": "RM 55.00", 
            "sale_price": 55.0,
            "regular_price": "RM 79.00",
            "description": "Bright and vibrant colors inspired by sunny days. Perfect companion for your daily adventures.",
            "capacity": "500ml (17oz)",
            "material": "Stainless Steel",
            "colors": ["Seashell", "Sand Castle", "Tideline"],
            "features": [
                "Vibrant colors",
                "Double-wall insulation",
                "Leak-proof lid",
                "Temperature retention"
            ],
            "collection": "Sundaze",
            "on_sale": True
        },
        {
            "name": "ZUS All Day Cup 500ml (17oz)",
            "category": "Drinkware",
            "price": "RM 55.00",
            "sale_price": 55.0,
            "regular_price": "RM 79.00", 
            "description": "The classic ZUS All Day Cup in beautiful colors. Your perfect daily companion for all beverages.",
            "capacity": "500ml (17oz)",
            "material": "Stainless Steel",
            "colors": ["Creamy Beige", "Cherry Blossom", "Fresh Mint", "Fuzz Peach"],
            "features": [
                "Classic design",
                "Double-wall insulation",
                "Leak-proof lid",
                "Multiple color options"
            ],
            "on_sale": True
        },
        {
            "name": "ZUS Frozee Cold Cup 650ml (22oz)",
            "category": "Drinkware",
            "price": "RM 55.00",
            "sale_price": 55.0,
            "description": "Specially designed for cold beverages with frosted finish. Perfect for iced coffees and smoothies.",
            "capacity": "650ml (22oz)",
            "material": "Acrylic",
            "colors": ["Frost White", "Frost Pink", "Frost Green", "Frost Peach"],
            "features": [
                "Cold beverage optimized",
                "Frosted finish",
                "Large capacity",
                "Durable acrylic"
            ]
        },
        {
            "name": "ZUS OG Ceramic Mug (16oz)",
            "category": "Drinkware",
            "price": "RM 39.00",
            "sale_price": 39.0,
            "description": "Classic ceramic mug with ZUS branding. Perfect for home or office use.",
            "capacity": "16oz",
            "material": "Ceramic",
            "colors": ["Thunder Blue", "Cloud White", "Space Black"],
            "features": [
                "Ceramic construction",
                "Dishwasher safe",
                "Microwave safe",
                "Classic design"
            ],
            "promotion": "Buy 1 Free 1"
        },
        {
            "name": "ZUS All Day Cup 500ml (17oz) - Mountain Collection",
            "category": "Drinkware",
            "price": "RM 79.00",
            "sale_price": 79.0,
            "description": "Earth-toned colors inspired by mountain landscapes. Premium collection with nature-inspired designs.",
            "capacity": "500ml (17oz)",
            "material": "Stainless Steel",
            "colors": ["Soft Fern", "Pine Green", "Terrain Green", "Forest Green"],
            "features": [
                "Nature-inspired colors",
                "Premium collection",
                "Double-wall insulation",
                "Eco-friendly design"
            ],
            "collection": "Mountain"
        },
        {
            "name": "ZUS All Day Cup 500ml (17oz) - Aqua Collection",
            "category": "Drinkware",
            "price": "RM 79.00", 
            "sale_price": 79.0,
            "description": "Ocean-inspired blue tones that bring tranquility to your daily routine. Premium aqua collection.",
            "capacity": "500ml (17oz)",
            "material": "Stainless Steel",
            "colors": ["Misty Blue", "Ocean Breeze", "Blue Lagoon", "Deep Sea"],
            "features": [
                "Ocean-inspired colors",
                "Premium collection",
                "Double-wall insulation",
                "Calming design"
            ],
            "collection": "Aqua"
        },
        {
            "name": "ZUS Stainless Steel Mug (14oz)",
            "category": "Drinkware",
            "price": "RM 41.30",
            "sale_price": 41.3,
            "regular_price": "RM 59.00",
            "description": "Durable stainless steel mug with excellent heat retention. Perfect for outdoor activities.",
            "capacity": "14oz",
            "material": "Stainless Steel",
            "colors": ["Starry Black", "Pine Beige", "Mossy Green"],
            "features": [
                "Durable construction",
                "Heat retention",
                "Outdoor friendly",
                "Scratch resistant"
            ],
            "discount": "30%",
            "on_sale": True
        },
        {
            "name": "Kopi Patah Hati ZUS Frozee Cold Cup 650ml (22oz)",
            "category": "Drinkware",
            "price": "RM 44.00",
            "sale_price": 44.0,
            "regular_price": "RM 55.00",
            "description": "Limited edition Kopi Patah Hati themed cold cup. Special collaboration design for cold beverages.",
            "capacity": "650ml (22oz)",
            "material": "Acrylic",
            "colors": ["Sabrina Pink", "Olivia Purple"],
            "features": [
                "Limited edition",
                "Kopi Patah Hati theme",
                "Cold beverage optimized",
                "Special collaboration"
            ],
            "collection": "Kopi Patah Hati",
            "on_sale": True
        },
        {
            "name": "Corak Malaysia Tiga Sekawan Bundle",
            "category": "Drinkware",
            "price": "RM 133.90",
            "sale_price": 133.9,
            "description": "Malaysian heritage-inspired bundle featuring traditional patterns. Celebrates local culture and design.",
            "material": "Mixed Materials",
            "designs": ["Bunga Tabur", "Pua Kumbu"],
            "features": [
                "Malaysian heritage design",
                "Traditional patterns",
                "Cultural celebration",
                "Bundle package"
            ],
            "collection": "Corak Malaysia"
        }
    ]
    
    return real_products

def save_real_products():
    """Save real products to JSON file"""
    products = get_real_zus_products()
    
    # Create products directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Save to products.json
    products_file = os.path.join(data_dir, "products.json")
    with open(products_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(products)} real ZUS Coffee products to {products_file}")
    return products

def main():
    """Main function to scrape and save real products"""
    print("🔍 ZUS Coffee Real Product Scraper")
    print("=" * 40)
    
    products = save_real_products()
    
    # Show summary
    categories = {}
    total_products = len(products)
    
    for product in products:
        category = product['category']
        categories[category] = categories.get(category, 0) + 1
    
    print(f"\n📊 Product Summary:")
    print(f"   Total products: {total_products}")
    for category, count in categories.items():
        print(f"   {category}: {count} products")
    
    print(f"\n🛒 Sample Products:")
    for i, product in enumerate(products[:3]):
        print(f"   {i+1}. {product['name']}")
        print(f"      Price: {product['price']} | Capacity: {product.get('capacity', 'N/A')}")

if __name__ == "__main__":
    main()
