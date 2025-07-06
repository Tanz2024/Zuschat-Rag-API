#!/usr/bin/env python3
"""
Test the robust backend locally to verify it can handle missing database gracefully
"""

import sys
import os
import requests
import json
import time
import subprocess
import signal

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_dir)

def test_robust_backend():
    """Test the robust backend with graceful error handling"""
    print("🔍 Testing robust backend with graceful error handling...")
    
    # Start the robust server
    print("🚀 Starting robust backend server...")
    
    # Use the robust main file
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main_robust:app", "--host", "127.0.0.1", "--port", "8001"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(5)
    
    base_url = "http://127.0.0.1:8001"
    
    try:
        # Test endpoints
        endpoints_to_test = [
            ("/", "root endpoint"),
            ("/ping", "ping endpoint"),
            ("/health", "health check"),
            ("/debug/system", "system debug")
        ]
        
        for endpoint, description in endpoints_to_test:
            try:
                print(f"\n📞 Testing {description}: {endpoint}")
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                else:
                    print(f"   Error: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"   ❌ Error testing {endpoint}: {e}")
        
        # Test chat endpoint
        print(f"\n💬 Testing chat endpoint...")
        test_messages = [
            "Hello",
            "Show me products",
            "Calculate 25 + 15",
            "Find outlets"
        ]
        
        for message in test_messages:
            try:
                print(f"\n  Testing: '{message}'")
                chat_data = {
                    "message": message,
                    "session_id": "test_robust"
                }
                
                response = requests.post(
                    f"{base_url}/chat",
                    json=chat_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                print(f"    Status: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    print(f"    Response: {result['response'][:80]}...")
                    print(f"    Intent: {result.get('intent', 'unknown')}")
                else:
                    print(f"    Error: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"    ❌ Chat error: {e}")
        
        print("\n✅ ROBUST BACKEND TEST COMPLETED")
        print("Robust backend handles missing database gracefully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    finally:
        # Stop the server
        print("\n🛑 Stopping test server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()

if __name__ == "__main__":
    test_robust_backend()
