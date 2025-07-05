#!/usr/bin/env python3
"""
Simple Render deployment test - just check if backend is reachable
"""

import requests
import time
import json

def test_render_backend():
    """Test if Render backend is accessible"""
    url = "https://zuschat-rag-api.onrender.com"
    
    print("🔍 Testing Render backend accessibility...")
    print(f"Target: {url}")
    
    # Try multiple times as Render free tier can be slow to wake up
    for attempt in range(5):
        try:
            print(f"\n📞 Attempt {attempt + 1}/5...")
            
            # Try to access root endpoint with longer timeout
            response = requests.get(
                f"{url}/", 
                timeout=30,
                headers={'User-Agent': 'ZUS-Test-Client/1.0'}
            )
            
            print(f"✅ Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Backend is accessible!")
                print(f"Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"⚠️  Got status {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print("⏰ Request timed out")
        except requests.exceptions.ConnectionError:
            print("🔌 Connection error")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        if attempt < 4:
            print("⏳ Waiting 10 seconds before retry...")
            time.sleep(10)
    
    print("❌ Backend is not accessible after multiple attempts")
    return False

def test_health_endpoint():
    """Test health endpoint specifically"""
    url = "https://zuschat-rag-api.onrender.com/health"
    
    print(f"\n🏥 Testing health endpoint: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Health response: {response.json()}")
            return True
    except Exception as e:
        print(f"Health check failed: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 SIMPLE RENDER DEPLOYMENT TEST")
    print("=" * 50)
    
    # Test basic connectivity
    if test_render_backend():
        # If basic test passes, try health endpoint
        test_health_endpoint()
    else:
        print("\n💡 Troubleshooting tips:")
        print("1. Check if the Render service is running in the dashboard")
        print("2. Look at the Render logs for deployment errors")
        print("3. Verify the render.yaml configuration")
        print("4. Free tier services may take time to wake up")
