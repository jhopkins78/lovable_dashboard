"""
lead_intelligence_agent.py
--------------------------
Implements the LeadIntelligenceAgent class for lead scoring and enrichment.

- score_lead: Scores a lead from 0 to 100 based on weighted fields.
- enrich_lead: Simulates enrichment by adding fields like industry and employee size.
- _calculate_field_weight: Helper for field-specific scoring logic.
"""

from typing import Dict

class LeadIntelligenceAgent:
    """
    Provides methods to score and enrich lead data for prioritization and analysis.
    """

    def score_lead(self, lead_data: Dict) -> int:
        """
        Scores a lead using a simple weighted model.
        Fields considered:
            - company_size: Larger companies score higher.
            - title: Senior titles score higher.
            - email: Business domains score higher.
            - phone: Presence adds to score.

        Returns:
            int: Lead score between 0 and 100.
        """
        score = 0
        max_score = 100
        weights = {
            "company_size": 40,
            "title": 30,
            "email": 20,
            "phone": 10
        }

        # Company size scoring
        score += self._calculate_field_weight("company_size", lead_data.get("company_size", None)) * weights["company_size"]

        # Title scoring
        score += self._calculate_field_weight("title", lead_data.get("title", None)) * weights["title"]

        # Email domain scoring
        score += self._calculate_field_weight("email", lead_data.get("email", None)) * weights["email"]

        # Phone presence scoring
        score += self._calculate_field_weight("phone", lead_data.get("phone", None)) * weights["phone"]

        # Normalize to 0-100
        score = int(min(max_score, max(0, score // 100)))
        return score

    def enrich_lead(self, lead_data: Dict) -> Dict:
        """
        Simulates enrichment of lead data.
        Adds:
            - industry: Based on email domain.
            - employee_size: Category based on company_size.

        Returns:
            dict: Enriched lead data.
        """
        enriched = lead_data.copy()

        # Simulate industry enrichment from email domain
        email = lead_data.get("email", "")
        if "finance" in email:
            enriched["industry"] = "Finance"
        elif "tech" in email or "software" in email:
            enriched["industry"] = "Technology"
        elif "health" in email:
            enriched["industry"] = "Healthcare"
        else:
            enriched["industry"] = "General"

        # Employee size category
        size = lead_data.get("company_size", 0)
        if size >= 1000:
            enriched["employee_size"] = "Enterprise"
        elif size >= 250:
            enriched["employee_size"] = "Mid-Market"
        elif size >= 50:
            enriched["employee_size"] = "SMB"
        else:
            enriched["employee_size"] = "Small Business"

        return enriched

    def _calculate_field_weight(self, field_name: str, field_value) -> float:
        """
        Helper to assign a normalized weight (0.0-1.0) for a given field and value.

        Scoring logic:
            - company_size: 0 (none) to 1.0 (large)
            - title: 1.0 for C-level, 0.7 for Director/VP, 0.4 for Manager, 0.1 for others
            - email: 1.0 for business domain, 0.3 for free email (gmail, yahoo, etc.)
            - phone: 1.0 if present, 0.0 if missing
        """
        if field_name == "company_size":
            try:
                size = int(field_value)
                if size >= 1000:
                    return 1.0
                elif size >= 250:
                    return 0.7
                elif size >= 50:
                    return 0.4
                elif size > 0:
                    return 0.1
            except (TypeError, ValueError):
                return 0.0
            return 0.0

        elif field_name == "title":
            if not field_value:
                return 0.0
            title = str(field_value).lower()
            if any(senior in title for senior in ["chief", "ceo", "cfo", "coo", "cto", "cmo"]):
                return 1.0
            elif any(mid in title for mid in ["vp", "vice president", "director"]):
                return 0.7
            elif "manager" in title:
                return 0.4
            else:
                return 0.1

        elif field_name == "email":
            if not field_value or "@" not in field_value:
                return 0.0
            domain = field_value.split("@")[-1].lower()
            free_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
            if any(free in domain for free in free_domains):
                return 0.3
            else:
                return 1.0

        elif field_name == "phone":
            return 1.0 if field_value else 0.0

        return 0.0


def analyze_lead(payload: Dict) -> Dict:
    """
    Function to analyze a lead with the provided payload.
    
    Args:
        payload (Dict): The lead data to analyze.
        
    Returns:
        Dict: A dictionary containing the lead score and enriched data.
    """
    # Initialize the agent
    agent = LeadIntelligenceAgent()
    
    # Enrich the lead data
    enriched_data = agent.enrich_lead(payload)
    
    # Score the lead
    score = agent.score_lead(enriched_data)
    
    # Return the analysis results
    return {
        "score": score,
        "enriched_data": enriched_data
    }
