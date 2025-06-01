from fastapi import APIRouter, Request
import pandas as pd

router = APIRouter()

def detect_time_column(df):
    for col in df.columns:
        try:
            parsed = pd.to_datetime(df[col], errors='coerce')
            if parsed.notnull().sum() > len(df) * 0.8:
                return col
        except Exception:
            continue
    return None

def detect_target_column(df):
    numeric_cols = df.select_dtypes(include=["number"]).columns
    if not numeric_cols.any():
        return None
    return df[numeric_cols].var().idxmax()

def load_dataset_from_supabase(dataset_id):
    """
    Stub for loading a dataset from Supabase.
    Raises ValueError if dataset_id is invalid.
    """
    if dataset_id != "demo":
        raise ValueError("Invalid or missing dataset ID")
    # Dummy quarterly revenue data
    return pd.DataFrame({
        "period": ["2025-Q1", "2025-Q2"],
        "revenue": [11500, 12800],
        "leads": [120, 135]
    })

def simple_forecast(df, time_col, target_col):
    """
    Simple linear projection for the next two periods using detected columns.
    """
    y = df[target_col].values
    periods = df[time_col].values
    if len(y) < 2:
        raise ValueError("Not enough data for forecasting")
    # Linear trend: extrapolate difference
    diff = y[-1] - y[-2]
    next1 = y[-1] + diff
    next2 = next1 + diff
    # Next periods (stub)
    last_period = periods[-1]
    if "Q" in str(last_period):
        year, q = str(last_period).split("-Q")
        year = int(year)
        q = int(q)
        next_periods = []
        for _ in range(2):
            q += 1
            if q > 4:
                q = 1
                year += 1
            next_periods.append(f"{year}-Q{q}")
    else:
        next_periods = ["next1", "next2"]
    forecast_values = [
        {"period": next_periods[0], "value": int(next1)},
        {"period": next_periods[1], "value": int(next2)}
    ]
    pct = (next1 - y[-1]) / y[-1] * 100
    summary = f"{target_col.capitalize()} expected to increase {pct:.1f}% over the next period"
    return {
        "forecast_target": target_col,
        "time_column": time_col,
        "forecast_values": forecast_values,
        "method": "linear_regression",
        "summary": summary
    }

@router.post("/forecast/generate")
async def generate_forecast(request: Request):
    try:
        data = await request.json()
        dataset_id = data.get("dataset_id")
        if not dataset_id:
            print("Missing dataset_id in request.")
            return {"status": "failed", "error": "Invalid or missing dataset ID"}
        df = load_dataset_from_supabase(dataset_id)
        time_col = detect_time_column(df)
        target_col = detect_target_column(df)
        if not time_col or not target_col:
            print("Could not detect a valid time or numeric target column.")
            return {
                "status": "failed",
                "error": "Could not detect a valid time or numeric target column."
            }
        result = simple_forecast(df, time_col, target_col)
        return result
    except Exception as e:
        print(f"Forecast generation error: {e}")
        return {"status": "failed", "error": str(e)}
