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
        health_data = response.json()
        print(f"   📄 Response: {health_data}")
        
        # Check version in response (if available)
        if "version" in str(health_data):
            print(f"   🔢 Backend Version: Check if updated")
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
    
    # Test 3: Root endpoint (check version)
    print("3. Testing / endpoint (version check)...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   ✅ Status: {response.status_code}")
        root_data = response.json()
        version = root_data.get("version", "unknown")
        print(f"   🔢 Version: {version}")
        print(f"   📄 System: {root_data.get('system', {})}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 4: Test chat endpoint (should work after redeploy)
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
            print("   🎉 Test endpoint is working!")
        else:
            print(f"   ❌ Error Response: {response.text}")
            if response.status_code == 404:
                print("   ⏳ Still deploying... try again in 1-2 minutes")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 5: Chat endpoint (the main one)
    print("5. Testing /chat endpoint...")
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
    
    print("\n🎯 Summary:")
    print("   • If /test-chat shows 404, wait 1-2 minutes for deployment")
    print("   • If /chat works, your main chatbot is functional")
    print("   • Version should be 1.0.2 or higher after deployment")

if __name__ == "__main__":
    test_backend()
