#!/usr/bin/env python3
"""
Professional Response Formatter for ZUS Coffee Chatbot
Enhances responses to be production-ready, professional, and conversational
without line breaks while maintaining friendliness.
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
            return "Welcome back to ZUS Coffee! How can I assist you today? I'm here to help with product recommendations, outlet locations, pricing calculations, and any questions about our services."
        else:
            return "Hello and welcome to ZUS Coffee! I'm your AI assistant, ready to help you explore our premium drinkware collection, find nearby outlets with their hours and services, calculate pricing and taxes, or answer any questions about ZUS Coffee. What would you like to know today?"
    
    @staticmethod
    def format_farewell() -> str:
        """Format farewell message."""
        return "Thank you for choosing ZUS Coffee! Have a wonderful day and we look forward to serving you again soon. Don't forget to check out our latest products and visit our outlets for the best coffee experience!"
    
    @staticmethod
    def format_outlet_list(outlets: List[Dict], location: str = "") -> str:
        """Format outlet list in a conversational way."""
        if not outlets:
            return "I couldn't find any ZUS Coffee outlets matching your search criteria. Could you try specifying a more specific location like KLCC, Pavilion KL, Sunway Pyramid, or mention your preferred area? I'll help you find the perfect outlet nearby!"
        
        location_text = f" in {location}" if location else ""
        response = f"Great! I found {len(outlets)} ZUS Coffee outlet{'s' if len(outlets) > 1 else ''}{location_text} for you: "
        
        outlet_details = []
        for i, outlet in enumerate(outlets, 1):
            details = f"{i}. **{outlet['name']}** - {outlet['address']}"
            
            # Add hours if available
            hours = outlet.get('opening_hours', {})
            if hours and isinstance(hours, dict):
                today = ProfessionalResponseFormatter._get_today_hours(hours)
                if today:
                    details += f" | {today}"
            
            # Add services if available
            services = outlet.get('services', [])
            if services:
                if isinstance(services, list) and services:
                    details += f" Services: {', '.join(services[:3])}"
            
            outlet_details.append(details)
        
        response += " | ".join(outlet_details)
        response += " Would you like more details about any of these outlets, such as contact information or specific services?"
        
        return response
    
    @staticmethod
    def format_outlet_hours(outlets: List[Dict]) -> str:
        """Format outlet hours in a conversational way."""
        if not outlets:
            return "I don't have specific hour information available right now. Could you specify which outlet you're interested in? I'll help you find their exact operating hours!"
        
        response = f"Here are the operating hours for our ZUS Coffee outlet{'s' if len(outlets) > 1 else ''}: "
        
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
        response += " For the most up-to-date hours or holiday schedules, feel free to call the outlet directly or ask me about specific days!"
        
        return response
    
    @staticmethod
    def format_product_list(products: List[Dict], user_context: str = "") -> str:
        """Format product list in a conversational way."""
        try:
            if not products:
                return "I couldn't find products matching your criteria right now. Try asking about our popular items like 'tumblers', 'coffee mugs', 'travel cups', or specific features like 'dishwasher safe' or 'double wall insulation'. I'm here to help you find the perfect ZUS drinkware!"
            
            response = f"Excellent choice! Here are {len(products)} fantastic ZUS Coffee product{'s' if len(products) > 1 else ''} I'd recommend: "
            
            product_details = []
            for i, product in enumerate(products, 1):
                try:
                    detail = f"{i}. **{product.get('name', 'Premium Product')}**"
                    
                    # Price information
                    price = product.get('price', {})
                    regular_price = price.get('regular_price_myr')
                    special_price = price.get('special_price_myr')
                    
                    if regular_price and special_price and regular_price != special_price:
                        detail += f" Special price RM{special_price} (originally RM{regular_price}) - Great savings!"
                    elif regular_price:
                        detail += f" RM{regular_price}"
                    elif special_price:
                        detail += f" RM{special_price}"
                    
                    # Category
                    category = product.get('category', '')
                    if category:
                        detail += f" | {category}"
                    
                    # Description
                    description = product.get('description', '')
                    if description:
                        # Keep description concise for conversational flow
                        short_desc = description[:100] + "..." if len(description) > 100 else description
                        detail += f" | {short_desc}"
                    
                    product_details.append(detail)
                except Exception as e:
                    # Skip malformed products but continue processing
                    continue
            
            if product_details:
                response += " | ".join(product_details)
                response += " Would you like more details about any of these products, or shall I help you find something specific?"
            else:
                response = "I found some products but couldn't format them properly. Could you try asking about specific product types or features? I'll help you find exactly what you're looking for!"
            
            return response
        except Exception as e:
            return "I'm having trouble retrieving product information right now. Please try asking about specific products like 'tumblers', 'mugs', or 'travel cups', and I'll do my best to help you find what you need!"
    
    @staticmethod
    def format_pricing_calculation(calculations: Dict[str, Any]) -> str:
        """Format pricing calculations in a conversational way."""
        try:
            if not calculations:
                return "I couldn't calculate pricing information right now. Could you specify which products you're interested in? I'll help you get accurate pricing including taxes and any applicable discounts!"
            
            response = "Here's your pricing breakdown: "
            
            # Base pricing
            subtotal = calculations.get('subtotal', 0)
            tax = calculations.get('tax', 0)
            total = calculations.get('total', 0)
            
            if subtotal > 0:
                response += f"Subtotal: RM{subtotal:.2f}"
                
                if tax > 0:
                    response += f" | Tax: RM{tax:.2f}"
                
                response += f" | **Total: RM{total:.2f}**"
                
                # Add discount info if available
                discount = calculations.get('discount', 0)
                if discount > 0:
                    response += f" (You saved RM{discount:.2f}!)"
            
            # Add payment options or additional info
            response += " This pricing includes applicable taxes. Would you like me to help you find the nearest outlet to purchase these items?"
            
            return response
        except Exception as e:
            return "I'm having trouble calculating pricing right now. Could you specify which products you're interested in? I'll help you get accurate pricing information!"
    
    @staticmethod
    def format_error_message(error_type: str = "general") -> str:
        """Format error messages in a helpful way."""
        error_messages = {
            "product_not_found": "I couldn't find that specific product in our current collection. Could you try asking about our popular categories like 'tumblers', 'mugs', 'travel cups', or mention specific features you're looking for? I'm here to help you find the perfect drinkware!",
            "outlet_not_found": "I couldn't locate outlets matching your search. Could you try specifying a more specific location like 'KLCC', 'Pavilion KL', 'Sunway Pyramid', or mention your preferred area? I'll help you find the nearest ZUS Coffee outlet!",
            "calculation_error": "I'm having trouble with that calculation right now. Could you specify which products and quantities you're interested in? I'll help you get accurate pricing information!",
            "general": "I'm having a bit of trouble with that request. Could you try rephrasing your question or ask about our products, outlets, or services? I'm here to help with anything related to ZUS Coffee!"
        }
        
        return error_messages.get(error_type, error_messages["general"])
    
    @staticmethod
    def enhance_response(response: str) -> str:
        """Apply general enhancements to responses."""
        if not response:
            return "I'm here to help with anything related to ZUS Coffee! Feel free to ask about our products, outlets, pricing, or services."
        
        # Remove excessive line breaks and normalize spacing
        response = re.sub(r'\n\s*\n', ' ', response)
        response = re.sub(r'\s+', ' ', response)
        
        # Ensure proper sentence structure
        response = response.strip()
        if response and not response.endswith(('.', '!', '?')):
            response += "!"
        
        return response
    
    @staticmethod
    def _get_today_hours(hours: Dict) -> str:
        """Get today's hours from hours dictionary."""
        import datetime
        
        try:
            today = datetime.datetime.now().strftime("%A").lower()
            
            if today in hours:
                day_hours = hours[today]
                if isinstance(day_hours, dict):
                    open_time = day_hours.get('open', '')
                    close_time = day_hours.get('close', '')
                    if open_time and close_time:
                        return f"Today: {open_time} - {close_time}"
                elif isinstance(day_hours, str):
                    return f"Today: {day_hours}"
            
            return "Hours available upon request"
        except Exception:
            return "Hours available upon request"
