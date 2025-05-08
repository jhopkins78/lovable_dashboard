from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import io

app = Flask(__name__)
CORS(app)

# Dummy data for leads
DUMMY_LEADS = [
    {
        "name": "John Doe",
        "company": "Acme Inc.",
        "score": 87,
        "summary": "High potential",
        "market_signal": "Positive news",
        "win_probability": 75,
        "estimated_revenue": 50000,
        "recommended_action": "Move to Contract Stage",
        "automation_status": "Scheduled",
        "coaching_tip": "Leverage urgency"
    },
    {
        "name": "Jane Smith",
        "company": "Beta Corp.",
        "score": 92,
        "summary": "Decision maker engaged",
        "market_signal": "New funding",
        "win_probability": 82,
        "estimated_revenue": 120000,
        "recommended_action": "Send Proposal",
        "automation_status": "Completed",
        "coaching_tip": "Highlight ROI"
    },
    {
        "name": "Alice Johnson",
        "company": "Gamma LLC",
        "score": 68,
        "summary": "Needs follow-up",
        "market_signal": "Neutral",
        "win_probability": 55,
        "estimated_revenue": 30000,
        "recommended_action": "Schedule Call",
        "automation_status": "Pending",
        "coaching_tip": "Personalize outreach"
    }
]

@app.route('/get_leads', methods=['GET'])
def get_leads():
    return jsonify(DUMMY_LEADS)

@app.route('/optimize_pipeline', methods=['POST'])
def optimize_pipeline():
    return jsonify({"message": "Pipeline optimized successfully"})

@app.route('/optimize', methods=['POST'])
def optimize():
    # Accept JSON (list of leads) or CSV file upload
    if request.content_type and "application/json" in request.content_type:
        leads = request.get_json()
        df = pd.DataFrame(leads)
    elif request.content_type and "multipart/form-data" in request.content_type:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        file = request.files["file"]
        df = pd.read_csv(file)
    else:
        return jsonify({"error": "Unsupported content type"}), 400

    # Scoring rules
    def score_lead(row):
        score = 0
        # Field: Lead Source
        if row.get("Lead Source") == "Organic Search":
            score += 20
        if row.get("Lead Source") == "Direct Traffic":
            score += 15
        if row.get("Lead Source") == "Olark Chat":
            score += 10
        # Field: TotalVisits
        try:
            if float(row.get("TotalVisits", 0)) > 3:
                score += 10
        except Exception:
            pass
        # Field: Total Time Spent on Website
        try:
            if float(row.get("Total Time Spent on Website", 0)) > 300:
                score += 15
        except Exception:
            pass
        # Field: Lead Profile
        if row.get("Lead Profile") == "Potential Lead":
            score += 25
        # Field: Asymmetrique Activity Score
        try:
            if float(row.get("Asymmetrique Activity Score", 0)) > 15:
                score += 10
        except Exception:
            pass
        # Field: Asymmetrique Profile Score
        try:
            if float(row.get("Asymmetrique Profile Score", 0)) > 15:
                score += 10
        except Exception:
            pass
        # Field: Last Notable Activity
        if row.get("Last Notable Activity") == "Email Opened":
            score += 15
        return score

    df["Score"] = df.apply(score_lead, axis=1)
    # Return as JSON, sorted by Score descending
    result = df.sort_values("Score", ascending=False).to_dict(orient="records")
    return jsonify(result)

@app.route('/automate_actions', methods=['POST'])
def automate_actions():
    return jsonify({"message": "Automation completed successfully"})

@app.route('/generate_coaching', methods=['POST'])
def generate_coaching():
    # Return dummy coaching tips for each lead in the posted data, or a generic message if no data
    leads = request.get_json(silent=True)
    if isinstance(leads, list):
        for lead in leads:
            lead["coaching_tip"] = "Keep momentum high"
        return jsonify(leads)
    return jsonify({"message": "Coaching tips generated successfully"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
