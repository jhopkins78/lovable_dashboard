"""
insight_agent.py
----------------
Implements the InsightSummarizationAgent class for generating intelligent lead opportunity summaries using GPT-4.

- generate_insight: Uses OpenAI GPT-4 (via service layer) to create a short summary of the lead's opportunity potential.
"""

from typing import Dict
from app.services.openai_service import OpenAIService

class InsightSummarizationAgent:
    """
    Provides methods to generate AI-powered insights for a lead.
    """

    def __init__(self, openai_service: OpenAIService):
        """
        Initialize with an OpenAIService instance.
        """
        self.openai_service = openai_service

    def generate_insight(self, lead_data: Dict) -> str:
        """
        Generates a 3–5 sentence summary of the lead's opportunity potential using GPT-4.
        Considers fields like company size, title, email domain, and enrichment fields.

        Args:
            lead_data (dict): The lead data, including enrichment fields.

        Returns:
            str: A clean, readable summary string.
        """
        # Compose a prompt for GPT-4 based on the lead data
        prompt = self._build_prompt(lead_data)

        # Call the OpenAI service layer to get the summary
        # Assumes openai_service.ask_gpt(prompt: str) -> str
        summary = self.openai_service.ask_gpt(prompt)

        # Ensure the summary is a clean, readable string
        return summary.strip()

    def _build_prompt(self, lead_data: Dict) -> str:
        """
        Helper to build a detailed prompt for GPT-4 based on lead data.

        Args:
            lead_data (dict): The lead data.

        Returns:
            str: The prompt to send to GPT-4.
        """
        # Extract relevant fields for the summary
        name = lead_data.get("name", "Unknown")
        company = lead_data.get("company", "Unknown Company")
        company_size = lead_data.get("company_size", "N/A")
        title = lead_data.get("title", "N/A")
        email = lead_data.get("email", "N/A")
        industry = lead_data.get("industry", "N/A")
        employee_size = lead_data.get("employee_size", "N/A")

        prompt = (
            f"You are a B2B sales intelligence assistant. "
            f"Given the following lead data, write a concise, intelligent summary (3–5 sentences) "
            f"of this lead's opportunity potential for a sales team. "
            f"Highlight company size, title seniority, industry, and any other relevant factors.\n\n"
            f"Lead Data:\n"
            f"- Name: {name}\n"
            f"- Company: {company}\n"
            f"- Company Size: {company_size}\n"
            f"- Title: {title}\n"
            f"- Email: {email}\n"
            f"- Industry: {industry}\n"
            f"- Employee Size: {employee_size}\n"
        )
        return prompt

# Example usage (in FastAPI route):
# from app.services.openai_service import OpenAIService
# openai_service = OpenAIService(api_key="YOUR_KEY")
# agent = InsightSummarizationAgent(openai_service)
# summary = agent.generate_insight(lead_data)

import openai
import os
from app.services.supabase_service import log_agent_activity

def run_insight_agent(payload):
    """
    Function to run the insight agent with the provided payload.
    
    Args:
        payload (Dict): The lead data to generate insights for.
        
    Returns:
        dict: A dictionary containing the status, echoed input, insight, and optional error.
    """
    print("RAW PAYLOAD RECEIVED:", payload)
    
    input_text = ""
    if isinstance(payload, dict):
        input_text = payload.get("input", "")
    else:
        input_text = str(payload)

    # Default fallback response
    response = {
        "status": "ok",
        "echo": input_text,
        "insight": "No insight generated. GPT logic not executed."
    }

    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable")

        print("Sending to OpenAI...")
        gpt_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a business analyst. Generate actionable insights from user-provided business data or statements."},
                {"role": "user", "content": input_text}
            ],
            max_tokens=300
        )

        generated_text = gpt_response["choices"][0]["message"]["content"]
        print("OpenAI returned:", generated_text)

        response["insight"] = generated_text
    except Exception as e:
        print("Insight Agent error:", str(e))
        response["insight"] = "Insight generation failed."
        response["error"] = str(e)

    # Log to Supabase
    log_agent_activity("insight", payload, response)
    
    return response
