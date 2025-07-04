#!/usr/bin/env python3
"""
Test script for ZUS Coffee Chatbot API
Tests all endpoints with real data
"""

import requests
import json
import time

API_BASE_URL = "https://zuschat-rag-api.onrender.com"

def test_endpoint(method, endpoint, data=None, params=None):
    """Test an API endpoint and return results."""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, params=params, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=30)
        
        print(f"\n{'='*60}")
        print(f"🧪 Testing: {method.upper()} {endpoint}")
        print(f"📍 URL: {url}")
        if params:
            print(f"📋 Params: {params}")
        if data:
            print(f"📦 Data: {json.dumps(data, indent=2)}")
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS")
            print(f"📄 Response: {json.dumps(result, indent=2)[:500]}...")
            return True, result
        else:
            print(f"❌ FAILED")
            print(f"📄 Error: {response.text}")
            return False, response.text
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False, str(e)

def main():
    """Run comprehensive API tests."""
    
    print("🚀 Starting ZUS Coffee Chatbot API Tests")
    print(f"🌐 Base URL: {API_BASE_URL}")
    
    results = []
    
    # Test 1: Root endpoint
    success, data = test_endpoint("GET", "/")
    results.append(("Root", success))
    
    # Test 2: Health check
    success, data = test_endpoint("GET", "/health")
    results.append(("Health", success))
    
    # Test 3: Product search
    success, data = test_endpoint("GET", "/products", params={"query": "tumbler", "top_k": 3})
    results.append(("Product Search", success))
    
    # Test 4: Outlet search
    success, data = test_endpoint("GET", "/outlets", params={"location": "Kuala Lumpur"})
    results.append(("Outlet Search", success))
    
    # Test 5: Calculator
    calc_data = {
        "expression": "2 * 50 * 0.9"  # 2 items * RM50 each * 10% discount
    }
    success, data = test_endpoint("POST", "/calculator", data=calc_data)
    results.append(("Calculator", success))
    
    # Test 6: Chat endpoint
    chat_data = {
        "message": "What tumblers do you have?",
        "conversation_id": "test-conversation-001",
        "user_id": "test-user"
    }
    success, data = test_endpoint("POST", "/chat", data=chat_data)
    results.append(("Chat", success))
    
    # Test 7: Chat with product query
    chat_data = {
        "message": "Show me outlets in KL",
        "conversation_id": "test-conversation-001",
        "user_id": "test-user"
    }
    success, data = test_endpoint("POST", "/chat", data=chat_data)
    results.append(("Chat - Outlets", success))
    
    # Test 8: Chat with calculation
    chat_data = {
        "message": "Calculate price for 2 tumblers with 15% discount",
        "conversation_id": "test-conversation-001", 
        "user_id": "test-user"
    }
    success, data = test_endpoint("POST", "/chat", data=chat_data)
    results.append(("Chat - Calculate", success))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your API is working perfectly!")
    else:
        print(f"⚠️  {total - passed} tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    main()
