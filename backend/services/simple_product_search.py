"""
Simplified Product Search Service (No ML Dependencies)
Fallback for when ML libraries are not available
"""
import json
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SimpleProductSearch:
    """Simple text-based product search without ML dependencies"""
    
    def __init__(self):
        self.products = []
        self.data_dir = os.path.join(os.path.dirname(__file__), "../data")
        self._load_products()
    
    def _load_products(self):
        """Load products from JSON file"""
        try:
            products_file = os.path.join(self.data_dir, "products.json")
            if os.path.exists(products_file):
                with open(products_file, 'r', encoding='utf-8') as f:
                    self.products = json.load(f)
                logger.info(f"Loaded {len(self.products)} products")
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
        
        # Check individual words
        query_words = query.split()
        for word in query_words:
            if len(word) > 2:  # Skip short words
                text_to_search = f"{product.get('name', '')} {product.get('description', '')}".lower()
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
