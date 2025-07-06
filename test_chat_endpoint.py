#!/usr/bin/env python3
"""
Quick test of the Render chat endpoint to debug the formatting issue
"""

import requests
import json

def test_chat_endpoint():
    """Test chat endpoint specifically"""
    url = "https://zuschat-rag-api.onrender.com/chat"
    
    print("💬 Testing Render chat endpoint...")
    print(f"Target: {url}")
    
    # Test with a simple message
    test_data = {
        "message": "Hello",
        "session_id": "test_session"
    }
    
    try:
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ Chat Response JSON: {json.dumps(result, indent=2)}")
                
                # Check if response field exists and is not None
                if 'response' in result:
                    if result['response'] is not None:
                        print(f"✅ Response message: {result['response'][:100]}...")
                    else:
                        print("❌ Response message is None")
                else:
                    print("❌ No 'response' field in result")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Raw response: {response.text[:200]}")
        else:
            print(f"❌ HTTP Error {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Request error: {e}")

if __name__ == "__main__":
    test_chat_endpoint()
