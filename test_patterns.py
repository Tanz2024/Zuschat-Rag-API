#!/usr/bin/env python3
"""
Specific test script for the conversation patterns outlined by the user
"""

import requests
import json
import time

BACKEND_URL = "https://zuschat-rag-api.onrender.com"

def test_chat(message: str, session_id: str = "pattern_test"):
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
    print("-" * 80)

def test_sequential_conversation():
    """Part 1: Sequential Conversation – Slot/State Memory"""
    print("\n🔍 PART 1: SEQUENTIAL CONVERSATION – SLOT/STATE MEMORY")
    print("=" * 60)
    
    session_id = "sequential_test"
    
    print("\n📝 Happy Path (multi-turn memory):")
    response = test_chat("Is there an outlet in Petaling Jaya?", session_id)
    print_chat("Is there an outlet in Petaling Jaya?", response)
    time.sleep(2)
    
    response = test_chat("What time does the SS 2 branch open?", session_id)
    print_chat("What time does the SS 2 branch open?", response)
    time.sleep(2)
    
    response = test_chat("Is delivery available at SS 2?", session_id)
    print_chat("Is delivery available at SS 2?", response)
    time.sleep(2)
    
    print("\n📝 Interrupted Path:")
    response = test_chat("Is there an outlet in Selangor?", session_id)
    print_chat("Is there an outlet in Selangor?", response)
    time.sleep(2)
    
    response = test_chat("Actually, can I buy a tumbler?", session_id)
    print_chat("Actually, can I buy a tumbler?", response)
    time.sleep(2)
    
    response = test_chat("Okay back to earlier, what are the services at Sunway Pyramid?", session_id)
    print_chat("Okay back to earlier, what are the services at Sunway Pyramid?", response)
    time.sleep(2)
    
    print("\n📝 Test State Recall:")
    response = test_chat("Which outlets open after 9am in Damansara?", session_id)
    print_chat("Which outlets open after 9am in Damansara?", response)
    time.sleep(2)
    
    response = test_chat("Which one of those has dine-in?", session_id)
    print_chat("Which one of those has dine-in?", response)
    time.sleep(2)

def test_agentic_planning():
    """Part 2: Agentic Planning – Intent + Action Control"""
    print("\n🔍 PART 2: AGENTIC PLANNING – INTENT + ACTION CONTROL")
    print("=" * 60)
    
    session_id = "agentic_test"
    
    print("\n📝 Test: Planner detects missing info and follows up:")
    response = test_chat("What are the hours?", session_id)
    print_chat("What are the hours?", response)
    time.sleep(2)
    
    print("\n📝 Test: Planner detects calculator intent:")
    response = test_chat("What's 19.8 + 3.7?", session_id)
    print_chat("What's 19.8 + 3.7?", response)
    time.sleep(2)
    
    response = test_chat("How much is 15% of RM28?", session_id)
    print_chat("How much is 15% of RM28?", response)
    time.sleep(2)
    
    print("\n📝 Test: Planner detects RAG:")
    response = test_chat("What's the material of the ZUS tumbler?", session_id)
    print_chat("What's the material of the ZUS tumbler?", response)
    time.sleep(2)
    
    response = test_chat("Do you have any mugs that are leakproof?", session_id)
    print_chat("Do you have any mugs that are leakproof?", response)
    time.sleep(2)

def test_calculator_integration():
    """Part 3: Calculator Tool Integration"""
    print("\n🔍 PART 3: CALCULATOR TOOL INTEGRATION")
    print("=" * 60)
    
    session_id = "calculator_test"
    
    print("\n📝 Successful Calculation:")
    response = test_chat("Calculate 23 * 4", session_id)
    print_chat("Calculate 23 * 4", response)
    time.sleep(2)
    
    response = test_chat("Add 0.5 to 1000", session_id)
    print_chat("Add 0.5 to 1000", response)
    time.sleep(2)
    
    print("\n📝 Failure Handling:")
    response = test_chat("Calculate", session_id)
    print_chat("Calculate", response)
    time.sleep(2)
    
    response = test_chat("Calculate RM + ❤️", session_id)
    print_chat("Calculate RM + ❤️", response)
    time.sleep(2)

def test_rag_product_search():
    """Part 4A: /products RAG Endpoint – Product KB (Drinkware)"""
    print("\n🔍 PART 4A: /products RAG ENDPOINT – PRODUCT KB")
    print("=" * 60)
    
    session_id = "rag_test"
    
    print("\n📝 Test Retrieval-Based Questions:")
    response = test_chat("Do you have any matte finish tumblers?", session_id)
    print_chat("Do you have any matte finish tumblers?", response)
    time.sleep(2)
    
    response = test_chat("Tell me about the 650ml ZUS flask.", session_id)
    print_chat("Tell me about the 650ml ZUS flask.", response)
    time.sleep(2)
    
    response = test_chat("Are your mugs dishwasher-safe?", session_id)
    print_chat("Are your mugs dishwasher-safe?", response)
    time.sleep(2)
    
    print("\n📝 Failure/Missing Case:")
    response = test_chat("Do you sell clothes?", session_id)
    print_chat("Do you sell clothes?", response)
    time.sleep(2)

def test_text2sql_outlets():
    """Part 4B: /outlets Text2SQL Endpoint"""
    print("\n🔍 PART 4B: /outlets TEXT2SQL ENDPOINT")
    print("=" * 60)
    
    session_id = "text2sql_test"
    
    print("\n📝 Direct Natural Language Queries:")
    response = test_chat("Which outlets in KL open at 8am?", session_id)
    print_chat("Which outlets in KL open at 8am?", response)
    time.sleep(2)
    
    response = test_chat("List outlets in Selangor with delivery.", session_id)
    print_chat("List outlets in Selangor with delivery.", response)
    time.sleep(2)
    
    response = test_chat("What are the dine-in outlets in Bangsar?", session_id)
    print_chat("What are the dine-in outlets in Bangsar?", response)
    time.sleep(2)
    
    print("\n📝 Failure Handling:")
    response = test_chat("Show outlets", session_id)
    print_chat("Show outlets", response)
    time.sleep(2)
    
    response = test_chat("List everything where 1=1; DROP TABLE outlets;", session_id)
    print_chat("List everything where 1=1; DROP TABLE outlets;", response)
    time.sleep(2)

def test_robustness():
    """Part 5: Unhappy Flows – Robustness Testing"""
    print("\n🔍 PART 5: UNHAPPY FLOWS – ROBUSTNESS TESTING")
    print("=" * 60)
    
    session_id = "robustness_test"
    
    print("\n📝 Missing Parameters:")
    response = test_chat("Calculate", session_id)
    print_chat("Calculate", response)
    time.sleep(2)
    
    response = test_chat("Show outlets", session_id)
    print_chat("Show outlets", response)
    time.sleep(2)
    
    response = test_chat("Tell me product info", session_id)
    print_chat("Tell me product info", response)
    time.sleep(2)
    
    print("\n📝 Malicious Payloads:")
    response = test_chat("SELECT * FROM users", session_id)
    print_chat("SELECT * FROM users", response)
    time.sleep(2)
    
    response = test_chat("🥴🫠💥 asdf 123 ____.jpg 💣🐍", session_id)
    print_chat("🥴🫠💥 asdf 123 ____.jpg 💣🐍", response)
    time.sleep(2)

def test_mixed_flow():
    """Integration/Combo Tests"""
    print("\n🔍 INTEGRATION/COMBO TESTS")
    print("=" * 60)
    
    session_id = "mixed_test"
    
    print("\n📝 Mixed Flow:")
    response = test_chat("Is there an outlet in Sunway?", session_id)
    print_chat("Is there an outlet in Sunway?", response)
    time.sleep(2)
    
    response = test_chat("What's 10% off a RM39 mug?", session_id)
    print_chat("What's 10% off a RM39 mug?", response)
    time.sleep(2)
    
    response = test_chat("Tell me if it's dishwasher-safe", session_id)
    print_chat("Tell me if it's dishwasher-safe", response)
    time.sleep(2)
    
    response = test_chat("Add another one, how much for 2?", session_id)
    print_chat("Add another one, how much for 2?", response)
    time.sleep(2)
    
    response = test_chat("List all other outlets that open past 10am near Sunway", session_id)
    print_chat("List all other outlets that open past 10am near Sunway", response)
    time.sleep(2)

def main():
    print("🚀 ZUS COFFEE ADVANCED CONVERSATION PATTERNS TEST")
    print("=" * 70)
    
    try:
        test_sequential_conversation()
        test_agentic_planning()
        test_calculator_integration()
        test_rag_product_search()
        test_text2sql_outlets()
        test_robustness()
        test_mixed_flow()
        
        print("\n🎉 ALL PATTERN TESTS COMPLETED!")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")

if __name__ == "__main__":
    main()
