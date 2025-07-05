#!/usr/bin/env python3
"""
Professional Response Formatter for ZUS Coffee Chatbot
Enhances responses to be more production-ready, professional, and conversational
without line breaks while maintaining friendliness and emoji usage.
"""

import re
from typing import Dict, Any, List

class ProfessionalResponseFormatter:
    """
    Professional response formatter that creates conversational, 
    single-flow responses without line breaks.
    """
    
    @staticmethod
    def format_greeting(is_returning_user: bool = False) -> str:
        """Format greeting message."""
        if is_returning_user:
            return "👋 Welcome back to ZUS Coffee! How can I assist you today? I'm here to help with product recommendations, outlet locations, pricing calculations, and any questions about our services."
        else:
            return "🎉 Hello and welcome to ZUS Coffee! I'm your friendly AI assistant, ready to help you explore our premium drinkware collection, find nearby outlets with their hours and services, calculate pricing and taxes, or answer any questions about ZUS Coffee. What would you like to know today?"
    
    @staticmethod
    def format_farewell() -> str:
        """Format farewell message."""
        return "☕ Thank you for choosing ZUS Coffee! Have a wonderful day and we look forward to serving you again soon. Don't forget to check out our latest products and visit our outlets for the best coffee experience! 🌟"
    
    @staticmethod
    def format_outlet_list(outlets: List[Dict], location: str = "") -> str:
        """Format outlet list in a conversational way."""
        if not outlets:
            return "🔍 I couldn't find any ZUS Coffee outlets matching your search criteria. Could you try specifying a more specific location like KLCC, Pavilion KL, Sunway Pyramid, or mention your preferred area? I'll help you find the perfect outlet nearby!"
        
        location_text = f" in {location}" if location else ""
        response = f"🏪 Great! I found {len(outlets)} ZUS Coffee outlet{'s' if len(outlets) > 1 else ''}{location_text} for you: "
        
        outlet_details = []
        for i, outlet in enumerate(outlets, 1):
            details = f"{i}. **{outlet['name']}** 📍 {outlet['address']}"
            
            # Add hours if available
            hours = outlet.get('opening_hours', {})
            if hours and isinstance(hours, dict):
                today = ProfessionalResponseFormatter._get_today_hours(hours)
                if today:
                    details += f" 🕒 {today}"
            
            # Add services if available
            services = outlet.get('services', [])
            if services:
                if isinstance(services, list) and services:
                    details += f" 🔧 Services: {', '.join(services[:3])}"
            
            outlet_details.append(details)
        
        response += " | ".join(outlet_details)
        response += " 💡 Would you like more details about any of these outlets, such as contact information or specific services?"
        
        return response
    
    @staticmethod
    def format_outlet_hours(outlets: List[Dict]) -> str:
        """Format outlet hours in a conversational way."""
        if not outlets:
            return "⏰ I don't have specific hour information available right now. Could you specify which outlet you're interested in? I'll help you find their exact operating hours!"
        
        response = f"🕒 Here are the operating hours for our ZUS Coffee outlet{'s' if len(outlets) > 1 else ''}: "
        
        hour_details = []
        for outlet in outlets:
            hours = outlet.get('opening_hours', {})
            if hours and isinstance(hours, dict):
                today_hours = ProfessionalResponseFormatter._get_today_hours(hours)
                detail = f"**{outlet['name']}** {today_hours if today_hours else 'Hours available upon request'}"
            else:
                detail = f"**{outlet['name']}** Hours available upon request"
            hour_details.append(detail)
        
        response += " | ".join(hour_details)
        response += " 📞 For the most up-to-date hours or holiday schedules, feel free to call the outlet directly or ask me about specific days!"
        
        return response
    
    @staticmethod
    def format_product_list(products: List[Dict], user_context: str = "") -> str:
        """Format product list in a conversational way."""
        if not products:
            return "🔍 I couldn't find products matching your criteria right now. Try asking about our popular items like 'tumblers', 'coffee mugs', 'travel cups', or specific features like 'dishwasher safe' or 'double wall insulation'. I'm here to help you find the perfect ZUS drinkware!"
        
        response = f"☕ Excellent choice! Here are {len(products)} fantastic ZUS Coffee product{'s' if len(products) > 1 else ''} I'd recommend: "
        
        product_details = []
        for i, product in enumerate(products, 1):
            detail = f"{i}. **{product.get('name', 'Premium Product')}**"
            
            # Price information
            price = product.get('price', 'Contact for pricing')
            sale_price = product.get('sale_price')
            regular_price = product.get('regular_price')
            
            if sale_price and regular_price:
                try:
                    reg_price_num = float(str(regular_price).replace('RM ', '').replace(',', ''))
                    if sale_price < reg_price_num:
                        detail += f" 💰 Special price {price} (originally {regular_price}) - Great savings!"
                    else:
                        detail += f" 💰 {price}"
                except:
                    detail += f" 💰 {price}"
            else:
                detail += f" 💰 {price}"
            
            # Key features
            features = product.get('features', [])
            if features and isinstance(features, list):
                detail += f" ✨ {', '.join(features[:2])}"
            
            # Capacity and material
            capacity = product.get('capacity')
            material = product.get('material')
            if capacity:
                detail += f" 📏 {capacity}"
            if material:
                detail += f" 🧱 {material}"
            
            product_details.append(detail)
        
        response += " | ".join(product_details)
        response += " 🛒 Would you like more details about any of these products, or shall I help you with pricing calculations?"
        
        return response
    
    @staticmethod
    def format_calculation_result(expression: str, result: str, calculation_type: str = "general") -> str:
        """Format calculation results professionally."""
        if calculation_type == "tax":
            return f"🧮 Tax calculation complete! **{expression}** equals **{result}**. This includes all applicable taxes for your convenience. Need help with anything else?"
        elif calculation_type == "discount":
            return f"💸 Discount calculation done! **{expression}** equals **{result}**. That's a great savings! Would you like me to calculate the final total with tax?"
        elif calculation_type == "cart":
            return f"🛒 Cart total calculated! **{expression}** equals **{result}**. This is your subtotal - would you like me to add tax or apply any discounts?"
        else:
            return f"🧮 Calculation complete! **{expression}** equals **{result}**. Is there anything else I can calculate for you?"
    
    @staticmethod
    def format_error_message(error_type: str = "general") -> str:
        """Format error messages professionally."""
        if error_type == "calculation":
            return "🤔 I had trouble with that calculation. Could you rephrase it using numbers and basic operations like '+', '-', '*', '/' or percentages? For example: '15% of 50' or '25.50 + 18.90'. I'm here to help!"
        elif error_type == "product":
            return "🔍 I'm having trouble accessing our product catalog right now. Could you try asking about specific items like 'coffee mugs', 'tumblers', or 'travel cups'? I'll do my best to help you find what you're looking for!"
        elif error_type == "outlet":
            return "📍 I'm having difficulty finding outlet information at the moment. Could you specify a location like 'KLCC', 'Sunway', or your preferred area? I'll help you locate the nearest ZUS Coffee outlet!"
        elif error_type == "malicious":
            return "🛡️ I can't process that type of request for security reasons. I'm here to help with ZUS Coffee products, outlet locations, calculations, and general inquiries. What would you like to know about our coffee and drinkware?"
        else:
            return "🤝 I want to help you, but I'm not quite sure what you're looking for. Could you rephrase your question? I can assist with product information, outlet locations, pricing calculations, or general ZUS Coffee inquiries!"
    
    @staticmethod
    def format_clarification_request() -> str:
        """Format clarification request."""
        return "🤝 I'd love to help you find exactly what you need! Could you please be more specific? I can assist with 🏪 outlet locations and hours, ☕ product recommendations and details, 🧮 pricing calculations and tax computations, or 💰 current promotions and offers. What interests you most?"
    
    @staticmethod
    def format_about_us() -> str:
        """Format about us response."""
        return "🏢 ZUS Coffee is Malaysia's leading tech-driven coffee chain, passionate about delivering premium coffee experiences and innovative drinkware products! 📍 We proudly operate 243 outlets across Malaysia, especially in Kuala Lumpur and Selangor, serving quality coffee and offering an amazing selection of tumblers, mugs, and cups. 🚀 We're committed to innovation, technology, and creating exceptional customer experiences. Visit zuscoffee.com to discover more about our journey and latest offerings!"
    
    @staticmethod
    def format_context_recall(context_type: str, items: List[Dict]) -> str:
        """Format context recall responses."""
        if context_type == "outlets" and items:
            return f"🔄 Based on our earlier conversation, you were interested in these outlets: {ProfessionalResponseFormatter.format_outlet_list(items)}. Would you like more specific information about any of these locations?"
        elif context_type == "products" and items:
            return f"🔄 From what we discussed earlier, you were looking at these products: {ProfessionalResponseFormatter.format_product_list(items)}. Shall I provide more details or help with calculations?"
        else:
            return "🔄 I'd be happy to continue helping you! Could you remind me what specific information you're looking for? I have access to all our outlet and product details!"
    
    @staticmethod
    def _get_today_hours(hours_dict: Dict) -> str:
        """Get today's hours from hours dictionary."""
        import datetime
        today = datetime.datetime.now().strftime('%A').lower()
        
        if today in hours_dict:
            return f"Today: {hours_dict[today]}"
        elif 'monday' in hours_dict:
            return f"Typical hours: {hours_dict['monday']}"
        else:
            return "Hours available upon request"
    
    @staticmethod
    def clean_response(response: str) -> str:
        """Clean response by removing excessive line breaks and formatting properly."""
        # Remove multiple line breaks
        response = re.sub(r'\n+', ' ', response)
        # Remove excessive spaces
        response = re.sub(r'\s+', ' ', response)
        # Clean up markdown formatting for better readability
        response = response.strip()
        return response
