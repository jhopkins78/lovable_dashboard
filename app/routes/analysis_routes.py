from fastapi import APIRouter, Request
import pandas as pd

# Import the in-memory registry from dataset_routes for demo purposes
from app.routes.dataset_routes import DATASET_REGISTRY

import os
import time

router = APIRouter()

# Track last analysis run (in-memory for demo)
LAST_ANALYSIS_RUN = {"dataset_id": None, "timestamp": None}

def load_dataset_by_id(dataset_id):
    # Try in-memory registry first
    for ds in DATASET_REGISTRY.values():
        if ds["dataset_id"] == dataset_id:
            print(f"[LOAD] Dataset loaded from memory: {dataset_id}")
            # In production, load from disk or DB
            # Here, return a dummy DataFrame
            return pd.DataFrame({
                "col1": [1, 2, 3],
                "col2": ["a", "b", "c"]
            })
    # Fallback: try loading from disk
    import os
    disk_path = f"./data/uploads/{dataset_id}.csv"
    if os.path.exists(disk_path):
        print(f"[LOAD] Dataset loaded from disk: {dataset_id}")
        return pd.read_csv(disk_path)
    raise ValueError("Dataset not found")

def run_eda_agent(df):
    # Stub: return example EDA results
    return {
        "summary": "3 rows, 2 columns. No missing values.",
        "columns": list(df.columns),
        "head": df.head(3).to_dict(orient="records")
    }

def run_modeling_pipeline(df):
    # Stub: return example modeling results
    return {
        "model": "LinearRegression",
        "r2": 0.82,
        "mae": 3.1,
        "rmse": 4.2
    }

def evaluate_models(model_results):
    # Stub: return example evaluation
    return {
        "best_model": model_results["model"],
        "score": model_results["r2"],
        "notes": "LinearRegression selected based on r2."
    }

def compose_markdown_report(eda, modeling, evaluation):
    md = "## AI Analysis Report\n\n"
    md += "### EDA Summary\n"
    md += f"{eda['summary']}\n\n"
    md += "### Model Performance\n"
    md += f"- Model: {modeling['model']}\n"
    md += f"- R2: {modeling['r2']}\n"
    md += f"- MAE: {modeling['mae']}\n"
    md += f"- RMSE: {modeling['rmse']}\n\n"
    md += "### Evaluation\n"
    md += f"Best Model: {evaluation['best_model']} (R2: {evaluation['score']})\n"
    md += f"Notes: {evaluation['notes']}\n"
    return md

@router.post("/start")
async def run_full_analysis(payload: dict):
    dataset_id = payload.get("dataset_id")
    if not dataset_id:
        return {"status": "failed", "error": "No dataset_id provided"}
    try:
        df = load_dataset_by_id(dataset_id)
        eda_results = run_eda_agent(df)
        model_results = run_modeling_pipeline(df)
        evaluation = evaluate_models(model_results)
        markdown = compose_markdown_report(eda_results, model_results, evaluation)
        # Log last analysis run
        LAST_ANALYSIS_RUN["dataset_id"] = dataset_id
        LAST_ANALYSIS_RUN["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return {
            "status": "completed",
            "eda": eda_results,
            "modeling": model_results,
            "evaluation": evaluation,
            "markdown": markdown
        }
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@router.get("/logs")
async def analysis_logs():
    # List available dataset files
    uploads_dir = "./data/uploads"
    try:
        files = []
        if os.path.exists(uploads_dir):
            for fname in os.listdir(uploads_dir):
                if fname.endswith(".csv"):
                    files.append(fname)
        logs = {
            "available_datasets": files,
            "last_analysis_run": LAST_ANALYSIS_RUN
        }
        print(f"[LOGS] Analysis logs requested: {logs}")
        return logs
    except Exception as e:
        return {"status": "failed", "error": str(e)}
