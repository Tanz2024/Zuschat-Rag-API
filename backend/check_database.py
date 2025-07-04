#!/usr/bin/env python3
"""
Database Health Check Script
Tests database connection and displays configuration info
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
sys.path.append(os.path.dirname(__file__))

try:
    from data.database import validate_database_config, get_db_info
    
    print("🔍 ZUS Coffee AI Chatbot - Database Health Check")
    print("=" * 50)
    
    # Display connection info (without credentials)
    db_info = get_db_info()
    if "error" not in db_info:
        print(f"📍 Host: {db_info['host']}")
        print(f"🔌 Port: {db_info['port']}")
        print(f"🗄️  Database: {db_info['database']}")
        print(f"🏊 Pool Size: {db_info['pool_size']}")
        print(f"⬆️  Max Overflow: {db_info['max_overflow']}")
    else:
        print(f"❌ {db_info['error']}")
    
    print("\n🧪 Testing database connection...")
    
    # Validate connection
    if validate_database_config():
        print("\n🎉 Database is ready for use!")
        sys.exit(0)
    else:
        print("\n💥 Database connection failed!")
        print("\n🔧 Troubleshooting:")
        print("1. Check if PostgreSQL is running")
        print("2. Verify DATABASE_URL in .env file")
        print("3. Ensure database exists")
        print("4. Check network connectivity")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the backend directory")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
