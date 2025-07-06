#!/usr/bin/env python3
"""
Test local backend startup with SQLite fallback
"""

import os
import sys
import tempfile

# Set a temporary DATABASE_URL for testing
temp_db = os.path.join(tempfile.gettempdir(), "test_zus.db")
os.environ["DATABASE_URL"] = f"sqlite:///{temp_db}"

print(f"Using temporary SQLite database: {temp_db}")

try:
    # Add backend directory to path
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    sys.path.insert(0, backend_dir)
    
    # Now try to import the main app
    from main import app
    print("✅ FastAPI app imported successfully")
    
    # Test the enhanced chatbot import
    from chatbot.enhanced_minimal_agent import get_chatbot
    chatbot = get_chatbot()
    print("✅ Enhanced chatbot imported successfully")
    
    # Test a simple chat
    response = chatbot.chat("Hello", "test_session")
    print(f"✅ Chat test: {response}")
    
    print("\n🎉 LOCAL BACKEND TEST PASSED")
    print("The issue is likely with the Render DATABASE_URL configuration")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
