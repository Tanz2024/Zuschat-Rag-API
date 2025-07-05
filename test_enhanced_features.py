#!/usr/bin/env python3
"""
Test the enhanced filtering capabilities of the ZUS Coffee chatbot
"""

import sys
import os
import asyncio

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_dir)

from chatbot.enhanced_minimal_agent import EnhancedMinimalAgent

async def test_enhanced_features():
    """Test all new enhanced features"""
    agent = EnhancedMinimalAgent()
    
    print("🚀 TESTING ENHANCED ZUS COFFEE CHATBOT FEATURES")
    print("=" * 60)
    
    test_queries = [
        # Price range filtering
        "Show me products under RM 50",
        "Products between RM 50 and RM 60",
        "Show expensive items above RM 100",
        
        # Category filtering
        "Show me all tumblers",
        "I want ceramic mugs",
        "Any cups available?",
        
        # Material filtering
        "Show stainless steel products",
        "Ceramic items please",
        
        # Collection filtering
        "Show Sundaze collection",
        "Products from Aqua collection",
        
        # Tax calculation
        "Show me products with tax calculation",
        "What's the total cost with SST for the ceramic mug?",
        
        # City-based outlet filtering
        "Outlets in Kuala Lumpur",
        "Show me outlets in Selangor",
        "Any outlets in Petaling Jaya?",
        
        # Service-based outlet filtering
        "Outlets with delivery service",
        "Which outlets have WiFi?",
        
        # Show all
        "Show me all products",
        "Show all outlets",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 40)
        
        try:
            response = await agent.process_message(query, "test_session")
            print(f"✅ Response: {response['message'][:200]}...")
            print(f"   Intent: {response.get('intent', 'unknown')}")
            print(f"   Confidence: {response.get('confidence', 0):.2f}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        await asyncio.sleep(0.5)  # Small delay
    
    print(f"\n🎉 Enhanced feature testing completed!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_features())
