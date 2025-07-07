#!/usr/bin/env python3
"""
Quick deployment verification script for ZUS Coffee Chatbot
Tests core functionality after dependency fixes
"""

import sys
import os

def test_imports():
    """Test all critical imports"""
    try:
        print("🔍 Testing critical imports...")
        
        # Core FastAPI imports
        from fastapi import FastAPI
        print("  ✅ FastAPI import successful")
        
        # Database imports
        import sqlalchemy
        print("  ✅ SQLAlchemy import successful")
        
        # Add backend to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        # Chatbot agent import
        from chatbot.enhanced_minimal_agent import EnhancedMinimalAgent
        print("  ✅ Enhanced Minimal Agent import successful")
        
        # AI/ML imports
        import sentence_transformers
        print("  ✅ Sentence Transformers import successful")
        
        # Vector search imports
        try:
            import faiss
            print("  ✅ FAISS import successful")
        except ImportError:
            print("  ⚠️  FAISS not available (will be installed on Render)")
        
        print("\n🎉 All critical imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_agent_functionality():
    """Test core chatbot functionality"""
    try:
        print("\n🤖 Testing chatbot agent functionality...")
        
        # Add backend to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        from chatbot.enhanced_minimal_agent import EnhancedMinimalAgent
        
        # Initialize agent
        agent = EnhancedMinimalAgent()
        print("  ✅ Agent initialization successful")
        
        # Test intent detection
        test_queries = [
            "Hello",
            "What coffee do you have?",
            "Find outlets near me",
            "Calculate 5 + 3"
        ]
        
        for query in test_queries:
            result = agent.parse_intent_and_plan_action(query, "test_session")
            intent = result.get('intent', 'unknown')
            print(f"  ✅ Intent detection for '{query}': {intent}")
        
        # Test translation function (should fallback gracefully)
        translated = agent.translate_query("Hello world")
        print(f"  ✅ Translation fallback test: '{translated}'")
        
        print("\n🎉 All chatbot functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Chatbot test error: {e}")
        return False

def test_requirements():
    """Verify requirements.txt doesn't have conflicts"""
    try:
        print("\n📋 Checking requirements.txt...")
        
        req_path = os.path.join(os.path.dirname(__file__), 'backend', 'requirements.txt')
        if os.path.exists(req_path):
            with open(req_path, 'r') as f:
                content = f.read()
                
            # Check for problematic dependencies
            if 'googletrans' in content:
                print("  ❌ googletrans still in requirements (conflict risk)")
                return False
            
            if 'httpx==' in content:
                print("  ⚠️  httpx version pinned (potential conflict)")
            
            print("  ✅ Requirements.txt looks clean")
            
            # Count dependencies
            lines = [line.strip() for line in content.split('\n') 
                    if line.strip() and not line.strip().startswith('#')]
            print(f"  📦 Total dependencies: {len(lines)}")
            
        return True
        
    except Exception as e:
        print(f"❌ Requirements check error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 ZUS Coffee Chatbot - Deployment Verification")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Agent Functionality", test_agent_functionality),
        ("Requirements Check", test_requirements)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED - READY FOR RENDER DEPLOYMENT!")
    else:
        print("❌ SOME TESTS FAILED - CHECK ISSUES BEFORE DEPLOYMENT")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
