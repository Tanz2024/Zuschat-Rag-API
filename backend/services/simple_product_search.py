"""
Simplified Product Search Service (No ML Dependencies)
Fallback for when ML libraries are not available
"""
import json
import os
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from data.database import get_db, Product

logger = logging.getLogger(__name__)

class SimpleProductSearch:
    """Simple text-based product search without ML dependencies"""
    
    def __init__(self):
        self.products = []
        self.data_dir = os.path.join(os.path.dirname(__file__), "../data")
        self._load_products()
    
    def _load_products(self):
        """Load products from database or JSON file as fallback"""
        try:
            # Try to load from database first
            db = next(get_db())
            db_products = db.query(Product).all()
            
            if db_products:
                self.products = []
                for product in db_products:
                    self.products.append({
                        'id': product.id,
                        'name': product.name,
                        'category': product.category,
                        'description': product.description,
                        'price': self._parse_price(product.price),
                        'sale_price': product.sale_price,
                        'regular_price': product.regular_price,
                        'material': product.material,
                        'collection': product.collection,
                        'capacity': product.capacity,
                        'colors': product.colors,
                        'features': product.features,
                        'ingredients': product.ingredients,
                        'promotion': product.promotion,
                        'on_sale': product.on_sale,
                        'discount': product.discount,
                        'image_url': getattr(product, 'image_url', ''),
                        'product_url': getattr(product, 'product_url', '')
                    })
                logger.info(f"Loaded {len(self.products)} products from database")
                db.close()
                return
                
        except Exception as e:
            logger.warning(f"Could not load from database: {e}")
        
        # Fallback to JSON file
        try:
            products_file = os.path.join(self.data_dir, "products.json")
            if os.path.exists(products_file):
                with open(products_file, 'r', encoding='utf-8') as f:
                    self.products = json.load(f)
                logger.info(f"Loaded {len(self.products)} products from JSON file")
            else:
                logger.warning(f"Products file not found: {products_file}")
        except Exception as e:
            logger.error(f"Error loading products: {e}")
            self.products = []
    
    def search_products(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Simple text-based product search
        """
        if not query or not self.products:
            return []
        
        query_lower = query.lower()
        results = []
        
        for product in self.products:
            score = self._calculate_text_similarity(query_lower, product)
            if score > 0:
                results.append({
                    'product': product,
                    'score': score,
                    'match_type': 'text_match'
                })
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def _parse_price(self, price_str: str) -> float:
        """Parse price string like 'RM 55.00' to float value"""
        if not price_str:
            return 0.0
        
        try:
            # Remove 'RM' and any whitespace, then convert to float
            price_clean = str(price_str).replace('RM', '').strip()
            return float(price_clean)
        except (ValueError, AttributeError):
            logger.warning(f"Could not parse price: {price_str}")
            return 0.0
    
    def _calculate_text_similarity(self, query: str, product: Dict) -> float:
        """Calculate simple text similarity score"""
        score = 0.0
        
        # Check name (highest weight)
        if query in product.get('name', '').lower():
            score += 3.0
        
        # Check category
        if query in product.get('category', '').lower():
            score += 2.0
        
        # Check description
        if query in product.get('description', '').lower():
            score += 1.5
        
        # Check material
        if query in product.get('material', '').lower():
            score += 1.0
        
        # Check collection
        if query in product.get('collection', '').lower():
            score += 1.0
        
        # Check ingredients
        if query in product.get('ingredients', '').lower():
            score += 1.0
        
        # Check colors (JSON string)
        colors_str = product.get('colors', '')
        if colors_str and query in colors_str.lower():
            score += 0.8
        
        # Check features (JSON string)
        features_str = product.get('features', '')
        if features_str and query in features_str.lower():
            score += 0.8
        
        # Check individual words
        query_words = query.split()
        for word in query_words:
            if len(word) > 2:  # Skip short words
                text_to_search = f"{product.get('name', '')} {product.get('description', '')} {product.get('ingredients', '')}".lower()
                if word in text_to_search:
                    score += 0.5
        
        return score
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Get product by ID"""
        for product in self.products:
            if product.get('id') == product_id:
                return product
        return None
    
    def get_products_by_category(self, category: str) -> List[Dict]:
        """Get products by category"""
        return [p for p in self.products if p.get('category', '').lower() == category.lower()]
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Main search method for compatibility with ML-based search
        """
        results = self.search_products(query, top_k)
        # Return just the products, not the wrapper with scores
        return [result['product'] for result in results]
    
    def generate_summary(self, query: str, results: List[Dict]) -> str:
        """Generate a summary of search results"""
        if not results:
            return f"No products found for '{query}'"
        
        product_names = [p.get('name', 'Unknown') for p in results[:3]]
        if len(results) == 1:
            return f"Found 1 product: {product_names[0]}"
        elif len(results) <= 3:
            return f"Found {len(results)} products: {', '.join(product_names)}"
        else:
            return f"Found {len(results)} products including: {', '.join(product_names)} and {len(results)-3} more"
    
    def get_featured_products(self, limit: int = 5) -> List[Dict]:
        """Get featured/sale products"""
        featured = [p for p in self.products if p.get('on_sale') or p.get('promotion')]
        return featured[:limit]

# Factory function to get the appropriate search service
def get_product_search_service():
    """Get product search service (tries ML first, falls back to simple)"""
    try:
        # Try to import ML dependencies
        import sentence_transformers
        import faiss
        from services.product_search_service import ProductVectorStore
        
        # If successful, return the ML-based service
        vector_store = ProductVectorStore()
        return vector_store
    except ImportError:
        # Fall back to simple text search
        logger.info("ML dependencies not available, using simple text search")
        return SimpleProductSearch()

# Main function for compatibility
def get_vector_store():
    """Compatibility function"""
    return get_product_search_service()
