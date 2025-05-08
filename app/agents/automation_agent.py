"""
automation_agent.py
-------------------
Defines the AutomationAgent class for simulating automated actions based on recommended pipeline actions.

- execute_action: Enriches a lead with an automation_status field based on recommended_action.
"""

from typing import Dict

class AutomationAgent:
    """
    Simulates automation of actions for leads based on recommended_action.
    """

    def execute_action(self, lead: Dict) -> Dict:
        """
        Applies automation logic to a lead.

        Rules:
        - If recommended_action == "Move to Contract Stage":
            automation_status = "CRM task created"
        - If recommended_action == "Schedule Follow-Up Call":
            automation_status = "Follow-up call scheduled"
        - If recommended_action == "Send Discount Offer":
            automation_status = "Discount email sent"
        - If recommended_action == "Nurture — Low Priority":
            automation_status = "Nurture task scheduled"
        - Otherwise:
            automation_status = "No action taken"

        Args:
            lead (dict): The lead dictionary.

        Returns:
            dict: The updated lead dictionary with automation_status.
        """
        lead = lead.copy()
        action = lead.get("recommended_action", "")

        if action == "Move to Contract Stage":
            lead["automation_status"] = "CRM task created"
        elif action == "Schedule Follow-Up Call":
            lead["automation_status"] = "Follow-up call scheduled"
        elif action == "Send Discount Offer":
            lead["automation_status"] = "Discount email sent"
        elif action == "Nurture — Low Priority":
            lead["automation_status"] = "Nurture task scheduled"
        else:
            lead["automation_status"] = "No action taken"

        return lead
