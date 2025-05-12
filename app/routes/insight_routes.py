"""
insight_routes.py
-----------------
Defines insight generation API routes.
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import InsightRequest, InsightResponse

router = APIRouter()

@router.get("/")
async def get_insights():
    """
    Skeleton endpoint to generate insights.
    """
    return {"message": "Get insights endpoint"}

@router.post("/insights/generate", response_model=InsightResponse)
async def generate_insight(payload: InsightRequest):
    """
    Generate insights for a lead using the insight agent.
    """
    try:
        from app.agents.insight_agent import run_insight_agent
        return run_insight_agent(payload.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
