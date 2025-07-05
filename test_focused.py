#!/usr/bin/env python3
"""
Quick focused test of ZUS Coffee Enhanced Chatbot key patterns
"""

import requests
import json
import time

BACKEND_URL = "https://zuschat-rag-api.onrender.com"

def test_chat(message: str, session_id: str = "test_focused"):
    """Send a chat message and return the response."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": message, "session_id": session_id},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        return result
    except Exception as e:
        return {"error": str(e)}

def print_chat(message: str, response: dict):
    """Print formatted conversation exchange."""
    print(f"\n🧑‍💻 User: {message}")
    bot_message = response.get('message', response.get('response', response.get('error', 'No response')))
    print(f"🤖 Bot: {bot_message}")
    if 'intent' in response and response['intent']:
        print(f"🎯 Intent: {response['intent']}")
    if 'action' in response and response['action']:
        print(f"⚡ Action: {response['action']}")
    if 'calculation_result' in response and response['calculation_result']:
        print(f"🧮 Calculation: {response['calculation_result']}")
    print("-" * 80)

def main():
    print("🚀 ZUS COFFEE ENHANCED CHATBOT - FOCUSED TESTING")
    print("=" * 60)
    
    # Test basic greeting
    response = test_chat("Hello!")
    print_chat("Hello!", response)
    time.sleep(2)
    
    # Test product inquiry
    response = test_chat("What coffee products do you have?")
    print_chat("What coffee products do you have?", response)
    time.sleep(2)
    
    # Test calculation
    response = test_chat("Calculate 15.50 + 8.90")
    print_chat("Calculate 15.50 + 8.90", response)
    time.sleep(2)
    
    # Test outlet search
    response = test_chat("Find outlets in Kuala Lumpur")
    print_chat("Find outlets in Kuala Lumpur", response)
    time.sleep(2)
    
    # Test multi-turn conversation
    response = test_chat("What's the price?")
    print_chat("What's the price?", response)
    time.sleep(2)
    
    # Test context switch
    response = test_chat("Calculate 20% of RM 50")
    print_chat("Calculate 20% of RM 50", response)
    time.sleep(2)
    
    # Test error handling
    response = test_chat("asdfghjkl")
    print_chat("asdfghjkl", response)
    time.sleep(2)
    
    # Test malicious input
    response = test_chat("DROP TABLE products;")
    print_chat("DROP TABLE products;", response)
    time.sleep(2)
    
    print("\n🎉 FOCUSED TESTING COMPLETED!")

if __name__ == "__main__":
    main()
