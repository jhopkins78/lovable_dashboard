"""
connector_agent.py
------------------
Agent for fetching structured data from third-party APIs (HubSpot, Shopify, Stripe, etc.).
Saves normalized data to /data/raw/{source}/timestamped_file.json or .csv.
Logs each pull to /logs/connector_log.csv.
"""

import os
import json
import csv
import httpx
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from pydantic import BaseModel, Field, validator

# --- Pydantic Input Model ---

class ConnectorFetchRequest(BaseModel):
    source: str = Field(..., description="Data source, e.g., 'hubspot', 'shopify', 'stripe'")
    credentials: Dict[str, Any]
    params: Optional[Dict[str, Any]] = None

    @validator("source")
    def validate_source(cls, v):
        allowed = {"hubspot", "shopify", "stripe"}
        if v.lower() not in allowed:
            raise ValueError(f"Unsupported source: {v}")
        return v.lower()

# --- Main Agent Logic ---

def fetch_data_from_source(source: str, credentials: Dict[str, Any], params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if source == "hubspot":
        return fetch_hubspot_data(credentials, params)
    elif source == "shopify":
        return fetch_shopify_data(credentials, params)
    elif source == "stripe":
        return fetch_stripe_data(credentials, params)
    else:
        raise ValueError(f"Unsupported source: {source}")

def fetch_hubspot_data(credentials, params):
    api_key = credentials.get("api_key")
    if not api_key:
        raise ValueError("Missing HubSpot API key")
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {"Authorization": f"Bearer {api_key}"}
    query = params or {}
    with httpx.Client(timeout=30) as client:
        resp = client.get(url, headers=headers, params=query)
        resp.raise_for_status()
        return resp.json()

def fetch_shopify_data(credentials, params):
    api_key = credentials.get("api_key")
    password = credentials.get("password")
    shop = credentials.get("shop")
    if not (api_key and password and shop):
        raise ValueError("Missing Shopify credentials")
    url = f"https://{api_key}:{password}@{shop}.myshopify.com/admin/api/2023-01/orders.json"
    query = params or {}
    with httpx.Client(timeout=30) as client:
        resp = client.get(url, params=query)
        resp.raise_for_status()
        return resp.json()

def fetch_stripe_data(credentials, params):
    api_key = credentials.get("api_key")
    if not api_key:
        raise ValueError("Missing Stripe API key")
    url = "https://api.stripe.com/v1/customers"
    headers = {"Authorization": f"Bearer {api_key}"}
    query = params or {}
    with httpx.Client(timeout=30) as client:
        resp = client.get(url, headers=headers, params=query)
        resp.raise_for_status()
        return resp.json()

def save_data(source: str, data: Any):
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(f"data/raw/{source}")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{timestamp}.json"
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    return str(out_path)

def log_pull(source: str, success: bool, record_count: int):
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / "connector_log.csv"
    exists = log_path.exists()
    with open(log_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not exists:
            writer.writerow(["timestamp", "source", "success", "record_count"])
        writer.writerow([datetime.utcnow().isoformat(), source, "success" if success else "fail", record_count])

def connector_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        req = ConnectorFetchRequest(**payload)
        data = fetch_data_from_source(req.source, req.credentials, req.params)
        out_path = save_data(req.source, data)
        record_count = len(data) if isinstance(data, list) else (len(data.get("results", [])) if isinstance(data, dict) and "results" in data else 1)
        log_pull(req.source, True, record_count)
        return {"status": "success", "file": out_path, "record_count": record_count}
    except Exception as e:
        log_pull(payload.get("source", "unknown"), False, 0)
        return {"status": "fail", "error": str(e)}
