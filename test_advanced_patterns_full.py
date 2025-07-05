#!/usr/bin/env python3
"""
Comprehensive Advanced Pattern Testing for ZUS Coffee Chatbot
Tests all specified conversation patterns including multi-turn memory,
agentic planning, calculator integration, RAG, and Text2SQL capabilities.
"""

import requests
import json
import time
from typing import Dict, Any, List

BACKEND_URL = "https://zuschat-rag-api.onrender.com"

class AdvancedPatternTester:
    def __init__(self):
        self.session_id = f"advanced_test_{int(time.time())}"
        self.conversation_log = []
    
    def chat(self, message: str, description: str = "") -> Dict[str, Any]:
        """Send a chat message and log the response."""
        try:
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json={"message": message, "session_id": self.session_id},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            # Log conversation
            entry = {
                "description": description,
                "user": message,
                "bot": result.get("message", result.get("response", "No response")),
                "intent": result.get("intent"),
                "confidence": result.get("confidence"),
                "timestamp": time.time()
            }
            self.conversation_log.append(entry)
            
            return result
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"message": f"Error: {e}"}
    
    def print_exchange(self, message: str, response: Dict[str, Any], description: str = ""):
        """Print formatted conversation exchange."""
        if description:
            print(f"\n🔍 {description}")
        print(f"👤 User: {message}")
        bot_message = response.get("message", response.get("response", "No response"))
        print(f"🤖 Bot: {bot_message}")
        
        # Check for key indicators
        if len(bot_message) == 0:
            print("⚠️  Empty response")
        elif "\n" in bot_message:
            line_count = bot_message.count('\n')
            print(f"📝 Contains {line_count} line breaks")
        
        print("-" * 80)
        time.sleep(2)  # Rate limiting

def test_part1_slot_memory(tester: AdvancedPatternTester):
    """Test Part 1: Sequential Conversation – Slot/State Memory"""
    print("\n🧠 PART 1: SEQUENTIAL CONVERSATION – SLOT/STATE MEMORY")
    print("=" * 70)
    
    print("\n📋 Happy Path (multi-turn memory):")
    
    # Test 1: Multi-turn memory
    response1 = tester.chat("Is there an outlet in Petaling Jaya?", "Initial outlet query")
    tester.print_exchange("Is there an outlet in Petaling Jaya?", response1, "Initial outlet query")
    
    response2 = tester.chat("What time does the SS 2 branch open?", "Follow-up about specific branch")
    tester.print_exchange("What time does the SS 2 branch open?", response2, "Follow-up about specific branch")
    
    response3 = tester.chat("Is delivery available at SS 2?", "Service inquiry for same branch")
    tester.print_exchange("Is delivery available at SS 2?", response3, "Service inquiry for same branch")
    
    print("\n📋 Interrupted Path:")
    
    response4 = tester.chat("Is there an outlet in Selangor?", "New location query")
    tester.print_exchange("Is there an outlet in Selangor?", response4, "New location query")
    
    response5 = tester.chat("Actually, can I buy a tumbler?", "Topic change to products")
    tester.print_exchange("Actually, can I buy a tumbler?", response5, "Topic change to products")
    
    response6 = tester.chat("Okay back to earlier, what are the services at Sunway Pyramid?", "Context recall")
    tester.print_exchange("Okay back to earlier, what are the services at Sunway Pyramid?", response6, "Context recall")
    
    print("\n📋 State Recall:")
    
    response7 = tester.chat("Which outlets open after 9am in Damansara?", "Specific time and location query")
    tester.print_exchange("Which outlets open after 9am in Damansara?", response7, "Specific time and location query")
    
    response8 = tester.chat("Which one of those has dine-in?", "Reference to previous results")
    tester.print_exchange("Which one of those has dine-in?", response8, "Reference to previous results")

def test_part2_agentic_planning(tester: AdvancedPatternTester):
    """Test Part 2: Agentic Planning – Intent + Action Control"""
    print("\n🎯 PART 2: AGENTIC PLANNING – INTENT + ACTION CONTROL")
    print("=" * 70)
    
    print("\n📋 Planner detects missing info:")
    
    response1 = tester.chat("What are the hours?", "Incomplete query - should ask for clarification")
    tester.print_exchange("What are the hours?", response1, "Incomplete query - should ask for clarification")
    
    print("\n📋 Planner detects calculator intent:")
    
    response2 = tester.chat("What's 19.8 + 3.7?", "Simple calculation")
    tester.print_exchange("What's 19.8 + 3.7?", response2, "Simple calculation")
    
    response3 = tester.chat("How much is 15% of RM28?", "Percentage calculation")
    tester.print_exchange("How much is 15% of RM28?", response3, "Percentage calculation")
    
    print("\n📋 Planner detects RAG intent:")
    
    response4 = tester.chat("What's the material of the ZUS tumbler?", "Product detail query")
    tester.print_exchange("What's the material of the ZUS tumbler?", response4, "Product detail query")
    
    response5 = tester.chat("Do you have any mugs that are leakproof?", "Product feature query")
    tester.print_exchange("Do you have any mugs that are leakproof?", response5, "Product feature query")

def test_part3_calculator(tester: AdvancedPatternTester):
    """Test Part 3: Calculator Tool Integration"""
    print("\n🧮 PART 3: CALCULATOR TOOL INTEGRATION")
    print("=" * 70)
    
    print("\n📋 Successful Calculations:")
    
    response1 = tester.chat("Calculate 23 * 4", "Multiplication")
    tester.print_exchange("Calculate 23 * 4", response1, "Multiplication")
    
    response2 = tester.chat("Add 0.5 to 1000", "Addition with decimal")
    tester.print_exchange("Add 0.5 to 1000", response2, "Addition with decimal")
    
    print("\n📋 Failure Handling:")
    
    response3 = tester.chat("Calculate", "Incomplete calculation request")
    tester.print_exchange("Calculate", response3, "Incomplete calculation request")
    
    response4 = tester.chat("Calculate RM + ❤️", "Invalid calculation")
    tester.print_exchange("Calculate RM + ❤️", response4, "Invalid calculation")

def test_part4a_rag_products(tester: AdvancedPatternTester):
    """Test Part 4A: /products RAG Endpoint – Product KB"""
    print("\n☕ PART 4A: PRODUCTS RAG ENDPOINT – PRODUCT KB")
    print("=" * 70)
    
    print("\n📋 Retrieval-Based Questions:")
    
    response1 = tester.chat("Do you have any matte finish tumblers?", "Specific product feature")
    tester.print_exchange("Do you have any matte finish tumblers?", response1, "Specific product feature")
    
    response2 = tester.chat("Tell me about the 650ml ZUS flask.", "Specific product inquiry")
    tester.print_exchange("Tell me about the 650ml ZUS flask.", response2, "Specific product inquiry")
    
    response3 = tester.chat("Are your mugs dishwasher-safe?", "Product safety feature")
    tester.print_exchange("Are your mugs dishwasher-safe?", response3, "Product safety feature")
    
    print("\n📋 Failure/Missing Case:")
    
    response4 = tester.chat("Do you sell clothes?", "Out of scope product")
    tester.print_exchange("Do you sell clothes?", response4, "Out of scope product")

def test_part4b_text2sql_outlets(tester: AdvancedPatternTester):
    """Test Part 4B: /outlets Text2SQL Endpoint"""
    print("\n🏪 PART 4B: OUTLETS TEXT2SQL ENDPOINT")
    print("=" * 70)
    
    print("\n📋 Direct Natural Language Queries:")
    
    response1 = tester.chat("Which outlets in KL open at 8am?", "Time-specific location query")
    tester.print_exchange("Which outlets in KL open at 8am?", response1, "Time-specific location query")
    
    response2 = tester.chat("List outlets in Selangor with delivery.", "Service-specific location query")
    tester.print_exchange("List outlets in Selangor with delivery.", response2, "Service-specific location query")
    
    response3 = tester.chat("What are the dine-in outlets in Bangsar?", "Service and location query")
    tester.print_exchange("What are the dine-in outlets in Bangsar?", response3, "Service and location query")
    
    print("\n📋 Failure Handling:")
    
    response4 = tester.chat("Show outlets", "Incomplete query")
    tester.print_exchange("Show outlets", response4, "Incomplete query")
    
    response5 = tester.chat("List everything where 1=1; DROP TABLE outlets;", "SQL injection attempt")
    tester.print_exchange("List everything where 1=1; DROP TABLE outlets;", response5, "SQL injection attempt")

def test_additional_robustness(tester: AdvancedPatternTester):
    """Test additional robustness patterns"""
    print("\n🛡️ ADDITIONAL ROBUSTNESS TESTING")
    print("=" * 70)
    
    print("\n📋 Missing Parameters:")
    
    response1 = tester.chat("Calculate", "Missing calculation")
    tester.print_exchange("Calculate", response1, "Missing calculation")
    
    response2 = tester.chat("Show outlets", "Missing location")
    tester.print_exchange("Show outlets", response2, "Missing location")
    
    response3 = tester.chat("Tell me product info", "Missing product details")
    tester.print_exchange("Tell me product info", response3, "Missing product details")
    
    print("\n📋 Random Garbage Input:")
    
    response4 = tester.chat("🥴🫠💥 asdf 123 ____.jpg 💣🐍", "Emoji/garbage mix")
    tester.print_exchange("🥴🫠💥 asdf 123 ____.jpg 💣🐍", response4, "Emoji/garbage mix")

def test_mixed_flow(tester: AdvancedPatternTester):
    """Test mixed conversation flow"""
    print("\n🔄 MIXED CONVERSATION FLOW")
    print("=" * 70)
    
    response1 = tester.chat("Is there an outlet in Sunway?", "Outlet query")
    tester.print_exchange("Is there an outlet in Sunway?", response1, "Outlet query")
    
    response2 = tester.chat("What's 10% off a RM39 mug?", "Price calculation")
    tester.print_exchange("What's 10% off a RM39 mug?", response2, "Price calculation")
    
    response3 = tester.chat("Tell me if it's dishwasher-safe", "Product feature follow-up")
    tester.print_exchange("Tell me if it's dishwasher-safe", response3, "Product feature follow-up")
    
    response4 = tester.chat("Add another one, how much for 2?", "Quantity calculation")
    tester.print_exchange("Add another one, how much for 2?", response4, "Quantity calculation")

def main():
    """Run all advanced pattern tests."""
    print("🚀 ZUS COFFEE ADVANCED PATTERN TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 80)
    
    tester = AdvancedPatternTester()
    
    try:
        # Run all test suites
        test_part1_slot_memory(tester)
        test_part2_agentic_planning(tester)
        test_part3_calculator(tester)
        test_part4a_rag_products(tester)
        test_part4b_text2sql_outlets(tester)
        test_additional_robustness(tester)
        test_mixed_flow(tester)
        
        print("\n🎉 ALL ADVANCED PATTERN TESTS COMPLETED!")
        print("=" * 80)
        print(f"Total exchanges: {len(tester.conversation_log)}")
        print(f"Session ID: {tester.session_id}")
        
        # Save detailed results
        with open(f"advanced_test_results_{int(time.time())}.json", "w") as f:
            json.dump(tester.conversation_log, f, indent=2)
        print("📁 Detailed results saved to advanced_test_results_*.json")
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")

if __name__ == "__main__":
    main()
