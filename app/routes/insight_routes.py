"""
insight_routes.py
-----------------
Defines insight generation API routes.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_insights():
    """
    Skeleton endpoint to generate insights.
    """
    # Implement logic to generate insights here
    return {"message": "Get insights endpoint"}

@router.post("/generate")
async def generate_insight(payload: dict):
    """
    Generate insights for a lead using the insight agent.
    """
    from app.agents.insight_agent import run_insight_agent
    return run_insight_agent(payload)
