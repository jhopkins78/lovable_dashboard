from fastapi import APIRouter, Request
import pandas as pd

# Import the in-memory registry from dataset_routes for demo purposes
from app.routes.dataset_routes import DATASET_REGISTRY

router = APIRouter()

def load_dataset_by_id(dataset_id):
    # For demo: find the latest dataset with this id in the registry
    for ds in DATASET_REGISTRY.values():
        if ds["dataset_id"] == dataset_id:
            # In production, load from disk or DB
            # Here, return a dummy DataFrame
            return pd.DataFrame({
                "col1": [1, 2, 3],
                "col2": ["a", "b", "c"]
            })
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
        return {
            "status": "completed",
            "eda": eda_results,
            "modeling": model_results,
            "evaluation": evaluation,
            "markdown": markdown
        }
    except Exception as e:
        return {"status": "failed", "error": str(e)}
