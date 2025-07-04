#!/usr/bin/env python3
"""
Enhanced Product Model with Calculated Fields
Adds pre-calculated values to improve performance
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
import json

Base = declarative_base()

class EnhancedProduct(Base):
    """Enhanced Product model with calculated fields"""
    __tablename__ = "products_enhanced"
    
    # Basic product info
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    description = Column(Text)
    
    # Pricing (store both original and calculated)
    price_display = Column(String, nullable=False)  # "RM 55.00" for display
    price_value = Column(Float, nullable=False, index=True)  # 55.0 for calculations
    regular_price_display = Column(String)  # "RM 79.00"
    regular_price_value = Column(Float)  # 79.0
    
    # Pre-calculated discount fields
    discount_percentage = Column(Float)  # 30.0 (calculated from regular vs sale)
    discount_amount = Column(Float)  # 24.0 (RM saved)
    is_on_sale = Column(Boolean, default=False, index=True)
    
    # Tax calculations (if needed)
    tax_rate = Column(Float, default=0.0)  # 6% SST in Malaysia
    price_before_tax = Column(Float)
    tax_amount = Column(Float)
    
    # Product specifications
    capacity = Column(String)
    material = Column(String)
    colors = Column(Text)  # JSON string
    features = Column(Text)  # JSON string
    collection = Column(String, index=True)
    
    # Promotional info
    promotion_type = Column(String)  # "Buy 1 Free 1", "Limited Edition"
    promotion_valid_until = Column(DateTime)
    
    # Inventory and availability
    stock_status = Column(String, default="Available")  # Available, Out of Stock, Limited
    is_featured = Column(Boolean, default=False, index=True)
    
    def calculate_discount(self):
        """Calculate discount percentage and amount"""
        if self.regular_price_value and self.price_value < self.regular_price_value:
            self.discount_amount = self.regular_price_value - self.price_value
            self.discount_percentage = (self.discount_amount / self.regular_price_value) * 100
            self.is_on_sale = True
        else:
            self.discount_amount = 0.0
            self.discount_percentage = 0.0
            self.is_on_sale = False
    
    def calculate_tax(self):
        """Calculate tax amount (6% SST for Malaysia)"""
        if self.tax_rate > 0:
            self.price_before_tax = self.price_value / (1 + self.tax_rate / 100)
            self.tax_amount = self.price_value - self.price_before_tax
        else:
            self.price_before_tax = self.price_value
            self.tax_amount = 0.0
    
    def get_colors_list(self):
        """Get colors as list"""
        try:
            return json.loads(self.colors) if self.colors else []
        except:
            return []
    
    def get_features_list(self):
        """Get features as list"""
        try:
            return json.loads(self.features) if self.features else []
        except:
            return []
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'price': self.price_display,
            'price_value': self.price_value,
            'regular_price': self.regular_price_display,
            'discount_percentage': round(self.discount_percentage, 1) if self.discount_percentage else None,
            'discount_amount': round(self.discount_amount, 2) if self.discount_amount else None,
            'savings': f"RM {self.discount_amount:.2f}" if self.discount_amount > 0 else None,
            'is_on_sale': self.is_on_sale,
            'capacity': self.capacity,
            'material': self.material,
            'colors': self.get_colors_list(),
            'features': self.get_features_list(),
            'collection': self.collection,
            'promotion_type': self.promotion_type,
            'stock_status': self.stock_status,
            'is_featured': self.is_featured
        }

# Cart and Order calculations (compute on-the-fly)
class CartCalculator:
    """Handle dynamic cart calculations"""
    
    def __init__(self, tax_rate=6.0):  # 6% SST in Malaysia
        self.tax_rate = tax_rate
    
    def calculate_cart_total(self, items):
        """
        Calculate cart total with tax and discounts
        items: [{'product': Product, 'quantity': int}]
        """
        subtotal = 0.0
        total_savings = 0.0
        
        for item in items:
            product = item['product']
            quantity = item['quantity']
            
            # Calculate line total
            line_total = product.price_value * quantity
            subtotal += line_total
            
            # Calculate savings
            if product.discount_amount:
                line_savings = product.discount_amount * quantity
                total_savings += line_savings
        
        # Calculate tax on discounted amount
        tax_amount = (subtotal * self.tax_rate) / 100
        
        # Final total
        final_total = subtotal + tax_amount
        
        return {
            'subtotal': round(subtotal, 2),
            'total_savings': round(total_savings, 2),
            'tax_amount': round(tax_amount, 2),
            'tax_rate': self.tax_rate,
            'final_total': round(final_total, 2),
            'display_total': f"RM {final_total:.2f}"
        }
    
    def apply_promo_code(self, cart_total, promo_code):
        """Apply promotional discount codes"""
        promos = {
            'WELCOME10': 0.10,  # 10% off
            'STUDENT15': 0.15,  # 15% off for students
            'NEWBIE20': 0.20,   # 20% off for new customers
        }
        
        if promo_code in promos:
            discount = cart_total['subtotal'] * promos[promo_code]
            new_subtotal = cart_total['subtotal'] - discount
            new_tax = (new_subtotal * self.tax_rate) / 100
            new_total = new_subtotal + new_tax
            
            return {
                **cart_total,
                'promo_code': promo_code,
                'promo_discount': round(discount, 2),
                'subtotal_after_promo': round(new_subtotal, 2),
                'tax_amount': round(new_tax, 2),
                'final_total': round(new_total, 2),
                'display_total': f"RM {new_total:.2f}"
            }
        
        return cart_total

def migrate_existing_products():
    """Migration script to add calculated fields to existing products"""
    print("🔄 Migrating products to enhanced model...")
    
    # This would read your existing products and calculate the new fields
    # Implementation depends on your current data structure
    pass

if __name__ == "__main__":
    # Example usage
    calculator = CartCalculator()
    
    # Example cart calculation
    # items = [
    #     {'product': some_product, 'quantity': 2}
    # ]
    # total = calculator.calculate_cart_total(items)
    # print(f"Cart total: {total['display_total']}")
    
    print("✅ Enhanced product model ready for implementation")
