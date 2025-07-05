"""
Robust Database configuration for ZUS Coffee chatbot
PostgreSQL with SQLAlchemy ORM + graceful fallback handling
"""
import os
import logging
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

logger = logging.getLogger(__name__)

# Database configuration with fallback handling
DATABASE_URL = os.getenv("DATABASE_URL")
DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "production")  # production, development, test

def validate_and_setup_database():
    """
    Validate database configuration and set up connection with fallback handling.
    Returns tuple: (engine, SessionLocal, Base, database_available)
    """
    global DATABASE_URL
    
    # Handle missing DATABASE_URL
    if not DATABASE_URL:
        if DEPLOYMENT_MODE == "production":
            logger.error("DATABASE_URL environment variable is required in production")
            raise ValueError(
                "DATABASE_URL environment variable is required. "
                "Please set it to your PostgreSQL connection string. "
                "Example: postgresql://username:password@host:port/database"
            )
        else:
            logger.warning("DATABASE_URL not set, using in-memory SQLite for development")
            DATABASE_URL = "sqlite:///:memory:"
    
    # Clean up DATABASE_URL in case it has the variable name as prefix
    if DATABASE_URL.startswith("DATABASE_URL="):
        DATABASE_URL = DATABASE_URL.replace("DATABASE_URL=", "")
        logger.warning("DATABASE_URL had incorrect prefix, cleaned it up")
    
    # Validate DATABASE_URL format for production
    if DEPLOYMENT_MODE == "production" and not DATABASE_URL.startswith(("postgresql://", "postgres://")):
        logger.error(f"Invalid DATABASE_URL format in production: '{DATABASE_URL[:50]}...'")
        raise ValueError(
            f"Invalid DATABASE_URL format: '{DATABASE_URL[:50]}...' "
            "Must start with 'postgresql://' or 'postgres://' in production"
        )
    
    # Database configuration
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "60"))
    DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"
    
    try:
        # Create engine with appropriate settings
        if DATABASE_URL.startswith("sqlite"):
            # SQLite configuration (development/fallback)
            engine = create_engine(
                DATABASE_URL,
                echo=DB_ECHO,
                pool_pre_ping=True,
                connect_args={"check_same_thread": False}  # SQLite specific
            )
            logger.info("Using SQLite database (development mode)")
        else:
            # PostgreSQL configuration (production)
            engine = create_engine(
                DATABASE_URL,
                pool_size=DB_POOL_SIZE,
                max_overflow=DB_MAX_OVERFLOW,
                pool_timeout=DB_POOL_TIMEOUT,
                echo=DB_ECHO,
                pool_pre_ping=True
            )
            logger.info("Using PostgreSQL database (production mode)")
        
        # Test the connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base = declarative_base()
        
        logger.info("Database connection established successfully")
        return engine, SessionLocal, Base, True
        
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        
        if DEPLOYMENT_MODE == "production":
            # In production, we must have a working database
            raise RuntimeError(f"Production database connection failed: {e}")
        else:
            # In development, create a fallback in-memory database
            logger.warning("Falling back to in-memory SQLite database")
            fallback_engine = create_engine("sqlite:///:memory:", echo=False)
            FallbackSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=fallback_engine)
            FallbackBase = declarative_base()
            return fallback_engine, FallbackSessionLocal, FallbackBase, False

# Initialize database with error handling
try:
    engine, SessionLocal, Base, database_available = validate_and_setup_database()
except Exception as e:
    logger.critical(f"Critical database setup error: {e}")
    # Last resort: create minimal fallback for basic operation
    engine = create_engine("sqlite:///:memory:", echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    database_available = False
    logger.warning("Using emergency fallback database - limited functionality")

# Database models
class ChatSession(Base):
    """Chat session model for storing conversation history."""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    message_count = Column(Integer, default=0)

class ChatMessage(Base):
    """Chat message model for storing individual messages."""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    message = Column(Text)
    response = Column(Text)
    intent = Column(String(100))
    confidence = Column(String(10))
    timestamp = Column(DateTime, default=datetime.utcnow)

def create_tables():
    """Create database tables with error handling."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        if DEPLOYMENT_MODE == "production":
            raise RuntimeError(f"Failed to create database tables in production: {e}")

def get_db():
    """Database dependency for FastAPI with error handling."""
    if not database_available:
        logger.warning("Database not available, using fallback")
        # Return a mock database session that doesn't actually persist
        return MockDBSession()
    
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

class MockDBSession:
    """Mock database session for when database is not available."""
    
    def add(self, obj):
        pass
    
    def commit(self):
        pass
    
    def rollback(self):
        pass
    
    def close(self):
        pass
    
    def query(self, *args):
        return MockQuery()

class MockQuery:
    """Mock query object."""
    
    def filter(self, *args):
        return self
    
    def first(self):
        return None
    
    def all(self):
        return []

# Health check function
def check_database_health():
    """Check if database is healthy and accessible."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "available": database_available}
    except Exception as e:
        return {"status": "error", "error": str(e), "available": False}

# Export key components
__all__ = [
    'engine', 'SessionLocal', 'Base', 'database_available',
    'ChatSession', 'ChatMessage', 'create_tables', 'get_db',
    'check_database_health'
]
