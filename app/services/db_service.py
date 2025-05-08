"""
db_service.py
-------------
Handles database connections and operations.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Example: Replace with your actual database URL
DATABASE_URL = "postgresql://user:password@localhost/dbname"

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
