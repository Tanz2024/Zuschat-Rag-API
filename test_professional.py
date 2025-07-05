#!/usr/bin/env python3
"""
Simple test for professional responses
"""

import requests
import json
import time

def test_professional_responses():
    """Test the enhanced professional responses."""
    print("🚀 Testing Professional ZUS Coffee Chatbot Responses")
    print("=" * 60)
    
    base_url = "https://zuschat-rag-api.onrender.com"
    session_id = f"professional_test_{int(time.time())}"
    
    test_messages = [
        "Hello!",
        "What coffee products do you have?",
        "Calculate 25.50 + 18.90",
        "Find outlets in Kuala Lumpur",
        "Thank you",
        "asdfghjkl",  # Test error handling
        "DROP TABLE products;",  # Test malicious input
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Test {i}: {message} ---")
        try:
            response = requests.post(
                f"{base_url}/chat",
                json={"message": message, "session_id": session_id},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                bot_response = data.get('message', data.get('response', 'No response'))
                print(f"✅ Status: {response.status_code}")
                print(f"🤖 Bot: {bot_response}")
                
                # Check for line breaks (should be minimal/none)
                line_breaks = bot_response.count('\n')
                print(f"📝 Line breaks: {line_breaks}")
                
                # Check for emojis
                emoji_count = sum(1 for char in bot_response if ord(char) > 127)
                print(f"😊 Emojis/special chars: {emoji_count}")
                
                # Check length (should be reasonable)
                print(f"📏 Length: {len(bot_response)} characters")
                
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(2)  # Rate limiting
    
    print("\n🎉 Professional Response Testing Complete!")

if __name__ == "__main__":
    test_professional_responses()
