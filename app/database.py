"""
database.py
-----------
Provides mock database helper functions for testing before connecting to a real database.
"""

from typing import List, Dict

def get_all_leads() -> List[Dict]:
    """
    Returns a list of mock leads for testing.
    Each lead has: id, name, score, summary.
    """
    return [
        {
            "id": 1,
            "name": "Alice Johnson",
            "score": 87,
            "summary": "Alice is a senior decision-maker at a mid-sized tech company, showing strong opportunity potential."
        },
        {
            "id": 2,
            "name": "Bob Smith",
            "score": 72,
            "summary": "Bob manages operations at a growing finance firm. His role and company size indicate moderate opportunity."
        },
        {
            "id": 3,
            "name": "Carol Lee",
            "score": 95,
            "summary": "Carol is the CTO at a large healthcare enterprise, representing a high-value lead."
        }
    ]
