#!/usr/bin/env python3
"""
Test the local standalone server to verify chatbot functionality
"""

import requests
import json
import time

def test_local_server():
    """Test the local standalone server"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing local standalone server...")
    print(f"Target: {base_url}")
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    try:
        # Test root endpoint
        print("\n📞 Testing root endpoint...")
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Root response: {json.dumps(response.json(), indent=2)}")
        
        # Test health endpoint
        print("\n🏥 Testing health endpoint...")
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Health response: {json.dumps(response.json(), indent=2)}")
        
        # Test chat endpoint
        print("\n💬 Testing chat endpoint...")
        
        test_messages = [
            "Hello",
            "Show me all products", 
            "Calculate 25 + 15",
            "Find outlets in KL"
        ]
        
        for message in test_messages:
            print(f"\n  Testing: '{message}'")
            chat_data = {
                "message": message,
                "session_id": "test_session"
            }
            
            response = requests.post(
                f"{base_url}/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"  Response: {result['response'][:100]}...")
                print(f"  Intent: {result.get('intent', 'unknown')}")
            else:
                print(f"  Error: {response.text}")
        
        print("\n✅ LOCAL STANDALONE SERVER TEST COMPLETED")
        print("If this works, the issue is definitely with Render deployment configuration")
        
    except Exception as e:
        print(f"❌ Error testing local server: {e}")

if __name__ == "__main__":
    test_local_server()
