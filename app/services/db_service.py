"""
db_service.py
-------------
Handles database connections and operations.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os
from supabase import create_client

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

def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

def log_prediction(data, result):
    from app.services.db_service import get_supabase_client
    supabase = get_supabase_client()

    def safe_str(val):
        return str(val) if val is not None else ""

    def safe_float(val):
        try:
            return float(val)
        except:
            return 0.0

    payload = {
        "lead_name": safe_str(data.get("lead_name")),
        "company": safe_str(data.get("company")),
        "deal_amount": safe_float(data.get("deal_amount")),
        "engagement_score": safe_float(data.get("engagement_score")),
        "industry": safe_str(data.get("industry")),
        "stage": safe_str(data.get("stage")),
        "lead_score": safe_float(result.get("lead_score")),
        "classification": safe_str(result.get("classification")),
        "gpt_summary": safe_str(result.get("gpt_summary"))
    }

    print("📦 Cleaned prediction payload:", payload)

    try:
        supabase.table("lead_predictions").insert(payload).execute()
        print("✅ Prediction logged successfully")
    except Exception as e:
        print("❌ Supabase insert failed:", e)
