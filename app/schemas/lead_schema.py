from pydantic import BaseModel

class LeadAnalysisRequest(BaseModel):
    lead_name: str
    email: str
    job_title: str
    intent: str
    company: str
