#!/usr/bin/env python3
"""
Debug the specific 500 error in chat endpoint
"""

import requests
import json

def test_debug_endpoint():
    """Test the debug endpoint to see system status"""
    url = "https://zuschat-rag-api.onrender.com/debug/system"
    
    print("🔍 Testing debug endpoint...")
    
    try:
        response = requests.get(url, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Debug info: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

def test_minimal_chat():
    """Test with minimal payload"""
    url = "https://zuschat-rag-api.onrender.com/chat"
    
    print("\n💬 Testing minimal chat payload...")
    
    # Try the absolute minimal required payload
    minimal_data = {
        "message": "hi"
    }
    
    try:
        response = requests.post(
            url,
            json=minimal_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_debug_endpoint()
    test_minimal_chat()
