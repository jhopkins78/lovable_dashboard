"""
pipeline_optimization_agent.py
------------------------------
Defines the PipelineOptimizationAgent class for recommending pipeline actions.

- recommend_action: Enriches a lead with a recommended_action field based on win_probability and market_signal_detected.
"""

from typing import Dict

class PipelineOptimizationAgent:
    """
    Provides simple rule-based recommendations for pipeline movement.
    """

    def recommend_action(self, lead: Dict) -> Dict:
        """
        Applies pipeline optimization rules to a lead.

        Rules:
        - If win_probability >= 80:
            recommended_action = "Move to Contract Stage"
        - If win_probability between 50 and 79:
            recommended_action = "Schedule Follow-Up Call"
        - If market_signal_detected is true but win_probability < 50:
            recommended_action = "Send Discount Offer"
        - Otherwise:
            recommended_action = "Nurture — Low Priority"

        Args:
            lead (dict): The lead dictionary.

        Returns:
            dict: The updated lead dictionary with recommended_action.
        """
        lead = lead.copy()
        win_prob = lead.get("win_probability", 0)
        signal = lead.get("market_signal_detected", False)

        if win_prob >= 80:
            lead["recommended_action"] = "Move to Contract Stage"
        elif 50 <= win_prob < 80:
            lead["recommended_action"] = "Schedule Follow-Up Call"
        elif signal and win_prob < 50:
            lead["recommended_action"] = "Send Discount Offer"
        else:
            lead["recommended_action"] = "Nurture — Low Priority"

        return lead
