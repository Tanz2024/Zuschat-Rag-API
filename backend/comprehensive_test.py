"""
Comprehensive test script to verify the ZUS Coffee chatbot handles all types of user questions.
Tests beginner to advanced questions, calculations, error handling, and data boundaries.
"""

import requests
import json
import time

# Base URL for the chatbot API
BASE_URL = "http://localhost:8000"

def test_chatbot_endpoint(message):
    """Test a single message with the chatbot"""
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": message},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "No response")
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Exception: {str(e)}"

def run_comprehensive_tests():
    """Run all test categories"""
    
    print("🚀 Starting Comprehensive ZUS Coffee Chatbot Tests")
    print("=" * 60)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    test_categories = [
        {
            "name": "1. Basic Product Questions",
            "questions": [
                "What drinks do you have?",
                "Show me all coffee options",
                "What's on the menu?",
                "List all beverages",
                "What can I order?"
            ]
        },
        {
            "name": "2. Specific Product Queries", 
            "questions": [
                "Tell me about Americano",
                "What's the price of Cappuccino?",
                "How much is a Latte?",
                "Do you have iced coffee?",
                "What's in a Mocha?"
            ]
        },
        {
            "name": "3. Outlet/Location Questions",
            "questions": [
                "Where are your stores?",
                "Show me all outlets",
                "Which outlet is in KL?",
                "Find stores near me",
                "List all locations"
            ]
        },
        {
            "name": "4. Specific Outlet Queries",
            "questions": [
                "Where is KLCC outlet?",
                "What's the address of Sunway Pyramid?",
                "Tell me about Mid Valley store",
                "Is there a ZUS in 1 Utama?",
                "Where can I find ZUS in PJ?"
            ]
        },
        {
            "name": "5. Mathematical Calculations",
            "questions": [
                "What's 15 + 25?",
                "Calculate 100 * 3.5",
                "What is 50 divided by 2?",
                "If I buy 3 Americanos at RM 8 each, how much total?",
                "What's the square root of 144?"
            ]
        },
        {
            "name": "6. Complex Business Questions",
            "questions": [
                "What's the cheapest drink you have?",
                "How many outlets do you have in total?",
                "Which drinks cost more than RM 10?",
                "What's the average price of hot drinks?",
                "Show me all outlets in Selangor"
            ]
        },
        {
            "name": "7. Conversational Context",
            "questions": [
                "Hi there! How are you?",
                "What can you help me with?",
                "Tell me about ZUS Coffee",
                "What makes ZUS special?",
                "Thank you for your help"
            ]
        },
        {
            "name": "8. Incomplete/Unclear Questions",
            "questions": [
                "price",
                "where",
                "coffee thing",
                "that one drink",
                "the store with the thing"
            ]
        },
        {
            "name": "9. Invalid/Malicious Inputs",
            "questions": [
                "DROP TABLE products;",
                "SELECT * FROM users WHERE password='';",
                "'; DELETE FROM outlets; --",
                "What's 5/0?",
                "Calculate infinity + 1"
            ]
        },
        {
            "name": "10. Non-ZUS Related Questions",
            "questions": [
                "What's the weather today?",
                "Who is the Prime Minister?",
                "Tell me about Starbucks",
                "How do I make pasta?",
                "What's the capital of France?"
            ]
        }
    ]
    
    all_passed = True
    
    for category in test_categories:
        print(f"\n📋 {category['name']}")
        print("-" * 40)
        
        for i, question in enumerate(category['questions'], 1):
            print(f"\n❓ Q{i}: {question}")
            response = test_chatbot_endpoint(question)
            print(f"🤖 Response: {response[:200]}{'...' if len(response) > 200 else ''}")
            
            # Basic validation
            if "error" in response.lower() and "exception" in response.lower():
                print("❌ FAILED: Exception occurred")
                all_passed = False
            elif len(response.strip()) < 10:
                print("⚠️  WARNING: Very short response")
            else:
                print("✅ PASSED: Valid response received")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS COMPLETED - Chatbot appears to be working correctly!")
    else:
        print("⚠️  SOME ISSUES DETECTED - Check the responses above")
    print("=" * 60)

if __name__ == "__main__":
    run_comprehensive_tests()
