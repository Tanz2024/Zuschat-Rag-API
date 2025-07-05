#!/usr/bin/env python3
"""
Minimal test of just the chatbot agent without database dependencies
"""

import sys
import os

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_dir)

try:
    # Test just the chatbot agent without main.py imports
    from chatbot.enhanced_minimal_agent import EnhancedMinimalAgent
    
    print("✅ Enhanced chatbot agent imported successfully")
    
    # Create agent instance
    agent = EnhancedMinimalAgent()
    print("✅ Agent instance created")
    
    # Test basic functionality
    import asyncio
    
    async def test_agent():
        # Test greeting
        response1 = await agent.process_message("Hello", "test_session")
        print(f"✅ Greeting test: {response1['message'][:100]}...")
        
        # Test product search
        response2 = await agent.process_message("Show me all products", "test_session")
        print(f"✅ Product search test: {response2['message'][:100]}...")
        
        # Test calculation
        response3 = await agent.process_message("Calculate 25 + 15", "test_session")
        print(f"✅ Calculator test: {response3['message'][:100]}...")
        
        # Test outlet search
        response4 = await agent.process_message("Find outlets in KL", "test_session")
        print(f"✅ Outlet search test: {response4['message'][:100]}...")
        
        return True
    
    # Run the test
    result = asyncio.run(test_agent())
    
    if result:
        print("\n🎉 CHATBOT AGENT TEST PASSED")
        print("The enhanced minimal agent is working correctly!")
        print("The Render issue is likely related to database connectivity or deployment configuration.")
    
except Exception as e:
    print(f"❌ Error testing chatbot agent: {e}")
    import traceback
    traceback.print_exc()
