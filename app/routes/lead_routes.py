"""
lead_routes.py
--------------
Defines lead management API routes.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_leads():
    """
    Skeleton endpoint to fetch leads.
    """
    # Implement logic to fetch leads here
    return {"message": "Get leads endpoint"}

@router.post("/analyze")
async def analyze_lead(payload: dict):
    """
    Analyze a lead using the lead intelligence agent.
    """
    from app.agents.lead_intelligence_agent import analyze_lead
    return analyze_lead(payload)

@router.post("/ltv")
async def estimate_ltv(payload: dict):
    """
    Estimate the lifetime value of a lead using the LTV agent.
    """
    from app.agents.ltv_agent import estimate_lifetime_value
    return estimate_lifetime_value(payload)
