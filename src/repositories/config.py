from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///data/records.db"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create the SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the declarative base for models
Base = declarative_base()

def configure_database():
    """Create all database tables if they do not exist."""
    # Import the models so SQLAlchemy's Base registry registers them
    from src.repositories.records import GenerationRecord
    import os
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    Base.metadata.create_all(bind=engine)
