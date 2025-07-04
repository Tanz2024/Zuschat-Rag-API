"""
Database configuration and setup for ZUS Coffee chatbot
PostgreSQL with SQLAlcdef validate_database_config():
    """Validate database configuration and connection"""
    try:
        # Test database connection
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please check your DATABASE_URL and ensure PostgreSQL is running")
        return False"
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Please set it to your PostgreSQL connection string. "
        "Example: postgresql://username:password@host:port/database"
    )

# Additional database configuration
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"

# SQLAlchemy setup with configurable pool settings
engine = create_engine(
    DATABASE_URL,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
    echo=DB_ECHO,  # Set to True for SQL query logging
    pool_pre_ping=True  # Validates connections before use
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Outlet model
class Outlet(Base):
    __tablename__ = "outlets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    address = Column(Text, nullable=False)
    opening_hours = Column(Text)
    services = Column(Text)

# Chat session model
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)

# Chat message model
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)

def get_connection():
    """Get database connection for direct queries"""
    return engine.connect()

def validate_database_config():
    """Validate database configuration and connection"""
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please check your DATABASE_URL and ensure PostgreSQL is running")
        return False

def get_db_info():
    """Get database connection information (without exposing credentials)"""
    try:
        url_parts = DATABASE_URL.split("://")[1].split("/")
        host_port = url_parts[0].split("@")[1] if "@" in url_parts[0] else url_parts[0]
        database = url_parts[1] if len(url_parts) > 1 else "unknown"
        
        return {
            "host": host_port.split(":")[0],
            "port": host_port.split(":")[1] if ":" in host_port else "5432",
            "database": database,
            "pool_size": DB_POOL_SIZE,
            "max_overflow": DB_MAX_OVERFLOW
        }
    except Exception:
        return {"error": "Unable to parse DATABASE_URL"}
