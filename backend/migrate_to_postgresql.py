#!/usr/bin/env python3
"""
Migration script to transfer data from SQLite to PostgreSQL
"""
import sqlite3
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Load environment variables from .env file
load_dotenv()

from data.database import engine, create_tables, Outlet, SessionLocal

def migrate_sqlite_to_postgresql():
    """Migrate outlet data from SQLite to PostgreSQL"""
    
    # Create PostgreSQL tables
    print("Creating PostgreSQL tables...")
    create_tables()
    
    # Connect to SQLite
    sqlite_path = os.path.join(os.path.dirname(__file__), 'data', 'outlets.db')
    if not os.path.exists(sqlite_path):
        print(f"SQLite database not found at {sqlite_path}")
        return
    
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_cursor = sqlite_conn.cursor()
    
    # Get all outlets from SQLite
    sqlite_cursor.execute("SELECT id, name, address, opening_hours, services FROM outlets")
    outlets_data = sqlite_cursor.fetchall()
    
    print(f"Found {len(outlets_data)} outlets in SQLite database")
    
    # Insert into PostgreSQL
    db = SessionLocal()
    try:
        for outlet_data in outlets_data:
            outlet = Outlet(
                name=outlet_data[1],
                address=outlet_data[2],
                opening_hours=outlet_data[3],
                services=outlet_data[4]
            )
            db.add(outlet)
        
        db.commit()
        print(f"Successfully migrated {len(outlets_data)} outlets to PostgreSQL")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
    finally:
        db.close()
        sqlite_conn.close()

if __name__ == "__main__":
    migrate_sqlite_to_postgresql()
