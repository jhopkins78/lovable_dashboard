from fastapi import APIRouter, Request

router = APIRouter()

def compose_report(
    dataset_id,
    analysis_summary,
    model_metrics,
    strategy_recommendations,
    visuals=None
):
    """
    Compose a Markdown-formatted lead intelligence report.
    """
    md = f"## Lead Intelligence Report\n\n"
    md += f"### Dataset Overview\n"
    md += f"- Dataset ID: {dataset_id}\n\n"
    md += f"### Auto Analysis Summary\n"
    md += f"{analysis_summary}\n\n"
    md += f"### Model Performance Metrics\n"
    md += "| Metric | Value |\n|---|---|\n"
    for k in ["model", "r2", "rmse", "mae"]:
        v = model_metrics.get(k, "N/A")
        md += f"| {k} | {v} |\n"
    md += "\n"
    md += f"### Strategy Recommendations\n"
    for rec in strategy_recommendations:
        md += f"- {rec}\n"
    md += "\n"
    if visuals:
        md += f"### Visual Summary\n"
        for vis in visuals:
            md += f"![{vis}]({vis})\n"
        md += "\n"
    return md

@router.post("/reports/compose")
async def compose_report_endpoint(request: Request):
    try:
        data = await request.json()
        dataset_id = data.get("dataset_id")
        analysis_summary = data.get("analysis_summary")
        model_metrics = data.get("model_metrics", {})
        strategy_recommendations = data.get("strategy_recommendations", [])
        visuals = data.get("visuals", None)

        if not (dataset_id and analysis_summary and model_metrics and strategy_recommendations):
            print("Missing required fields in /reports/compose request:", data)
            return {"status": "failed", "error": "Missing required fields"}

        markdown = compose_report(
            dataset_id,
            analysis_summary,
            model_metrics,
            strategy_recommendations,
            visuals
        )
        print("Example /reports/compose request:", data)
        print("Example /reports/compose response:", {"markdown": markdown[:120] + "..." if len(markdown) > 120 else markdown})
        return {"markdown": markdown}
    except Exception as e:
        print(f"Report composition error: {e}")
        return {"status": "failed", "error": str(e)}
