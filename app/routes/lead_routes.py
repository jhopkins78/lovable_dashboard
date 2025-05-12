"""
lead_routes.py
--------------
Defines lead management API routes.
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    LeadAnalysisRequest,
    LeadAnalysisResponse,
    LtvEstimateRequest,
    LtvEstimateResponse,
)
from typing import List

router = APIRouter()

@router.get("/get_leads", response_model=List[dict])
async def get_leads():
    """
    Fetch all leads (placeholder).
    """
    try:
        # Replace with actual DB/service call
        return [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "risk_score": 0.2,
                "projected_ltv": 12000.0,
            }
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/leads/analyze", response_model=LeadAnalysisResponse)
async def analyze_lead(payload: LeadAnalysisRequest):
    """
    Analyze a lead using the lead intelligence agent.
    """
    try:
        from app.agents.lead_intelligence_agent import analyze_lead as agent_analyze_lead
        return agent_analyze_lead(payload.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/leads/ltv", response_model=LtvEstimateResponse)
async def estimate_ltv(payload: LtvEstimateRequest):
    """
    Estimate the lifetime value of a lead using the LTV agent.
    """
    try:
        from app.agents.ltv_agent import estimate_lifetime_value as agent_estimate_ltv
        return agent_estimate_ltv(payload.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
