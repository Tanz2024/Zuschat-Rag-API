#!/usr/bin/env python3
"""
Real-Time Calculator Integration for ZUS Coffee
Works with your existing products.json and database
"""

import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment
load_dotenv()

from data.database import Product

@dataclass
class CartItem:
    """Cart item for calculations"""
    product_id: int
    quantity: int

class ZUSRealTimeCalculator:
    """Real-time calculator specifically for ZUS Coffee products"""
    
    def __init__(self, tax_rate: float = 6.0):
        self.tax_rate = tax_rate
        
        # Create database session
        engine = create_engine(os.getenv('DATABASE_URL'))
        Session = sessionmaker(bind=engine)
        self.session = Session()
    
    def parse_price(self, price_str: str) -> float:
        """Convert price string to float"""
        if not price_str:
            return 0.0
        return float(price_str.replace('RM ', '').replace(',', '').strip())
    
    def get_product_pricing(self, product: Product) -> Dict:
        """Calculate pricing info for a product from database"""
        current_price = float(product.sale_price) if product.sale_price else self.parse_price(product.price)
        
        # Check if there's a regular price (indicating a sale)
        if product.regular_price:
            regular_price = self.parse_price(product.regular_price)
            if regular_price > current_price:
                discount_amount = regular_price - current_price
                discount_percentage = (discount_amount / regular_price) * 100
                
                return {
                    'product_id': product.id,
                    'name': product.name,
                    'current_price': current_price,
                    'regular_price': regular_price,
                    'has_discount': True,
                    'discount_amount': round(discount_amount, 2),
                    'discount_percentage': round(discount_percentage, 1),
                    'price_display': f"RM {current_price:.2f}",
                    'regular_price_display': f"RM {regular_price:.2f}",
                    'savings_text': f"Save RM {discount_amount:.2f} ({discount_percentage:.0f}% off)",
                    'promotion': product.promotion,
                    'chat_response': self._generate_chat_response(product, current_price, regular_price, discount_amount, discount_percentage)
                }
        
        # No discount
        return {
            'product_id': product.id,
            'name': product.name,
            'current_price': current_price,
            'regular_price': None,
            'has_discount': False,
            'price_display': f"RM {current_price:.2f}",
            'promotion': product.promotion,
            'chat_response': self._generate_chat_response(product, current_price)
        }
    
    def _generate_chat_response(self, product: Product, current_price: float, 
                               regular_price: float = None, discount_amount: float = None, 
                               discount_percentage: float = None) -> str:
        """Generate chatbot-friendly response"""
        
        if regular_price and discount_amount:
            return (f"🎉 {product.name} is on sale for RM {current_price:.2f} "
                   f"(was RM {regular_price:.2f}) - Save RM {discount_amount:.2f} "
                   f"({discount_percentage:.0f}% off)!")
        elif product.promotion:
            return (f"✨ {product.name} for RM {current_price:.2f} "
                   f"with special offer: {product.promotion}!")
        else:
            return f"☕ {product.name} - RM {current_price:.2f}"
    
    def calculate_cart_total(self, cart_items: List[CartItem]) -> Dict:
        """Calculate cart total in real-time"""
        if not cart_items:
            return {
                'empty_cart': True,
                'message': "Your cart is empty. Browse our ZUS Coffee products!"
            }
        
        subtotal = 0.0
        total_savings = 0.0
        items_detail = []
        
        for cart_item in cart_items:
            # Get product from database
            product = self.session.query(Product).filter(Product.id == cart_item.product_id).first()
            if not product:
                continue
            
            # Get pricing info
            pricing = self.get_product_pricing(product)
            
            # Calculate line totals
            line_total = pricing['current_price'] * cart_item.quantity
            subtotal += line_total
            
            # Add savings
            if pricing['has_discount']:
                line_savings = pricing['discount_amount'] * cart_item.quantity
                total_savings += line_savings
            
            items_detail.append({
                'name': product.name,
                'price': pricing['price_display'],
                'quantity': cart_item.quantity,
                'line_total': f"RM {line_total:.2f}",
                'has_discount': pricing['has_discount'],
                'savings': f"RM {pricing.get('discount_amount', 0) * cart_item.quantity:.2f}" if pricing['has_discount'] else None
            })
        
        # Calculate tax (6% SST for Malaysia)
        tax_amount = (subtotal * self.tax_rate) / 100
        final_total = subtotal + tax_amount
        
        return {
            'empty_cart': False,
            'items': items_detail,
            'item_count': len(cart_items),
            'total_quantity': sum(item.quantity for item in cart_items),
            'subtotal': round(subtotal, 2),
            'subtotal_display': f"RM {subtotal:.2f}",
            'total_savings': round(total_savings, 2),
            'savings_display': f"RM {total_savings:.2f}" if total_savings > 0 else None,
            'tax_rate': self.tax_rate,
            'tax_amount': round(tax_amount, 2),
            'tax_display': f"RM {tax_amount:.2f}",
            'final_total': round(final_total, 2),
            'final_total_display': f"RM {final_total:.2f}",
            'chat_summary': self._generate_cart_summary(len(cart_items), subtotal, total_savings, tax_amount, final_total)
        }
    
    def _generate_cart_summary(self, item_count: int, subtotal: float, 
                              savings: float, tax: float, total: float) -> str:
        """Generate chat-friendly cart summary"""
        summary = f"🛒 Your cart: {item_count} items\\n"
        summary += f"Subtotal: RM {subtotal:.2f}\\n"
        
        if savings > 0:
            summary += f"💰 You're saving: RM {savings:.2f}\\n"
        
        summary += f"Tax (6% SST): RM {tax:.2f}\\n"
        summary += f"**Total: RM {total:.2f}**"
        
        return summary
    
    def apply_promo_code(self, cart_total: Dict, promo_code: str) -> Dict:
        """Apply promo codes in real-time"""
        if cart_total.get('empty_cart'):
            return cart_total
        
        promo_codes = {
            'WELCOME10': {'discount': 0.10, 'description': '10% off for new customers'},
            'STUDENT15': {'discount': 0.15, 'description': '15% off for students'},  
            'ZUSCOFFEE20': {'discount': 0.20, 'description': '20% off - limited time'},
            'FIRSTCUP25': {'discount': 0.25, 'description': '25% off your first purchase'}
        }
        
        promo_code = promo_code.upper().strip()
        
        if promo_code not in promo_codes:
            return {
                **cart_total,
                'promo_error': f"❌ Invalid promo code: '{promo_code}'"
            }
        
        promo = promo_codes[promo_code]
        promo_discount = cart_total['subtotal'] * promo['discount']
        new_subtotal = cart_total['subtotal'] - promo_discount
        new_tax = (new_subtotal * self.tax_rate) / 100
        new_final_total = new_subtotal + new_tax
        
        total_discount = cart_total['total_savings'] + promo_discount
        
        return {
            **cart_total,
            'promo_applied': True,
            'promo_code': promo_code,
            'promo_description': promo['description'],
            'promo_discount': round(promo_discount, 2),
            'promo_discount_display': f"RM {promo_discount:.2f}",
            'subtotal_after_promo': round(new_subtotal, 2),
            'tax_amount': round(new_tax, 2),
            'tax_display': f"RM {new_tax:.2f}",
            'final_total': round(new_final_total, 2),
            'final_total_display': f"RM {new_final_total:.2f}",
            'total_discount': round(total_discount, 2),
            'promo_chat_response': f"🎫 Promo '{promo_code}' applied! {promo['description']} - Additional RM {promo_discount:.2f} off!"
        }
    
    def get_product_by_name(self, product_name: str) -> Optional[Dict]:
        """Search product by name and return pricing info"""
        product = self.session.query(Product).filter(
            Product.name.ilike(f"%{product_name}%")
        ).first()
        
        if product:
            return self.get_product_pricing(product)
        return None
    
    def close(self):
        """Close database session"""
        self.session.close()

def demo_with_real_data():
    """Demo with your actual database products"""
    print("🚀 ZUS COFFEE REAL-TIME CALCULATOR DEMO")
    print("=" * 50)
    
    calculator = ZUSRealTimeCalculator()
    
    try:
        # Get a product from database
        product = calculator.session.query(Product).first()
        if product:
            pricing = calculator.get_product_pricing(product)
            print("📱 Product Pricing Response:")
            print(f"   {pricing['chat_response']}")
            print()
            
            # Demo cart calculation
            cart_items = [
                CartItem(product_id=product.id, quantity=2)
            ]
            
            cart_total = calculator.calculate_cart_total(cart_items)
            print("🛒 Cart Calculation:")
            print(f"   {cart_total['chat_summary']}")
            print()
            
            # Demo promo code
            cart_with_promo = calculator.apply_promo_code(cart_total, 'WELCOME10')
            if 'promo_applied' in cart_with_promo:
                print("🎫 Promo Code Applied:")
                print(f"   {cart_with_promo['promo_chat_response']}")
                print(f"   New Total: {cart_with_promo['final_total_display']}")
        else:
            print("❌ No products found in database")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        calculator.close()

if __name__ == "__main__":
    demo_with_real_data()
