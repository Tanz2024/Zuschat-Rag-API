#!/usr/bin/env python3
"""
Production verification test for ZUS Coffee chatbot
"""

import requests
import json
import time

BASE_URL = "https://zuschat-rag-api.onrender.com"

def test_chatbot():
    """Test key chatbot functionalities"""
    
    test_cases = [
        {
            "query": "What drinkware collections do you have?",
            "expected_keywords": ["Sundaze", "Aqua", "Corak Malaysia"],
            "description": "Collections query"
        },
        {
            "query": "Show me coffee tumblers under RM40", 
            "expected_keywords": ["RM 39.00", "Ceramic Mug"],
            "description": "Price filtering"
        },
        {
            "query": "Show me all outlet locations",
            "expected_keywords": ["KLCC", "Pavilion", "outlets"],
            "description": "Outlet search"
        },
        {
            "query": "What steel tumblers are available?",
            "expected_keywords": ["All-Can Tumbler", "Stainless Steel"],
            "description": "Material search"
        },
        {
            "query": "ZUS Coffee outlets in KL with drive-thru",
            "expected_keywords": ["Shah Alam", "Drive-Thru"],
            "description": "Service search"
        }
    ]
    
    print("🧪 Testing ZUS Coffee Chatbot Production Deployment")
    print("=" * 60)
    
    success_count = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test['description']}")
        print(f"Query: {test['query']}")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json={"message": test['query'], "session_id": f"test_{i}"},
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', '')
                
                # Check for expected keywords
                found_keywords = [kw for kw in test['expected_keywords'] if kw.lower() in message.lower()]
                
                print(f"✅ Response time: {response_time:.2f}s")
                print(f"✅ Keywords found: {found_keywords}")
                print(f"📝 Response: {message[:100]}...")
                
                if found_keywords:
                    success_count += 1
                    print("✅ TEST PASSED")
                else:
                    print("❌ TEST FAILED - Keywords not found")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print("-" * 40)
    
    print(f"\n🎯 RESULTS: {success_count}/{len(test_cases)} tests passed")
    
    if success_count == len(test_cases):
        print("🎉 ALL TESTS PASSED - Chatbot is production ready!")
    else:
        print("⚠️ Some tests failed - Review required")

if __name__ == "__main__":
    test_chatbot()
