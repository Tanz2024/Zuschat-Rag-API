"""
Product Knowledge Base with Vector Store for ZUS Coffee products
"""
import json
import os
import pickle
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

logger = logging.getLogger(__name__)

class ProductVectorStore:
    """Vector store for product search using FAISS and SentenceTransformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.index = None
        self.products = []
        self.dimension = 384  # Dimension for all-MiniLM-L6-v2
        self.data_dir = os.path.join(os.path.dirname(__file__), "../data")
        
    def _load_model(self):
        """Load the sentence transformer model"""
        if self.model is None:
            try:
                self.model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise
    
    def load_products(self) -> bool:
        """Load products from JSON file"""
        products_file = os.path.join(self.data_dir, "products.json")
        try:
            if os.path.exists(products_file):
                with open(products_file, 'r', encoding='utf-8') as f:
                    self.products = json.load(f)
                logger.info(f"Loaded {len(self.products)} products")
                return True
            else:
                logger.warning(f"Products file not found: {products_file}")
                # Create sample products if file doesn't exist
                self.products = self._create_sample_products()
                self.save_products()
                return True
        except Exception as e:
            logger.error(f"Failed to load products: {e}")
            return False
    
    def _create_sample_products(self) -> List[Dict]:
        """Create sample products for testing"""
        return [
            {
                "name": "ZUS Coffee Signature Blend",
                "category": "Coffee",
                "price": "RM 8.90",
                "description": "Premium coffee blend with rich aroma and smooth taste",
                "ingredients": "Arabica coffee beans, milk, sugar"
            },
            {
                "name": "Iced Matcha Latte",
                "category": "Tea",
                "price": "RM 12.90",
                "description": "Refreshing matcha latte served with ice",
                "ingredients": "Matcha powder, milk, sugar, ice"
            },
            {
                "name": "Chicken Wrap",
                "category": "Food",
                "price": "RM 15.90",
                "description": "Grilled chicken wrap with fresh vegetables",
                "ingredients": "Chicken, tortilla, lettuce, tomato, sauce"
            }
        ]
    
    def save_products(self):
        """Save products to JSON file"""
        products_file = os.path.join(self.data_dir, "products.json")
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(products_file, 'w', encoding='utf-8') as f:
                json.dump(self.products, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.products)} products")
        except Exception as e:
            logger.error(f"Failed to save products: {e}")
    
    def build_index(self):
        """Build FAISS index from products"""
        if not self.products:
            logger.warning("No products loaded")
            return
        
        self._load_model()
        
        # Create text representations of products
        product_texts = []
        for product in self.products:
            text = f"{product.get('name', '')} {product.get('category', '')} {product.get('description', '')} {product.get('ingredients', '')}"
            product_texts.append(text)
        
        # Generate embeddings
        try:
            embeddings = self.model.encode(product_texts, convert_to_numpy=True)
            
            # Create FAISS index
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings.astype('float32'))
            
            logger.info(f"Built FAISS index with {len(product_texts)} products")
        except Exception as e:
            logger.error(f"Failed to build index: {e}")
            raise
    
    def save_index(self):
        """Save FAISS index to disk"""
        if self.index is None:
            logger.warning("No index to save")
            return
        
        try:
            index_file = os.path.join(self.data_dir, "products.faiss")
            meta_file = os.path.join(self.data_dir, "products_meta.pkl")
            
            faiss.write_index(self.index, index_file)
            
            with open(meta_file, 'wb') as f:
                pickle.dump({
                    'products': self.products,
                    'model_name': self.model_name,
                    'dimension': self.dimension
                }, f)
            
            logger.info("Saved FAISS index and metadata")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def load_index(self) -> bool:
        """Load FAISS index from disk"""
        try:
            index_file = os.path.join(self.data_dir, "products.faiss")
            meta_file = os.path.join(self.data_dir, "products_meta.pkl")
            
            if os.path.exists(index_file) and os.path.exists(meta_file):
                self.index = faiss.read_index(index_file)
                
                with open(meta_file, 'rb') as f:
                    meta = pickle.load(f)
                    self.products = meta['products']
                    self.model_name = meta['model_name']
                    self.dimension = meta['dimension']
                
                self._load_model()
                logger.info("Loaded FAISS index and metadata")
                return True
            else:
                logger.info("No saved index found, will build new one")
                return False
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for products using vector similarity"""
        if self.index is None or self.model is None:
            logger.warning("Index or model not loaded")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query], convert_to_numpy=True)
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.products):
                    product = self.products[idx].copy()
                    product['similarity_score'] = float(score)
                    results.append(product)
            
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def generate_summary(self, query: str, results: List[Dict]) -> str:
        """Generate a summary of search results"""
        if not results:
            return f"No products found for '{query}'"
        
        summary = f"Found {len(results)} products for '{query}':\n\n"
        for i, product in enumerate(results[:3], 1):
            summary += f"{i}. {product.get('name', 'Unknown')} - {product.get('price', 'Price not available')}\n"
            summary += f"   {product.get('description', 'No description')}\n\n"
        
        if len(results) > 3:
            summary += f"... and {len(results) - 3} more products."
        
        return summary

# Global instance
_vector_store = None

def get_vector_store() -> Optional[ProductVectorStore]:
    """Get the global vector store instance"""
    global _vector_store
    
    if _vector_store is None:
        try:
            _vector_store = ProductVectorStore()
            
            # Try to load existing index
            if not _vector_store.load_index():
                # Build new index if none exists
                if _vector_store.load_products():
                    _vector_store.build_index()
                    _vector_store.save_index()
                else:
                    logger.error("Failed to load products")
                    return None
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            return None
    
    return _vector_store
