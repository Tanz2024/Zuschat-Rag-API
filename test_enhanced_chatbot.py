#!/usr/bin/env python3
"""
ZUS Coffee Enhanced Chatbot Test Suite
Test all advanced features of the intelligent chatbot
"""

import requests
import json
import time
from typing import Dict, Any

class ZUSChatbotTester:
    def __init__(self, base_url: str = "https://zuschat-rag-api.onrender.com"):
        self.base_url = base_url
        self.session_id = f"test_session_{int(time.time())}"
    
    def send_message(self, message: str) -> Dict[str, Any]:
        """Send message to chatbot and return response."""
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json={
                    "message": message,
                    "session_id": self.session_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "response": response.text
                }
        except Exception as e:
            return {"error": str(e)}
    
    def test_enhanced_features(self):
        """Test all enhanced chatbot features."""
        
        test_cases = [
            # 1. Enhanced Greeting
            {
                "name": "Enhanced Greeting",
                "message": "Hello!",
                "expected_features": ["Welcome to ZUS Coffee", "AI assistant", "Product Information", "Outlet Locations", "Calculations"]
            },
            
            # 2. Smart Product Inquiry
            {
                "name": "Smart Product Search",
                "message": "Show me stainless steel tumblers under RM80",
                "expected_features": ["stainless steel", "tumbler", "price", "RM"]
            },
            
            # 3. Advanced Calculation
            {
                "name": "Cart Calculation with Tax",
                "message": "Calculate total price for 2 ZUS OG Cups and 1 All-Can Tumbler including 6% tax",
                "expected_features": ["calculate", "total", "tax", "6%", "RM"]
            },
            
            # 4. Location Intelligence
            {
                "name": "Smart Outlet Search",
                "message": "Find ZUS Coffee outlets in Damansara with operating hours",
                "expected_features": ["Damansara", "outlet", "hours", "operating"]
            },
            
            # 5. Product Comparison
            {
                "name": "Product Comparison",
                "message": "Compare ceramic mugs vs stainless steel tumblers",
                "expected_features": ["compare", "ceramic", "stainless steel", "vs", "difference"]
            },
            
            # 6. Budget-Based Recommendation
            {
                "name": "Budget Recommendation",
                "message": "Recommend drinkware for office use under RM60",
                "expected_features": ["recommend", "office", "RM60", "under"]
            },
            
            # 7. Promotion Inquiry
            {
                "name": "Promotion Intelligence",
                "message": "What promotions and discounts are available?",
                "expected_features": ["promotion", "discount", "sale", "deal"]
            },
            
            # 8. Mathematical Calculation
            {
                "name": "Math Calculation",
                "message": "Calculate 15% of RM120",
                "expected_features": ["15%", "RM120", "calculation", "18"]
            },
            
            # 9. Context Awareness Test
            {
                "name": "Context Follow-up",
                "message": "What are the operating hours?",
                "expected_features": ["hours", "operating", "open", "close"]
            },
            
            # 10. Complex Query
            {
                "name": "Complex Multi-Intent Query",
                "message": "I need 3 large capacity travel tumblers for my team, calculate total cost with tax, and find nearest outlet to KLCC",
                "expected_features": ["3", "large", "travel", "tumbler", "team", "calculate", "tax", "nearest", "KLCC"]
            }
        ]
        
        print("🧪 ZUS Coffee Enhanced Chatbot Test Suite")
        print("=" * 60)
        
        results = []
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n{i}. Testing: {test['name']}")
            print(f"Query: '{test['message']}'")
            
            response = self.send_message(test['message'])
            
            if "error" in response:
                print(f"❌ ERROR: {response['error']}")
                results.append({"test": test['name'], "status": "ERROR", "error": response['error']})
                continue
            
            # Check response
            message = response.get('message', '').lower()
            intent = response.get('intent', '')
            confidence = response.get('confidence', 0)
            
            print(f"Intent: {intent} (confidence: {confidence:.2f})")
            print(f"Response: {response.get('message', '')[:200]}...")
            
            # Check if expected features are present
            features_found = []
            features_missing = []
            
            for feature in test['expected_features']:
                if feature.lower() in message:
                    features_found.append(feature)
                else:
                    features_missing.append(feature)
            
            if len(features_found) >= len(test['expected_features']) * 0.6:  # 60% threshold
                print(f"✅ PASS - Found {len(features_found)}/{len(test['expected_features'])} expected features")
                results.append({"test": test['name'], "status": "PASS", "features_found": features_found})
            else:
                print(f"⚠️  PARTIAL - Found {len(features_found)}/{len(test['expected_features'])} expected features")
                print(f"Missing: {features_missing}")
                results.append({"test": test['name'], "status": "PARTIAL", "features_found": features_found, "missing": features_missing})
            
            time.sleep(1)  # Rate limiting
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = len([r for r in results if r['status'] == 'PASS'])
        partial = len([r for r in results if r['status'] == 'PARTIAL'])
        failed = len([r for r in results if r['status'] == 'ERROR'])
        
        print(f"✅ PASSED: {passed}/{len(results)}")
        print(f"⚠️  PARTIAL: {partial}/{len(results)}")
        print(f"❌ FAILED: {failed}/{len(results)}")
        
        if passed >= len(results) * 0.8:
            print("\n🎉 EXCELLENT! Enhanced chatbot is working well!")
        elif passed >= len(results) * 0.6:
            print("\n👍 GOOD! Most enhanced features are working.")
        else:
            print("\n⚠️  NEEDS IMPROVEMENT: Some features may need attention.")
        
        return results
    
    def test_health_check(self):
        """Test if the backend is accessible."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                print("✅ Backend is healthy and accessible")
                return True
            else:
                print(f"⚠️  Backend returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend not accessible: {str(e)}")
            return False

def main():
    """Run the complete test suite."""
    print("🚀 Starting ZUS Coffee Enhanced Chatbot Test")
    
    tester = ZUSChatbotTester()
    
    # Health check first
    if not tester.test_health_check():
        print("❌ Cannot proceed - backend not accessible")
        return
    
    print("⏳ Waiting 5 seconds for any deployment to settle...")
    time.sleep(5)
    
    # Run enhanced feature tests
    results = tester.test_enhanced_features()
    
    print(f"\n🔗 Session ID used: {tester.session_id}")
    print("✅ Test completed!")

if __name__ == "__main__":
    main()
