import requests
import json

def test_chatbot_version():
    """Test which version of chatbot is running."""
    
    # Test with a greeting that should trigger enhanced response
    test_message = "Hello, I'm looking for help with ZUS Coffee products and pricing!"
    
    try:
        response = requests.post(
            "https://zuschat-rag-api.onrender.com/chat",
            json={
                "message": test_message,
                "session_id": "version-test"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            message = data.get('message', '')
            
            print("🔍 CHATBOT VERSION TEST")
            print("=" * 50)
            print(f"Query: {test_message}")
            print(f"Response: {message}")
            print("=" * 50)
            
            # Check for enhanced features
            enhanced_indicators = [
                "Welcome to ZUS Coffee!",
                "AI assistant ready to help",
                "Product Information",
                "Outlet Locations", 
                "Calculations",
                "Recommendations",
                "Promotions"
            ]
            
            found_indicators = [indicator for indicator in enhanced_indicators if indicator in message]
            
            if len(found_indicators) >= 3:
                print("✅ ENHANCED CHATBOT DETECTED!")
                print(f"Found {len(found_indicators)}/{len(enhanced_indicators)} enhanced features")
                print("Enhanced features found:", found_indicators)
            else:
                print("⚠️  BASIC CHATBOT DETECTED")
                print(f"Found {len(found_indicators)}/{len(enhanced_indicators)} enhanced features")
                print("This suggests the deployment is still using the old version")
            
            return len(found_indicators) >= 3
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False

if __name__ == "__main__":
    test_chatbot_version()
