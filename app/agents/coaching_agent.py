"""
coaching_agent.py
-----------------
Defines the CoachingAgent class for generating sales coaching tips for leads.

- generate_coaching_tip: Enriches a lead with a coaching_tip field based on market_signal_detected and win_probability.
"""

from typing import Dict

class CoachingAgent:
    """
    Provides simple rule-based coaching tips for sales reps based on lead context.
    """

    def generate_coaching_tip(self, lead: Dict) -> Dict:
        """
        Applies coaching logic to a lead.

        Rules:
        - If market_signal_detected == true and win_probability >= 80:
            coaching_tip = "Use market momentum to close quickly."
        - If win_probability >= 80 but no market signal:
            coaching_tip = "Highlight lead's internal motivation to close deal."
        - If win_probability between 50 and 79:
            coaching_tip = "Address objections early and reinforce value proposition."
        - If win_probability < 50:
            coaching_tip = "Focus on building relationship and understanding lead’s deeper needs."

        Args:
            lead (dict): The lead dictionary.

        Returns:
            dict: The updated lead dictionary with coaching_tip.
        """
        lead = lead.copy()
        win_prob = lead.get("win_probability", 0)
        signal = lead.get("market_signal_detected", False)

        if signal and win_prob >= 80:
            lead["coaching_tip"] = "Use market momentum to close quickly."
        elif win_prob >= 80:
            lead["coaching_tip"] = "Highlight lead's internal motivation to close deal."
        elif 50 <= win_prob < 80:
            lead["coaching_tip"] = "Address objections early and reinforce value proposition."
        else:
            lead["coaching_tip"] = "Focus on building relationship and understanding lead’s deeper needs."

        return lead
