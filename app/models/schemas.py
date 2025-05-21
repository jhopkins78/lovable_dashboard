from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# --- Insight Generation ---

class InsightRequest(BaseModel):
    input: str

class InsightResponse(BaseModel):
    insight: str
    confidence: float
    timestamp: str

# --- Lead Analysis ---

class LeadAnalysisRequest(BaseModel):
    lead_name: str
    email: str
    job_title: str
    intent: str
    company: str
    title: str
    company: str
    email: str
    intent: str

class CompanyInfo(BaseModel):
    size: Optional[str] = None
    industry: Optional[str] = None
    founded: Optional[str] = None
    location: Optional[str] = None

class ContactInfo(BaseModel):
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None

class EngagementHistory(BaseModel):
    last_interaction: Optional[str] = None
    interaction_count: Optional[int] = None
    channels: Optional[List[str]] = None

class EnrichedData(BaseModel):
    company_info: Optional[CompanyInfo] = None
    contact_info: Optional[ContactInfo] = None
    engagement_history: Optional[EngagementHistory] = None

class LeadAnalysisResponse(BaseModel):
    score: float
    enriched_data: EnrichedData
    recommendations: List[str]

# --- LTV Estimation ---

class LtvEstimateRequest(BaseModel):
    deal_amount: float
    repeat_purchases: int

class ConfidenceInterval(BaseModel):
    lower: float
    upper: float

class LtvFactor(BaseModel):
    name: str
    impact: float

class LtvEstimateResponse(BaseModel):
    estimated_ltv: float
    confidence_interval: ConfidenceInterval
    factors: List[LtvFactor]
