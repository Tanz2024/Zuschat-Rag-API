#!/usr/bin/env python3
"""
Comprehensive Production Test for Enhanced ZUS Coffee Chatbot
Tests all advanced features and intelligent capabilities
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://zuschat-rag-api.onrender.com"

def test_endpoint(endpoint, method="GET", data=None, description=""):
    """Test an API endpoint with error handling."""
    print(f"\n🧪 Testing: {description}")
    print(f"📡 {method} {BASE_URL}{endpoint}")
    
    try:
        if method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=30)
        else:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
        
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if endpoint == "/chat":
                print(f"🤖 Response: {result.get('message', '')[:200]}...")
            else:
                print(f"📊 Result: {json.dumps(result, indent=2)[:300]}...")
            return True, result
        else:
            print(f"❌ Error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False, None

def main():
    """Run comprehensive production tests."""
    print("🚀 ZUS Coffee Enhanced Chatbot Production Test")
    print("=" * 60)
    
    session_id = f"prod_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Test 1: Health Check
    test_endpoint("/health", description="Backend Health Check")
    
    # Test 2: Basic Chat
    success, _ = test_endpoint("/chat", "POST", {
        "message": "Hello! I'm testing the enhanced chatbot.",
        "session_id": session_id
    }, description="Basic Greeting Test")
    
    # Test 3: Product Search Intelligence
    test_endpoint("/chat", "POST", {
        "message": "What coffee drinks do you have that are sweet and creamy?",
        "session_id": session_id
    }, description="Intelligent Product Recommendation")
    
    # Test 4: Price Calculation with Tax
    test_endpoint("/chat", "POST", {
        "message": "Calculate the total price for 2 Americano and 1 Cappuccino with 6% SST tax",
        "session_id": session_id
    }, description="Advanced Price Calculation with Tax")
    
    # Test 5: Outlet Location Query
    test_endpoint("/chat", "POST", {
        "message": "Show me ZUS Coffee outlets in KLCC area that are open until 10pm",
        "session_id": session_id
    }, description="Context-Aware Outlet Search")
    
    # Test 6: Mathematical Calculation
    test_endpoint("/chat", "POST", {
        "message": "If I buy 3 items at RM 12.50 each and get 15% discount, what's my total?",
        "session_id": session_id
    }, description="Smart Mathematical Calculation")
    
    # Test 7: Product Comparison
    test_endpoint("/chat", "POST", {
        "message": "Compare Americano vs Cappuccino - which has more caffeine and what are the prices?",
        "session_id": session_id
    }, description="Intelligent Product Comparison")
    
    # Test 8: Context-Aware Follow-up
    test_endpoint("/chat", "POST", {
        "message": "Add 2 more of the cheaper option to my order",
        "session_id": session_id
    }, description="Context-Aware Conversation Continuation")
    
    # Test 9: Direct Product Search Endpoint
    test_endpoint("/products?query=iced coffee&top_k=5", description="Product Search API")
    
    # Test 10: Outlet Query Endpoint
    test_endpoint("/outlets?location=kuala lumpur&top_k=3", description="Outlet Search API")
    
    print("\n" + "=" * 60)
    print("🎯 Production test completed!")
    print("📋 Check the responses above to verify enhanced chatbot intelligence.")

if __name__ == "__main__":
    main()
