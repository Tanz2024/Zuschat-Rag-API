#!/usr/bin/env python3
"""
Real-Time Calculation Service for ZUS Coffee Chatbot
Calculates pricing, discounts, and cart totals on-the-fly
"""

import json
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ProductInfo:
    """Product information for calculations"""
    id: int
    name: str
    price: str  # "RM 55.00"
    sale_price: float  # 55.0
    regular_price: Optional[str] = None  # "RM 79.00"
    discount: Optional[str] = None  # "30%"
    promotion: Optional[str] = None  # "Buy 1 Free 1"
    on_sale: Optional[bool] = None

class RealTimePriceCalculator:
    """Real-time price and discount calculator"""
    
    def __init__(self, tax_rate: float = 6.0):  # 6% SST for Malaysia
        self.tax_rate = tax_rate
    
    def parse_price(self, price_str: str) -> float:
        """Convert price string to float"""
        try:
            if not price_str:
                return 0.0
            # Remove "RM " and any commas, convert to float
            return float(price_str.replace('RM ', '').replace(',', '').strip())
        except (ValueError, AttributeError, TypeError) as e:
            # Return 0.0 for any parsing errors to prevent 500 errors
            return 0.0
    
    def calculate_discount(self, product: ProductInfo) -> Dict:
        """Calculate discount information for a product"""
        try:
            current_price = product.sale_price
            
            # Try to get regular price
            regular_price = None
            if product.regular_price:
                regular_price = self.parse_price(product.regular_price)
            
            # Calculate discount if regular price exists and is higher
            if regular_price and regular_price > current_price:
                discount_amount = regular_price - current_price
                discount_percentage = (discount_amount / regular_price) * 100
                
                return {
                    'has_discount': True,
                    'regular_price': regular_price,
                    'current_price': current_price,
                    'discount_amount': round(discount_amount, 2),
                    'discount_percentage': round(discount_percentage, 1),
                    'savings_display': f"Save RM {discount_amount:.2f} ({discount_percentage:.0f}% off)",
                    'price_display': f"RM {current_price:.2f}",
                    'regular_price_display': f"RM {regular_price:.2f}"
                }
            
            return {
                'has_discount': False,
                'current_price': current_price,
                'price_display': f"RM {current_price:.2f}",
                'regular_price_display': None,
                'savings_display': None
            }
        except Exception as e:
            # Return safe fallback for any calculation errors
            return {
                'has_discount': False,
                'current_price': 0.0,
                'price_display': "RM 0.00",
                'regular_price_display': None,
                'savings_display': None,
                'error': str(e)
            }
    
    def get_product_pricing_info(self, product: ProductInfo) -> Dict:
        """Get complete pricing information for chatbot responses"""
        try:
            discount_info = self.calculate_discount(product)
            
            # Enhanced info for chatbot
            pricing_info = {
                **discount_info,
                'product_name': product.name,
                'promotion': product.promotion,
                'is_on_sale': product.on_sale or discount_info['has_discount']
            }
            
            # Generate chatbot-friendly text
            if discount_info['has_discount']:
                pricing_info['chat_text'] = (
                    f"{product.name} is on sale for {discount_info['price_display']} "
                    f"(was {discount_info['regular_price_display']}) - "
                    f"{discount_info['savings_display']}!"
                )
            elif product.promotion:
                pricing_info['chat_text'] = (
                    f"{product.name} for {discount_info['price_display']} "
                    f"with special promotion: {product.promotion}!"
                )
            else:
                pricing_info['chat_text'] = f"{product.name} for {discount_info['price_display']}"
            
            return pricing_info
        except Exception as e:
            # Return safe fallback for any pricing info errors
            return {
                'has_discount': False,
                'current_price': 0.0,
                'price_display': "RM 0.00",
                'product_name': getattr(product, 'name', 'Unknown Product'),
                'promotion': None,
                'is_on_sale': False,
                'chat_text': f"{getattr(product, 'name', 'Product')} - pricing information temporarily unavailable",
                'error': str(e)
            }

class RealTimeCartCalculator:
    """Real-time cart and checkout calculator"""
    
    def __init__(self, tax_rate: float = 6.0):
        self.tax_rate = tax_rate
        self.price_calculator = RealTimePriceCalculator(tax_rate)
    
    def calculate_cart_totals(self, cart_items: List[Dict]) -> Dict:
        """
        Calculate cart totals in real-time
        cart_items: [{'product': ProductInfo, 'quantity': int}]
        """
        subtotal = 0.0
        total_savings = 0.0
        item_details = []
        
        for item in cart_items:
            product = item['product']
            quantity = item['quantity']
            
            # Get pricing info
            pricing = self.price_calculator.get_product_pricing_info(product)
            
            # Calculate line totals
            line_total = pricing['current_price'] * quantity
            subtotal += line_total
            
            # Calculate line savings
            line_savings = 0.0
            if pricing['has_discount']:
                line_savings = pricing['discount_amount'] * quantity
                total_savings += line_savings
            
            # Add to item details
            item_details.append({
                'product_name': product.name,
                'price': pricing['price_display'],
                'quantity': quantity,
                'line_total': f"RM {line_total:.2f}",
                'line_savings': f"RM {line_savings:.2f}" if line_savings > 0 else None,
                'has_promotion': bool(product.promotion),
                'promotion_text': product.promotion
            })
        
        # Calculate tax
        tax_amount = (subtotal * self.tax_rate) / 100
        final_total = subtotal + tax_amount
        
        return {
            'items': item_details,
            'item_count': len(cart_items),
            'total_quantity': sum(item['quantity'] for item in cart_items),
            'subtotal': round(subtotal, 2),
            'subtotal_display': f"RM {subtotal:.2f}",
            'total_savings': round(total_savings, 2),
            'savings_display': f"RM {total_savings:.2f}" if total_savings > 0 else None,
            'tax_rate': self.tax_rate,
            'tax_amount': round(tax_amount, 2),
            'tax_display': f"RM {tax_amount:.2f}",
            'final_total': round(final_total, 2),
            'final_total_display': f"RM {final_total:.2f}"
        }
    
    def apply_promo_code(self, cart_totals: Dict, promo_code: str) -> Dict:
        """Apply promotional codes in real-time"""
        promo_codes = {
            'WELCOME10': {'discount': 0.10, 'description': '10% off for new customers'},
            'STUDENT15': {'discount': 0.15, 'description': '15% off for students'},
            'ZUSCOFFEE20': {'discount': 0.20, 'description': '20% off limited time'},
            'NEWBIE25': {'discount': 0.25, 'description': '25% off for first purchase'}
        }
        
        promo_code = promo_code.upper().strip()
        
        if promo_code not in promo_codes:
            return {
                **cart_totals,
                'promo_error': f"Invalid promo code: {promo_code}"
            }
        
        promo = promo_codes[promo_code]
        promo_discount = cart_totals['subtotal'] * promo['discount']
        new_subtotal = cart_totals['subtotal'] - promo_discount
        new_tax = (new_subtotal * self.tax_rate) / 100
        new_final_total = new_subtotal + new_tax
        
        return {
            **cart_totals,
            'promo_code': promo_code,
            'promo_description': promo['description'],
            'promo_discount': round(promo_discount, 2),
            'promo_discount_display': f"RM {promo_discount:.2f}",
            'subtotal_after_promo': round(new_subtotal, 2),
            'subtotal_after_promo_display': f"RM {new_subtotal:.2f}",
            'tax_amount': round(new_tax, 2),
            'tax_display': f"RM {new_tax:.2f}",
            'final_total': round(new_final_total, 2),
            'final_total_display': f"RM {new_final_total:.2f}",
            'total_discount': round(cart_totals['total_savings'] + promo_discount, 2)
        }

class ChatbotPricingHelper:
    """Helper class to generate chatbot-friendly pricing responses"""
    
    def __init__(self):
        self.calculator = RealTimePriceCalculator()
    
    def get_product_response(self, product_data: Dict) -> str:
        """Generate chatbot response for a single product"""
        product = ProductInfo(
            id=product_data.get('id', 0),
            name=product_data['name'],
            price=product_data['price'],
            sale_price=product_data['sale_price'],
            regular_price=product_data.get('regular_price'),
            discount=product_data.get('discount'),
            promotion=product_data.get('promotion'),
            on_sale=product_data.get('on_sale')
        )
        
        pricing = self.calculator.get_product_pricing_info(product)
        return pricing['chat_text']
    
    def get_cart_summary_response(self, cart_totals: Dict) -> str:
        """Generate chatbot response for cart summary"""
        if cart_totals['item_count'] == 0:
            return "Your cart is empty. Would you like to browse our products?"
        
        response = f"Your cart has {cart_totals['total_quantity']} items:\n"
        response += f"Subtotal: {cart_totals['subtotal_display']}\n"
        
        if cart_totals['savings_display']:
            response += f"You're saving: {cart_totals['savings_display']}\n"
        
        response += f"Tax (6% SST): {cart_totals['tax_display']}\n"
        response += f"Total: {cart_totals['final_total_display']}"
        
        return response

# Example usage functions
def demo_real_time_calculations():
    """Demonstrate real-time calculations with your actual product data"""
    
    # Sample product from your data
    sample_product = {
        'id': 1,
        'name': 'ZUS OG CUP 2.0 With Screw-On Lid 500ml (17oz)',
        'price': 'RM 55.00',
        'sale_price': 55.0,
        'regular_price': 'RM 79.00',
        'on_sale': True
    }
    
    # Initialize calculator
    chatbot_helper = ChatbotPricingHelper()
    cart_calculator = RealTimeCartCalculator()
    
    # Get product pricing response
    product_response = chatbot_helper.get_product_response(sample_product)
    print("🤖 Chatbot Product Response:")
    print(f"   {product_response}")
    
    # Calculate cart with multiple items
    cart_items = [
        {
            'product': ProductInfo(**sample_product),
            'quantity': 2
        }
    ]
    
    cart_totals = cart_calculator.calculate_cart_totals(cart_items)
    cart_response = chatbot_helper.get_cart_summary_response(cart_totals)
    
    print(f"\n🛒 Cart Calculation (Real-time):")
    print(f"   {cart_response}")
    
    # Apply promo code
    cart_with_promo = cart_calculator.apply_promo_code(cart_totals, 'WELCOME10')
    
    print(f"\n🎫 With Promo Code 'WELCOME10':")
    print(f"   Promo Discount: {cart_with_promo['promo_discount_display']}")
    print(f"   New Total: {cart_with_promo['final_total_display']}")

if __name__ == "__main__":
    print("🚀 REAL-TIME CALCULATION SERVICE FOR ZUS COFFEE CHATBOT")
    print("=" * 60)
    print("✅ No database storage needed")
    print("✅ All calculations done on-the-fly") 
    print("✅ Always accurate and up-to-date")
    print("✅ Flexible for promotions and discounts")
    print()
    
    demo_real_time_calculations()
