#!/usr/bin/env python3
"""Test the fixed enhanced minimal agent"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot.enhanced_minimal_agent import get_chatbot

async def test_queries():
    agent = get_chatbot()
    
    test_cases = [
        'What drinkware collections do you have?',
        'Show me coffee tumblers under RM40',
        'Show me eco-friendly drinkware options', 
        'What steel tumblers are available?',
        'What products do you have?',
        'Show me all outlet locations',
        'Which outlets are open 24 hours?',
        'ZUS Coffee outlets in KL with drive-thru'
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f'\nTest {i}: {query}')
        result = await agent.process_message(query, f'test{i}')
        response = result['message']
        print(f'Response: {response[:150]}...')
        print(f'Intent: {result.get("intent", "unknown")}')

if __name__ == "__main__":
    asyncio.run(test_queries())
