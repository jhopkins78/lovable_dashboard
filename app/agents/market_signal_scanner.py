"""
market_signal_scanner.py
------------------------
Defines the MarketSignalScanner class for analyzing market signals in leads.

- scan_lead: Adds a market_signal field to the lead dictionary based on keyword matches in simulated news headlines.
- fetch_news_headlines: Returns a static list of example news headlines.
"""

from typing import Dict, List

class MarketSignalScanner:
    """
    Scans a lead for market signals using keyword matching in simulated news headlines.
    """

    def __init__(self):
        # Example keywords for signal detection
        self.keywords = [
            "AI", "M&A", "layoffs", "expansion", "partnership", "fundraising"
        ]

    def fetch_news_headlines(self) -> List[str]:
        """
        Returns a static list of simulated news headlines.
        In a real implementation, this would fetch from a news API.
        """
        return [
            "Tech company raises $50 million in Series B funding.",
            "Major layoffs expected in retail sector.",
            "New AI breakthrough could disrupt healthcare industry.",
            "Global expansion plans announced by leading software firm.",
            "Strategic partnership formed between two fintech startups.",
            "Healthcare company completes M&A deal.",
            "Retailer launches new product line.",
            "Startup secures major fundraising round.",
            "No significant market changes reported this week.",
            "Company invests in AI-driven analytics."
        ]

    def scan_lead(self, lead: Dict) -> Dict:
        """
        Scans news headlines for keywords and updates the lead with a market signal.
        If a keyword is found in any headline, sets market_signal to the matched headline.
        Otherwise, sets market_signal to 'No significant signals detected.'

        Args:
            lead (dict): The lead dictionary.

        Returns:
            dict: The updated lead dictionary.
        """
        lead = lead.copy()
        headlines = self.fetch_news_headlines()
        found_signal = False

        # Check each headline for any keyword match
        for headline in headlines:
            for keyword in self.keywords:
                if keyword.lower() in headline.lower():
                    lead["market_signal"] = headline
                    found_signal = True
                    break
            if found_signal:
                break

        if not found_signal:
            lead["market_signal"] = "No significant signals detected."

        # The /scan_market_signals endpoint will add market_signal_detected field
        return lead
