from fastapi import APIRouter, Request
import pandas as pd

router = APIRouter()

def run_modeling_pipeline(df):
    """
    Stub for modeling pipeline.
    Returns a dict with summary, metrics, and visuals.
    """
    # Example output
    return {
        "summary": "KNeighbors regression achieved strong performance on the dataset.",
        "metrics": {
            "model": "KNeighbors",
            "r2": 0.85,
            "rmse": 3.4,
            "mae": 2.1
        },
        "visuals": ["histogram.png", "heatmap.png"]
    }

@router.post("/ml/auto")
async def auto_analysis(request: Request):
    try:
        data = await request.json()
        # Simulate loading a dataset from a path or inline data
        if "dataset_path" in data:
            try:
                df = pd.read_csv(data["dataset_path"])
            except Exception as e:
                print(f"Dataset loading failed: {e}")
                return {"status": "failed", "error": "Dataset not found"}
        elif "data" in data:
            try:
                df = pd.DataFrame(data["data"])
            except Exception as e:
                print(f"Data parsing failed: {e}")
                return {"status": "failed", "error": "Invalid data format"}
        else:
            print("No dataset_path or data provided in request.")
            return {"status": "failed", "error": "No dataset provided"}

        # Run modeling pipeline
        result = run_modeling_pipeline(df)
        # Validate output structure
        if not isinstance(result, dict) or "summary" not in result or "metrics" not in result:
            print("Modeling pipeline returned invalid structure.")
            return {"status": "failed", "error": "Modeling pipeline error"}
        return result
    except Exception as exc:
        print(f"Auto analysis error: {exc}")
        return {"status": "failed", "error": str(exc)}
