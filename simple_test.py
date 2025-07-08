#!/usr/bin/env python3
"""
Simple test for the /test-chat endpoint using requests
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import requests
    print("✅ Requests library available")
except ImportError:
    print("❌ Requests library not available - installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

def test_endpoints():
    """Test all available endpoints."""
    base_url = "https://zuschat-rag-api.onrender.com"
    
    # Test 1: Health endpoint
    print("1. Testing /health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Health endpoint working")
        else:
            print(f"   ❌ Health endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Health endpoint error: {e}")
    
    # Test 2: Ping endpoint
    print("\n2. Testing /ping endpoint...")
    try:
        response = requests.get(f"{base_url}/ping", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Ping endpoint working")
        else:
            print(f"   ❌ Ping endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Ping endpoint error: {e}")
    
    # Test 3: New GET test endpoint
    print("\n3. Testing /test-chat-get endpoint...")
    try:
        response = requests.get(f"{base_url}/test-chat-get", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ GET test endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"   ❌ GET test endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ GET test endpoint error: {e}")
    
    # Test 4: POST test endpoint
    print("\n4. Testing /test-chat endpoint (POST)...")
    try:
        data = {"message": "Hello test", "session_id": "test_session"}
        response = requests.post(f"{base_url}/test-chat", json=data, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ POST test endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"   ❌ POST test endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ POST test endpoint error: {e}")
    
    # Test 5: Main chat endpoint
    print("\n5. Testing /chat endpoint...")
    try:
        data = {"message": "What ceramic mugs do you have?", "session_id": "test_chat"}
        response = requests.post(f"{base_url}/chat", json=data, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Main chat endpoint working")
            resp_data = response.json()
            print(f"   Message: {resp_data.get('message', 'N/A')[:100]}...")
        else:
            print(f"   ❌ Main chat endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Main chat endpoint error: {e}")

if __name__ == "__main__":
    print("=== ZUS Coffee Backend Endpoint Testing ===")
    test_endpoints()
    print("\n=== Testing Complete ===")
