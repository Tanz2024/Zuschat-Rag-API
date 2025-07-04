#!/usr/bin/env python3
"""
Reset PostgreSQL database with updated schema
"""
from dotenv import load_dotenv
load_dotenv()

from data.database import engine, Base, SessionLocal
from sqlalchemy import text

def reset_database():
    """Drop and recreate all tables with updated schema"""
    print("🔄 Resetting PostgreSQL database...")
    
    # Drop all tables
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS products CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS outlets CASCADE")) 
        conn.execute(text("DROP TABLE IF EXISTS chat_messages CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS chat_sessions CASCADE"))
        conn.commit()
    
    print("✅ Dropped existing tables")
    
    # Create all tables with new schema
    Base.metadata.create_all(bind=engine)
    print("✅ Created tables with updated schema")
    
    # Verify tables exist
    with SessionLocal() as db:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            
        print(f"\n📋 Created tables: {', '.join(tables)}")

if __name__ == "__main__":
    reset_database()
