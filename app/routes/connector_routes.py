"""
connector_routes.py
-------------------
Route for the Connector Agent: fetches data from third-party APIs.
"""

from fastapi import APIRouter, HTTPException
from app.agents.connector_agent import ConnectorFetchRequest, connector_agent

router = APIRouter()

@router.post("/connector/fetch_data")
async def fetch_data(request: ConnectorFetchRequest):
    """
    Fetch data from a third-party API (HubSpot, Shopify, Stripe, etc.).
    """
    result = connector_agent(request.dict())
    if result.get("status") == "fail":
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result
