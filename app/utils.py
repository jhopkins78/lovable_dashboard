"""
utils.py
--------
Utility functions for the application.
"""

def format_response(data=None, message="", success=True):
    """
    Helper to format API responses in a consistent structure.
    """
    return {
        "success": success,
        "message": message,
        "data": data
    }

# Example usage:
# return format_response(data={"id": 1}, message="Lead created.")
