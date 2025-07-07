"""
Database configuration and setup for ZUS Coffee chatbot
PostgreSQL with SQLAlchemy ORM
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database configuration

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL environment variable is not set. Database features will be disabled.")
    DATABASE_URL = None

# Clean up DATABASE_URL in case it has the variable name as prefix
if DATABASE_URL and DATABASE_URL.startswith("DATABASE_URL="):
    DATABASE_URL = DATABASE_URL.replace("DATABASE_URL=", "")
    print("WARNING: DATABASE_URL had incorrect prefix, cleaned it up")

# Validate DATABASE_URL format
if DATABASE_URL and not DATABASE_URL.startswith(("postgresql://", "postgres://")):
    print(f"Invalid DATABASE_URL format: '{DATABASE_URL[:50]}...'. Must start with 'postgresql://' or 'postgres://'")
    DATABASE_URL = None

# Additional database configuration
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"


if DATABASE_URL:
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
else:
    engine = None
    SessionLocal = None
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

# Product model
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    price = Column(String, nullable=False)
    sale_price = Column(Text)
    regular_price = Column(String)
    description = Column(Text)
    ingredients = Column(Text)
    capacity = Column(String)
    material = Column(String)
    colors = Column(Text)  # JSON string for colors array
    features = Column(Text)  # JSON string for features array
    collection = Column(String)
    promotion = Column(String)
    on_sale = Column(String)  # Boolean as string
    discount = Column(String)

def get_db():
    """Get database session, or None if DB is not configured"""
    try:
        if not SessionLocal:
            print("Database session requested but database is not configured.")
            yield None
            return
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    except Exception as e:
        print(f"Database session error: {e}")
        yield None

def create_tables():
    """Create database tables if DB is configured"""
    try:
        if not engine:
            print("Cannot create tables: database engine is not configured.")
            return
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Error creating tables: {e}")
        return

def get_connection():
    """Get database connection for direct queries, or None if not configured"""
    try:
        if not engine:
            print("Database connection requested but engine is not configured.")
            return None
        return engine.connect()
    except Exception as e:
        print(f"Error getting database connection: {e}")
        return None

def validate_database_config():
    """Validate database configuration and connection"""
    if not engine:
        print("Database engine is not configured.")
        return False
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connection successful")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("Please check your DATABASE_URL and ensure PostgreSQL is running")
        return False

def get_db_info():
    """Get database connection information (without exposing credentials)"""
    try:
        if not DATABASE_URL:
            return {"error": "DATABASE_URL not configured"}
            
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
    except Exception as e:
        return {"error": f"Unable to parse DATABASE_URL: {str(e)}"}
