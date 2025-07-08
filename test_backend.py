#!/usr/bin/env python3
"""
Quick test script to debug the 502 error on /chat endpoint
"""
import requests
import json

def test_backend():
    base_url = "https://zuschat-rag-api.onrender.com"
    
    print("🧪 Testing ZUS Coffee Backend Endpoints\n")
    
    # Test 1: Health check
    print("1. Testing /health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📄 Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 2: Ping endpoint
    print("2. Testing /ping endpoint...")
    try:
        response = requests.get(f"{base_url}/ping", timeout=10)
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📄 Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 3: Chat endpoint (the problematic one)
    print("3. Testing /chat endpoint...")
    try:
        chat_data = {
            "message": "hello",
            "session_id": "test-session"
        }
        response = requests.post(
            f"{base_url}/chat", 
            json=chat_data, 
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        print(f"   ✅ Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   📄 Response: {response.json()}")
        else:
            print(f"   ❌ Error Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 4: Test chat endpoint (if it exists)
    print("4. Testing /test-chat endpoint...")
    try:
        chat_data = {
            "message": "test message",
            "session_id": "test-session"
        }
        response = requests.post(
            f"{base_url}/test-chat", 
            json=chat_data, 
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        print(f"   ✅ Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   📄 Response: {response.json()}")
        else:
            print(f"   ❌ Error Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_backend()
