"""
webhook_listener_agent.py
-------------------------
Agent for listening to incoming webhooks from third-party platforms (Stripe, Facebook Lead Ads, Zapier, etc.).
Saves payloads to /data/raw/webhooks/{source}/{timestamp}.json.
Logs events to /logs/webhook_log.csv.
Handles Stripe signature verification and challenge verification (basic stubs).
"""

import os
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import Request, HTTPException

def save_webhook_payload(source: str, payload: Dict[str, Any]):
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(f"data/raw/webhooks/{source}")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{timestamp}.json"
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    return str(out_path)

def log_webhook_event(source: str, status_code: int):
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / "webhook_log.csv"
    exists = log_path.exists()
    with open(log_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not exists:
            writer.writerow(["timestamp", "source", "status_code"])
        writer.writerow([datetime.utcnow().isoformat(), source, status_code])

def verify_stripe_signature(request: Request) -> bool:
    # Placeholder for Stripe signature verification
    # In production, use stripe.Webhook.construct_event() with the secret
    return True

def handle_challenge_verification(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # Facebook/other platforms may send a challenge for verification
    if "challenge" in payload:
        return {"challenge": payload["challenge"]}
    return None

async def webhook_listener_agent(source: str, request: Request) -> Dict[str, Any]:
    try:
        payload = await request.json()
        # Stripe signature verification (if needed)
        if source == "stripe":
            if not verify_stripe_signature(request):
                log_webhook_event(source, 400)
                raise HTTPException(status_code=400, detail="Invalid Stripe signature")
        # Challenge verification
        challenge_response = handle_challenge_verification(payload)
        if challenge_response:
            log_webhook_event(source, 200)
            return challenge_response
        # Save payload
        out_path = save_webhook_payload(source, payload)
        log_webhook_event(source, 200)
        return {"status": "received", "file": out_path}
    except Exception as e:
        log_webhook_event(source, 500)
        raise HTTPException(status_code=500, detail=str(e))
