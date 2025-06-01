from fastapi import APIRouter, Request
import pandas as pd
from datetime import datetime

router = APIRouter()

def load_dataset_from_supabase(dataset_id):
    """
    Stub for loading a dataset from Supabase.
    Raises ValueError if dataset_id is invalid.
    """
    # For demonstration, accept only "demo" as a valid ID
    if dataset_id != "demo":
        raise ValueError("Invalid or missing dataset ID")
    # Return a dummy DataFrame
    return pd.DataFrame({
        "lead_source": ["web", "referral", "web", "event"],
        "intent_score": [0.9, 0.7, 0.8, 0.6]
    })

def scan_strategy(dataset_id):
    """
    Scans the dataset and returns recommendations and a summary.
    """
    df = load_dataset_from_supabase(dataset_id)
    # Heuristic: top lead sources
    top_sources = df["lead_source"].value_counts().index.tolist()
    avg_intent = df["intent_score"].mean()
    recommendations = [
        f"Focus on top lead sources: {', '.join(top_sources[:2])}.",
        f"Average intent score is {avg_intent:.2f}—target leads above this threshold.",
        "Consider increasing outreach to referral leads.",
        "Monitor event-based leads for conversion spikes."
    ]
    summary = f"{len(df)} rows scanned"
    return {
        "recommendations": recommendations[:4],
        "dataset_summary": summary
    }

@router.post("/strategy/scan")
async def strategy_scan(request: Request):
    try:
        data = await request.json()
        dataset_id = data.get("dataset_id")
        if not dataset_id:
            print("Missing dataset_id in request.")
            return {"status": "failed", "error": "Invalid or missing dataset ID"}
        # Log scan timestamp
        print(f"Strategy scan started for dataset_id={dataset_id} at {datetime.now().isoformat()}")
        result = scan_strategy(dataset_id)
        return result
    except Exception as e:
        print(f"Strategy scan error: {e}")
        return {"status": "failed", "error": str(e)}
