#!/usr/bin/env python3
"""
Chatbot API Integration for Real-Time Calculations
How to integrate the calculator with your ZUS Coffee chatbot
"""

from typing import List, Dict, Optional
from zus_realtime_calculator import ZUSRealTimeCalculator, CartItem

class ChatbotCalculatorAPI:
    """API wrapper for chatbot integration"""
    
    def __init__(self):
        self.calculator = ZUSRealTimeCalculator()
    
    def get_product_info(self, product_name: str) -> Dict:
        """
        Get product information for chatbot response
        Usage: When user asks about a specific product
        """
        try:
            product_info = self.calculator.get_product_by_name(product_name)
            if product_info:
                return {
                    'success': True,
                    'response': product_info['chat_response'],
                    'pricing': product_info
                }
            else:
                return {
                    'success': False,
                    'response': f"Sorry, I couldn't find '{product_name}'. Try searching for 'ZUS Cup' or 'Tumbler'."
                }
        except Exception as e:
            return {
                'success': False,
                'response': "Sorry, I'm having trouble accessing product information right now."
            }
    
    def add_to_cart_calculation(self, cart_items: List[Dict]) -> Dict:
        """
        Calculate cart total when user adds items
        cart_items: [{'product_id': int, 'quantity': int}]
        """
        try:
            cart_items_obj = [CartItem(item['product_id'], item['quantity']) for item in cart_items]
            cart_total = self.calculator.calculate_cart_total(cart_items_obj)
            
            if cart_total.get('empty_cart'):
                return {
                    'success': True,
                    'response': cart_total['message']
                }
            
            response = cart_total['chat_summary'].replace('\\n', '\n')
            
            return {
                'success': True,
                'response': response,
                'cart_details': cart_total
            }
            
        except Exception as e:
            return {
                'success': False,
                'response': "Sorry, I couldn't calculate your cart total right now."
            }
    
    def apply_promo_code_calculation(self, cart_items: List[Dict], promo_code: str) -> Dict:
        """
        Apply promo code and recalculate
        """
        try:
            # First calculate cart
            cart_result = self.add_to_cart_calculation(cart_items)
            if not cart_result['success'] or 'cart_details' not in cart_result:
                return cart_result
            
            # Apply promo code
            cart_with_promo = self.calculator.apply_promo_code(
                cart_result['cart_details'], 
                promo_code
            )
            
            if 'promo_error' in cart_with_promo:
                return {
                    'success': False,
                    'response': cart_with_promo['promo_error']
                }
            
            if 'promo_applied' in cart_with_promo:
                response = f"{cart_with_promo['promo_chat_response']}\\n\\n"
                response += f"Updated Total: {cart_with_promo['final_total_display']}"
                
                return {
                    'success': True,
                    'response': response,
                    'cart_details': cart_with_promo
                }
            
        except Exception as e:
            return {
                'success': False,
                'response': "Sorry, I couldn't apply that promo code right now."
            }
    
    def get_pricing_comparison(self, product_name: str) -> Dict:
        """
        Get detailed pricing comparison for a product
        """
        try:
            product_info = self.calculator.get_product_by_name(product_name)
            if not product_info:
                return {
                    'success': False,
                    'response': f"Product '{product_name}' not found."
                }
            
            if product_info['has_discount']:
                response = f"💰 **{product_info['name']}**\\n"
                response += f"Sale Price: {product_info['price_display']}\\n"
                response += f"Regular Price: {product_info['regular_price_display']}\\n"
                response += f"Your Savings: {product_info['savings_text']}"
            else:
                response = f"☕ **{product_info['name']}**\\n"
                response += f"Price: {product_info['price_display']}"
                
                if product_info.get('promotion'):
                    response += f"\\nSpecial Offer: {product_info['promotion']}"
            
            return {
                'success': True,
                'response': response,
                'pricing': product_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'response': "Sorry, I couldn't get pricing information right now."
            }
    
    def close(self):
        """Clean up resources"""
        self.calculator.close()

# Example chatbot conversation flows
def demo_chatbot_flows():
    """Demonstrate how the calculator works in chatbot conversations"""
    
    print("🤖 ZUS COFFEE CHATBOT - REAL-TIME CALCULATION FLOWS")
    print("=" * 60)
    
    api = ChatbotCalculatorAPI()
    
    try:
        # Flow 1: User asks about a product
        print("👤 User: Tell me about the ZUS OG Cup")
        result = api.get_product_info("ZUS OG Cup")
        print(f"🤖 Bot: {result['response']}")
        print()
        
        # Flow 2: User adds items to cart
        print("👤 User: Add 2 ZUS OG Cups to my cart")
        cart_items = [{'product_id': 1, 'quantity': 2}]  # Assuming product ID 1
        cart_result = api.add_to_cart_calculation(cart_items)
        print(f"🤖 Bot: {cart_result['response']}")
        print()
        
        # Flow 3: User applies promo code
        print("👤 User: Apply promo code WELCOME10")
        promo_result = api.apply_promo_code_calculation(cart_items, "WELCOME10")
        print(f"🤖 Bot: {promo_result['response']}")
        print()
        
        # Flow 4: Pricing comparison
        print("👤 User: Show me the pricing details for ZUS Stainless Steel Mug")
        pricing_result = api.get_pricing_comparison("Stainless Steel Mug")
        print(f"🤖 Bot: {pricing_result['response']}")
        
    except Exception as e:
        print(f"❌ Error in demo: {e}")
    finally:
        api.close()

# Integration with your existing chatbot code
def integrate_with_existing_chatbot():
    """
    Example of how to integrate with your existing chatbot
    """
    print(f"\\n📋 INTEGRATION GUIDE:")
    print("=" * 30)
    
    integration_code = '''
# In your existing chatbot code:

from chatbot_calculator_api import ChatbotCalculatorAPI

class ZUSChatbot:
    def __init__(self):
        self.calculator_api = ChatbotCalculatorAPI()
    
    def handle_product_query(self, user_message):
        """Handle product-related queries"""
        if "price" in user_message.lower() or "cost" in user_message.lower():
            # Extract product name from message
            product_name = self.extract_product_name(user_message)
            result = self.calculator_api.get_product_info(product_name)
            return result['response']
    
    def handle_cart_operations(self, cart_items):
        """Handle cart calculations"""
        result = self.calculator_api.add_to_cart_calculation(cart_items)
        return result['response']
    
    def handle_promo_code(self, cart_items, promo_code):
        """Handle promo code applications"""
        result = self.calculator_api.apply_promo_code_calculation(cart_items, promo_code)
        return result['response']
    
    def cleanup(self):
        """Clean up when chatbot session ends"""
        self.calculator_api.close()
'''
    
    print(integration_code)

if __name__ == "__main__":
    demo_chatbot_flows()
    integrate_with_existing_chatbot()
    
    print(f"\\n✅ REAL-TIME CALCULATION BENEFITS:")
    print("   🚀 Always accurate pricing")
    print("   ⚡ Instant cart calculations") 
    print("   🎫 Flexible promo code system")
    print("   💾 No database storage needed")
    print("   🔄 Easy to update and maintain")
    print(f"\\n🎯 Your ZUS Coffee chatbot now has real-time calculations!")
