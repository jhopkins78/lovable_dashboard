# ltv_agent.py

# TODO: Implement lifetime value (LTV) scoring for leads

class LtvAgent:
    def __init__(self):
        pass

    def run(self, lead_data):
        """
        Estimates a simple LTV based on lead score and company size.
        """
        # TODO: Refine LTV model (e.g., add OpenAI analysis, advanced features, etc.)
        base_value = 1000
        company_size = lead_data.get('company_size', 1)  # Assume 1 if missing
        score_multiplier = lead_data.get('score', 50) / 100
        projected_ltv = base_value * company_size * score_multiplier
        return round(projected_ltv, 2)


import openai
import os
from app.services.supabase_service import log_agent_activity

def estimate_lifetime_value(payload):
    """
    Function to estimate the lifetime value of a lead with the provided payload.
    
    Args:
        payload (dict): The lead data to analyze.
        
    Returns:
        dict: A dictionary containing the status, echoed payload, ltv_estimate, and optional error.
    """
    print("LTV PAYLOAD:", payload)
    
    input_data = {}
    if isinstance(payload, dict):
        input_data = payload
    else:
        input_data = {"raw_input": str(payload)}
    
    response = {
        "status": "ok",
        "echo": input_data,
        "ltv_estimate": "No LTV estimate generated.",
        "error": ""
    }
    
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("Missing OPENAI_API_KEY")

        print("Sending lead data to OpenAI for LTV estimation...")
        summary = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a financial forecasting assistant. Analyze the provided lead data to estimate lifetime value (LTV) based on deal amount, frequency, contract length, and other relevant factors."},
                {"role": "user", "content": str(input_data)}
            ],
            max_tokens=300
        )
        
        generated = summary["choices"][0]["message"]["content"]
        print("OpenAI returned LTV estimate:", generated)
        response["ltv_estimate"] = generated
    except Exception as e:
        print("LTV Agent Error:", str(e))
        response["error"] = str(e)

    # Log to Supabase
    log_agent_activity("ltv", payload, response)
    
    return response
