"""
Super Enhanced ZUS Coffee Product Scraper
Extracts complete product details including variants with Shopify API data
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin, urlparse
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SuperZUSProductScraper:
    def __init__(self):
        self.base_url = "https://shop.zuscoffee.com"
        self.drinkware_url = "https://shop.zuscoffee.com/collections/drinkware"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def get_product_links(self) -> List[str]:
        """Get all product links from the drinkware collection page."""
        logger.info("Fetching product links from drinkware collection...")
        
        try:
            response = self.session.get(self.drinkware_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            product_links = []
            
            # Look for product links
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if '/products/' in href and href not in ['/products/', '/products']:
                    full_url = urljoin(self.base_url, href)
                    if full_url not in product_links:
                        product_links.append(full_url)
            
            logger.info(f"Found {len(product_links)} product links")
            return product_links
            
        except Exception as e:
            logger.error(f"Error fetching product links: {e}")
            return []
    
    def get_shopify_product_data(self, product_url: str) -> Dict:
        """Get Shopify product JSON data."""
        try:
            # Convert product URL to JSON endpoint
            product_handle = product_url.split('/products/')[-1].split('?')[0]
            json_url = f"{self.base_url}/products/{product_handle}.js"
            
            response = self.session.get(json_url)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"Could not get Shopify data for {product_url}: {e}")
        
        return {}
    
    def extract_detailed_product_info(self, product_url: str) -> Optional[Dict]:
        """Extract comprehensive product information."""
        logger.info(f"Scraping product: {product_url}")
        
        try:
            # Get HTML page
            response = self.session.get(product_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get Shopify JSON data
            shopify_data = self.get_shopify_product_data(product_url)
            
            # Extract basic info
            product_name = self.extract_product_name(soup, shopify_data)
            description = self.extract_description(soup, shopify_data)
            
            # Extract pricing and variants from Shopify data
            price_info, variants = self.extract_price_and_variants(shopify_data)
            
            # Extract images
            images = self.extract_images_from_shopify(shopify_data)
            
            # Extract features from HTML
            features = self.extract_features(soup)
            
            # Extract specifications
            specifications = self.extract_specifications(soup, shopify_data)
            
            # Extract material and capacity
            capacity, material = self.extract_capacity_material(product_name, specifications)
            
            # Determine category
            category = self.determine_category(product_name)
            
            # Check if on sale
            promotions = []
            if price_info['original_price'] and price_info['sale_price']:
                if price_info['sale_price'] < price_info['original_price']:
                    promotions.append({
                        "type": "Sale",
                        "description": f"Save RM{price_info['original_price'] - price_info['sale_price']:.2f}"
                    })
            
            product_data = {
                "name": product_name,
                "sale_price": price_info['sale_price'],
                "original_price": price_info['original_price'],
                "description": description,
                "features": features,
                "specifications": specifications,
                "variants": variants,
                "promotions": promotions,
                "images": images,
                "category": category,
                "product_url": product_url,
                "availability": shopify_data.get('available', True),
                "material": material,
                "capacity": capacity,
                "care_instructions": self.extract_care_instructions(soup)
            }
            
            logger.info(f"✅ Successfully scraped: {product_name}")
            return product_data
            
        except Exception as e:
            logger.error(f"❌ Error scraping product {product_url}: {e}")
            return None
    
    def extract_product_name(self, soup: BeautifulSoup, shopify_data: Dict) -> str:
        """Extract product name."""
        if shopify_data.get('title'):
            return shopify_data['title']
        
        selectors = ['h1.product-title', 'h1.product__title', '.product-name h1', 'h1']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return "Unknown Product"
    
    def extract_description(self, soup: BeautifulSoup, shopify_data: Dict) -> str:
        """Extract product description."""
        if shopify_data.get('description'):
            # Clean HTML from description
            desc_soup = BeautifulSoup(shopify_data['description'], 'html.parser')
            return desc_soup.get_text(separator=' ', strip=True)
        
        selectors = ['.product-description', '.product__description', '.product-content', '.rte']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(separator=' ', strip=True)
        
        return ""
    
    def extract_price_and_variants(self, shopify_data: Dict) -> tuple:
        """Extract pricing and variant information from Shopify data."""
        price_info = {"sale_price": None, "original_price": None}
        variants = []
        
        if not shopify_data.get('variants'):
            return price_info, variants
        
        # Get pricing from variants
        prices = []
        compare_prices = []
        
        for variant in shopify_data['variants']:
            price = variant.get('price', 0) / 100  # Shopify stores prices in cents
            compare_price = variant.get('compare_at_price', 0)
            if compare_price:
                compare_price = compare_price / 100
            
            prices.append(price)
            if compare_price:
                compare_prices.append(compare_price)
            
            # Extract variant info
            variant_info = {
                "color": variant.get('option1', ''),
                "size": variant.get('option2', ''),
                "variant_id": variant.get('id'),
                "price": price,
                "compare_price": compare_price if compare_price else None,
                "available": variant.get('available', True),
                "inventory_quantity": variant.get('inventory_quantity', 0),
                "image_url": ""
            }
            
            # Find matching image for variant
            if shopify_data.get('images'):
                for img in shopify_data['images']:
                    if variant.get('id') in img.get('variant_ids', []):
                        variant_info['image_url'] = img.get('src', '')
                        break
            
            variants.append(variant_info)
        
        # Determine main pricing
        if prices:
            price_info['sale_price'] = min(prices)
            
        if compare_prices:
            price_info['original_price'] = min(compare_prices)
        elif len(set(prices)) > 1:
            # If multiple different prices, use max as original
            price_info['original_price'] = max(prices)
        
        return price_info, variants
    
    def extract_images_from_shopify(self, shopify_data: Dict) -> Dict:
        """Extract images from Shopify data."""
        images = {"main": "", "thumbnails": []}
        
        if shopify_data.get('images'):
            # Main image (first one)
            if shopify_data['images']:
                images['main'] = shopify_data['images'][0].get('src', '')
            
            # Thumbnails (rest of images)
            for img in shopify_data['images'][1:]:
                images['thumbnails'].append(img.get('src', ''))
        
        return images
    
    def extract_features(self, soup: BeautifulSoup) -> List[str]:
        """Extract product features."""
        features = []
        
        selectors = [
            '.product-description ul li',
            '.product-features li',
            '.features li',
            '.product-info ul li',
            '.rte ul li'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                feature = element.get_text(strip=True)
                if feature and feature not in features and len(feature) > 3:
                    features.append(feature)
        
        return features
    
    def extract_specifications(self, soup: BeautifulSoup, shopify_data: Dict) -> Dict:
        """Extract product specifications."""
        specs = {}
        
        # From product name/title
        title = shopify_data.get('title', '')
        
        # Extract capacity
        capacity_match = re.search(r'(\d+(?:\.\d+)?(?:ml|oz|l))', title, re.IGNORECASE)
        if capacity_match:
            specs['Capacity'] = capacity_match.group(1)
        
        # Extract material from title
        materials = ['stainless steel', 'ceramic', 'glass', 'plastic', 'bamboo', 'silicone']
        for material in materials:
            if material.lower() in title.lower():
                specs['Material'] = material.title()
                break
        
        # Look for specification tables in HTML
        spec_sections = soup.select('.specifications, .product-specs, .product-details')
        for section in spec_sections:
            # Look for key-value pairs
            dt_elements = section.select('dt')
            dd_elements = section.select('dd')
            
            for dt, dd in zip(dt_elements, dd_elements):
                key = dt.get_text(strip=True)
                value = dd.get_text(strip=True)
                if key and value:
                    specs[key] = value
        
        return specs
    
    def extract_capacity_material(self, product_name: str, specifications: Dict) -> tuple:
        """Extract capacity and material."""
        capacity = specifications.get('Capacity', '')
        material = specifications.get('Material', '')
        
        # Extract from name if not in specs
        if not capacity:
            capacity_match = re.search(r'(\d+(?:\.\d+)?(?:ml|oz|l))', product_name, re.IGNORECASE)
            if capacity_match:
                capacity = capacity_match.group(1)
        
        if not material:
            materials = ['stainless steel', 'ceramic', 'glass', 'plastic', 'bamboo']
            for mat in materials:
                if mat.lower() in product_name.lower():
                    material = mat.title()
                    break
        
        return capacity, material
    
    def determine_category(self, product_name: str) -> str:
        """Determine product category."""
        name_lower = product_name.lower()
        
        if any(word in name_lower for word in ['cup', 'mug']):
            return "Cups & Mugs"
        elif any(word in name_lower for word in ['tumbler', 'bottle']):
            return "Tumblers & Bottles"
        elif 'bundle' in name_lower:
            return "Bundles"
        else:
            return "Drinkware"
    
    def extract_care_instructions(self, soup: BeautifulSoup) -> List[str]:
        """Extract care instructions."""
        instructions = ["Hand Wash Recommended"]
        
        # Look for care instruction text
        care_text = soup.get_text().lower()
        
        if 'dishwasher safe' in care_text:
            instructions = ["Dishwasher Safe"]
        elif 'microwave safe' in care_text:
            instructions.append("Microwave Safe")
        
        return instructions
    
    def scrape_all_products(self) -> List[Dict]:
        """Scrape all products with complete details."""
        logger.info(" Starting super comprehensive product scraping...")
        
        product_links = self.get_product_links()
        
        if not product_links:
            logger.error(" No product links found")
            return []
        
        products = []
        
        for i, link in enumerate(product_links, 1):
            logger.info(f" Processing product {i}/{len(product_links)}")
            
            product_data = self.extract_detailed_product_info(link)
            if product_data:
                products.append(product_data)
            
            # Be respectful - wait between requests
            time.sleep(1.5)
        
        logger.info(f" Successfully scraped {len(products)} products")
        return products
    
    def save_products(self, products: List[Dict], filename: str = "final_zus_products.json"):
        """Save scraped products to JSON file."""
        filepath = f"./data/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        
        logger.info(f" Saved {len(products)} products to {filepath}")

def main():
    """Main scraping function."""
    scraper = SuperZUSProductScraper()
    
    # Scrape all products
    products = scraper.scrape_all_products()
    
    if products:
        # Save to file
        scraper.save_products(products)
        
        # Print detailed summary
        print(f"\n SUPER SCRAPING COMPLETED!")
        print(f"=" * 50)
        print(f" Total products scraped: {len(products)}")
        print(f" Products with sale prices: {sum(1 for p in products if p['sale_price'])}")
        print(f"  Products with original prices: {sum(1 for p in products if p['original_price'])}")
        print(f" Products with variants: {sum(1 for p in products if p['variants'])}")
        print(f" Products with main images: {sum(1 for p in products if p['images']['main'])}")
        print(f" Products with features: {sum(1 for p in products if p['features'])}")
        print(f"  Products on sale: {sum(1 for p in products if p['promotions'])}")
        
        # Show sample product details
        if products:
            print(f"\n SAMPLE PRODUCT DETAILS:")
            print(f"=" * 30)
            sample = products[0]
            print(f"Name: {sample['name']}")
            print(f"Price: RM{sample['sale_price']}")
            if sample['original_price']:
                print(f"Original Price: RM{sample['original_price']}")
            print(f"Variants: {len(sample['variants'])}")
            if sample['variants']:
                print(f"  - Colors: {', '.join(set(v['color'] for v in sample['variants'] if v['color']))}")
            print(f"Features: {len(sample['features'])}")
            print(f"Category: {sample['category']}")
            print(f"Material: {sample['material']}")
            print(f"Capacity: {sample['capacity']}")
            
        print(f"\n Data saved to: ./data/final_zus_products.json")
        
    else:
        print(" No products were scraped successfully")

if __name__ == "__main__":
    main()
