#!/usr/bin/env python3
"""Test the specific calculator prompts that are failing"""

import requests
import json

def test_specific_calculator():
    url = "http://localhost:8000/chat"
    
    test_messages = [
        "Calculate 6% SST on RM55",
        "What's the total for 2 × RM39?", 
        "What's 20% discount on RM79?"
    ]
    
    for message in test_messages:
        print(f"\n{'='*60}")
        print(f"Testing: {message}")
        print(f"{'='*60}")
        
        try:
            payload = {"message": message}
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {data['message']}")
                print(f"Intent: {data.get('intent', 'N/A')}")
                print(f"Confidence: {data.get('confidence', 'N/A')}")
            else:
                print(f"Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_specific_calculator()
