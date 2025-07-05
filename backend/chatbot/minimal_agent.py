#!/usr/bin/env python3
"""
Minimal working chatbot agent for emergency fallback
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MinimalChatbotAgent:
    """Minimal chatbot that always works."""
    
    def __init__(self):
        self.sessions = {}
    
    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """Process message with minimal logic."""
        try:
            # Store session
            if session_id not in self.sessions:
                self.sessions[session_id] = {"count": 0}
            
            self.sessions[session_id]["count"] += 1
            count = self.sessions[session_id]["count"]
            
            # Generate simple response
            if "hello" in message.lower() or "hi" in message.lower():
                response = f"🎉 Hello and welcome to ZUS Coffee! I'm your friendly AI assistant, ready to help you explore our premium drinkware collection, find nearby outlets with their hours and services, calculate pricing and taxes, or answer any questions about ZUS Coffee. What would you like to know today?"
            
            elif "calculate" in message.lower() or any(op in message for op in ['+', '-', '*', '/', '%']):
                try:
                    # Simple calculation
                    import re
                    numbers = re.findall(r'\d+\.?\d*', message)
                    if len(numbers) >= 2:
                        if '+' in message:
                            result = float(numbers[0]) + float(numbers[1])
                            response = f"🧮 Calculation complete! **{numbers[0]} + {numbers[1]}** equals **{result}**. Is there anything else I can calculate for you?"
                        elif '*' in message:
                            result = float(numbers[0]) * float(numbers[1])
                            response = f"🧮 Calculation complete! **{numbers[0]} × {numbers[1]}** equals **{result}**. Is there anything else I can calculate for you?"
                        else:
                            response = "🧮 I'm ready to help with your calculations! Please provide a mathematical expression like '25.50 + 18.90', percentage calculations like '15% of 200', or let me know which products you'd like pricing calculations for."
                    else:
                        response = "🧮 I'm ready to help with your calculations! Please provide a mathematical expression like '25.50 + 18.90' or '15% of 200'."
                except:
                    response = "🤔 I had trouble with that calculation. Could you rephrase it using numbers and basic operations like '+', '-', '*', '/' or percentages? For example: '15% of 50' or '25.50 + 18.90'. I'm here to help!"
            
            elif "outlet" in message.lower() or "location" in message.lower() or "store" in message.lower():
                response = "🏪 Great! I found some ZUS Coffee outlets for you: 1. **ZUS Coffee KLCC** 📍 Lot G-316A, Ground Floor, Suria KLCC, Kuala Lumpur City Centre, 50088 Kuala Lumpur 🕒 Today: 8:00 AM - 10:00 PM | 2. **ZUS Coffee Pavilion KL** 📍 Lot 1.39.00, Level 1, Pavilion Kuala Lumpur, 168, Jalan Bukit Bintang, 55100 Kuala Lumpur 🕒 Today: 10:00 AM - 10:00 PM 💡 Would you like more details about any of these outlets, such as contact information or specific services?"
            
            elif "product" in message.lower() or "coffee" in message.lower() or "tumbler" in message.lower() or "mug" in message.lower():
                response = "☕ Excellent choice! Here are 2 fantastic ZUS Coffee products I'd recommend: 1. **ZUS Coffee Premium Tumbler** 💰 RM 25.90 ✨ Double wall insulation, Leak-proof 📏 350ml 🧱 Stainless steel | 2. **ZUS Coffee Travel Mug** 💰 RM 32.90 ✨ Spill-proof lid, Easy grip handle 📏 500ml 🧱 Ceramic with silicone grip 🛒 Would you like more details about any of these products, or shall I help you with pricing calculations?"
            
            elif "thank" in message.lower() or "bye" in message.lower() or "goodbye" in message.lower():
                response = "☕ Thank you for choosing ZUS Coffee! Have a wonderful day and we look forward to serving you again soon. Don't forget to check out our latest products and visit our outlets for the best coffee experience! 🌟"
            
            elif message.strip() == "" or len(message.strip()) < 2:
                response = "🤝 I'd love to help you find exactly what you need! Could you please be more specific? I can assist with 🏪 outlet locations and hours, ☕ product recommendations and details, 🧮 pricing calculations and tax computations, or 💰 current promotions and offers. What interests you most?"
            
            else:
                response = "🤝 I want to help you, but I'm not quite sure what you're looking for. Could you rephrase your question? I can assist with product information, outlet locations, pricing calculations, or general ZUS Coffee inquiries!"
            
            return {
                "message": response,
                "session_id": session_id,
                "intent": "general",
                "confidence": 0.8
            }
            
        except Exception as e:
            logger.error(f"Error in minimal chatbot: {e}")
            return {
                "message": "🔧 I'm experiencing some technical difficulties right now. Please try again in a moment, and I'll be happy to help you with ZUS Coffee information, outlet locations, or product recommendations!",
                "session_id": session_id,
                "error": str(e)
            }

# Global instance
_minimal_chatbot = None

def get_chatbot():
    """Get the minimal chatbot instance."""
    global _minimal_chatbot
    if _minimal_chatbot is None:
        _minimal_chatbot = MinimalChatbotAgent()
    return _minimal_chatbot
