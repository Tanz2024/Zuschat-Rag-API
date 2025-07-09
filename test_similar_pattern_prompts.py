#!/usr/bin/env python3
"""Test similar pattern prompts to the frontend suggestive prompts for robustness."""

import requests
import json

def test_similar_pattern_prompts():
    url = "http://localhost:8000/chat"
    
    test_messages = [
        # Products Category (paraphrased)
        "Show me the ZUS OG Cup 2.0 that comes with a screw-on lid.",
        "Which ceramic mug is the most affordable?",
        "List all products priced below RM60.",
        "Give me details about the ZUS All-Can Tumbler 600ml.",
        # Outlets Category (paraphrased)
        "List ZUS Coffee outlets located in Kuala Lumpur.",
        "Which outlets in Selangor offer WiFi?",
        "Are there any outlets close to Cheras?",
        "Which ZUS Coffee locations have drive-thru options?",
        # Calculator Category (paraphrased)
        "How much is 6% SST for RM55?",
        "Calculate the total price for two items at RM39 each.",
        "Add up RM105, RM55, and RM39.",
        "How much do I pay after a 20% discount on RM79?"
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
    test_similar_pattern_prompts()
