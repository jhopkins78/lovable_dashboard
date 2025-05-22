"""
lead_routes.py
--------------
Defines lead management API routes.
"""

from fastapi import APIRouter, HTTPException
from app.schemas.lead_schema import LeadAnalysisRequest
from app.models.schemas import (
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


from pydantic import BaseModel
import os
import openai

# You may want to tune these weights for your use case
STAGE_WEIGHT = {
    "Prospecting": 2,
    "Qualification": 4,
    "Proposal": 6,
    "Negotiation": 8,
    "Closed Won": 10,
    "Closed Lost": -5,
}
INDUSTRY_WEIGHT = {
    "B2B SaaS": 5,
    "E-Commerce": 3,
    "Healthcare": 4,
    "Finance": 2,
    "Other": 1,
}

class LeadPredictRequest(BaseModel):
    lead_name: str
    company: str
    deal_amount: float
    engagement_score: float
    industry: str
    stage: str

class LeadPredictResponse(BaseModel):
    lead_score: float
    classification: str
    gpt_summary: str

def classify_score(score):
    if score >= 80:
        return "High Priority"
    elif score >= 60:
        return "Medium Priority"
    else:
        return "Low Priority"

from app.services.db_service import log_prediction

@router.post("/leads/predict", response_model=LeadPredictResponse)
async def predict_lead(payload: LeadPredictRequest):
    try:
        # Rule-based scoring
        deal_amt = payload.deal_amount or 0
        engagement = payload.engagement_score or 0
        stage = payload.stage or "Other"
        industry = payload.industry or "Other"
        score = (
            (deal_amt / 1000) * 0.25 +
            engagement * 0.5 +
            STAGE_WEIGHT.get(stage, 0) +
            INDUSTRY_WEIGHT.get(industry, 0)
        )
        classification = classify_score(score)

        # GPT prompt
        openai_api_key = os.getenv("OPENAI_API_KEY")
        gpt_prompt = (
            f"Given a lead with a score of {int(score)} and the following attributes:\n"
            f"Lead Name: {payload.lead_name}\n"
            f"Company: {payload.company}\n"
            f"Deal Amount: {payload.deal_amount}\n"
            f"Engagement Score: {payload.engagement_score}\n"
            f"Industry: {payload.industry}\n"
            f"Stage: {payload.stage}\n"
            "Explain their likelihood of converting and suggest an outreach strategy."
        )
        gpt_summary = "No GPT response."
        if openai_api_key:
            client = openai.OpenAI(api_key=openai_api_key)
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a B2B sales strategist."},
                    {"role": "user", "content": gpt_prompt}
                ],
                max_tokens=120,
                temperature=0.7,
            )
            gpt_summary = completion.choices[0].message.content.strip()
        else:
            gpt_summary = "No OpenAI API key configured."

        result = {
            "lead_score": round(score, 2),
            "classification": classification,
            "gpt_summary": gpt_summary
        }
        # Log prediction to Supabase
        log_prediction(payload.dict(), result)

        return LeadPredictResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import traceback

import traceback

@router.post("/leads/analyze")
async def analyze_lead(payload: LeadAnalysisRequest):
    """
    Analyze a lead using the lead intelligence agent.
    """
    print(f"Incoming /leads/analyze request: {payload}")
    try:
        import os
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            print("Warning: OPENAI_API_KEY is missing or empty.")
        from app.agents.lead_intelligence_agent import analyze_lead as agent_analyze_lead
        try:
            result = agent_analyze_lead(payload.dict())
            # Ensure recommendations array is always present
            if isinstance(result, dict):
                if "recommendations" not in result or result["recommendations"] is None:
                    result["recommendations"] = []
            return result
        except Exception as gpt_exc:
            print("Exception during GPT call in /leads/analyze:")
            traceback.print_exc()
            raise
    except Exception as e:
        print("Exception in /leads/analyze:", e)
        traceback.print_exc()
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
