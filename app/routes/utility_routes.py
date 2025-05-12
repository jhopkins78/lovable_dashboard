"""
utility_routes.py
-----------------
Defines utility endpoints: health check and report section addition.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ReportSectionRequest(BaseModel):
    section: str  # Markdown content

class ReportSectionResponse(BaseModel):
    success: bool

@router.post("/report/add_section", response_model=ReportSectionResponse)
async def add_report_section(payload: ReportSectionRequest):
    """
    Add a markdown section to a report (placeholder).
    """
    try:
        # Implement actual logic to add section to report
        return ReportSectionResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}
