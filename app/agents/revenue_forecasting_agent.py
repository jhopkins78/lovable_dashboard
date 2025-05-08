"""
revenue_forecasting_agent.py
----------------------------
Defines the RevenueForecastingAgent class for simple rule-based revenue forecasting.

- forecast: Enriches a lead with win_probability and estimated_revenue based on score and market_signal_detected.
"""

from typing import Dict

class RevenueForecastingAgent:
    """
    Provides a simple rule-based forecast for lead win probability and estimated revenue.
    """

    def forecast(self, lead: Dict) -> Dict:
        """
        Applies forecasting rules to a lead.

        Rules:
        - If score > 80 and market_signal_detected is true:
            win_probability = 90, estimated_revenue = 50000
        - If score > 80 but market_signal_detected is false:
            win_probability = 75, estimated_revenue = 40000
        - If score <= 80 and market_signal_detected is true:
            win_probability = 60, estimated_revenue = 30000
        - Else:
            win_probability = 35, estimated_revenue = 15000

        Args:
            lead (dict): The lead dictionary.

        Returns:
            dict: The updated lead dictionary with forecast fields.
        """
        lead = lead.copy()
        score = lead.get("score", 0)
        signal = lead.get("market_signal_detected", False)

        if score > 80 and signal:
            lead["win_probability"] = 90
            lead["estimated_revenue"] = 50000
        elif score > 80 and not signal:
            lead["win_probability"] = 75
            lead["estimated_revenue"] = 40000
        elif score <= 80 and signal:
            lead["win_probability"] = 60
            lead["estimated_revenue"] = 30000
        else:
            lead["win_probability"] = 35
            lead["estimated_revenue"] = 15000

        return lead
