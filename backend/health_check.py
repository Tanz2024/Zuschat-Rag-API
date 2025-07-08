#!/usr/bin/env python3
"""
Quick health check for the backend to identify 502 issues
"""
import sys
import os
sys.path.append('.')

def test_backend_health():
    """Test all backend components for health"""
    print("🔍 Backend Health Check")
    print("=" * 50)
    
    try:
        # Test 1: Models import
        print("1. Testing models import...")
        from models import ChatRequest, ChatResponse, ErrorResponse
        print("   ✅ Models imported successfully")
        
        # Test 2: Chatbot import
        print("2. Testing chatbot import...")
        from chatbot.enhanced_minimal_agent import get_chatbot
        chatbot = get_chatbot()
        print("   ✅ Chatbot imported and instantiated")
        
        # Test 3: FastAPI app creation
        print("3. Testing FastAPI app creation...")
        from main import app
        print("   ✅ FastAPI app created successfully")
        
        # Test 4: Basic chatbot functionality
        print("4. Testing basic chatbot functionality...")
        import asyncio
        
        async def test_chat():
            result = await chatbot.process_message("Hello", "test")
            return result
        
        result = asyncio.run(test_chat())
        if result and 'message' in result:
            print(f"   ✅ Chatbot responds: {result['message'][:50]}...")
        else:
            print("   ❌ Chatbot response issue")
            
        # Test 5: Intent validation
        print("5. Testing intent validation...")
        from models import Intent
        valid_intents = [e.value for e in Intent]
        print(f"   ✅ Valid intents: {valid_intents}")
        
        # Test 6: ChatResponse creation
        print("6. Testing ChatResponse creation...")
        response = ChatResponse(
            message="Test response",
            session_id="test",
            intent="greeting",
            confidence=0.9
        )
        print("   ✅ ChatResponse creation successful")
        
        print("\n🎉 ALL HEALTH CHECKS PASSED!")
        print("Backend should work correctly on Render.")
        return True
        
    except Exception as e:
        print(f"\n❌ HEALTH CHECK FAILED: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_backend_health()
    sys.exit(0 if success else 1)
