"""
webhook_routes.py
-----------------
Route for the Webhook Listener Agent: receives webhooks from third-party platforms.
"""

from fastapi import APIRouter, Request
from app.agents.webhook_listener_agent import webhook_listener_agent

router = APIRouter()

@router.post("/webhook/{source}")
async def webhook_listener(source: str, request: Request):
    """
    Listen for incoming webhooks from third-party platforms.
    """
    return await webhook_listener_agent(source, request)
