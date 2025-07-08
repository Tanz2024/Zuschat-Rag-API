#!/usr/bin/env python3
"""
Test the deployed backend /test-chat endpoint with proper POST request
"""
import requests
import json

def test_test_chat_endpoint():
    """Test the /test-chat endpoint with POST request."""
    url = "https://zuschat-rag-api.onrender.com/test-chat"
    
    # Test data
    test_data = {
        "message": "Hello, this is a test message",
        "session_id": "test_session_123"
    }
    
    print(f"Testing POST request to: {url}")
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            url, 
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS - /test-chat endpoint is working!")
            response_data = response.json()
            print(f"Response Data: {json.dumps(response_data, indent=2)}")
        else:
            print(f"❌ FAILED - Status {response.status_code}")
            print(f"Response Text: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - Request took too long")
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")

def test_chat_endpoint():
    """Test the main /chat endpoint."""
    url = "https://zuschat-rag-api.onrender.com/chat"
    
    # Test data
    test_data = {
        "message": "What's the cheapest ceramic mug you have?",
        "session_id": "test_session_456"
    }
    
    print(f"\n\nTesting POST request to: {url}")
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            url, 
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS - /chat endpoint is working!")
            response_data = response.json()
            print(f"Response Data: {json.dumps(response_data, indent=2)}")
        else:
            print(f"❌ FAILED - Status {response.status_code}")
            print(f"Response Text: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - Request took too long")
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")

if __name__ == "__main__":
    print("=== ZUS Coffee Backend Endpoint Testing ===")
    test_test_chat_endpoint()
    test_chat_endpoint()
    print("\n=== Testing Complete ===")
