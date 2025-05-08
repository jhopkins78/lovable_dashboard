"""
config.py
---------
Handles application configuration and environment variable loading.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file at project root
load_dotenv()

def get_env_variable(key: str, default=None):
    """
    Helper to get environment variables with an optional default.
    """
    return os.getenv(key, default)

# Example usage:
# DATABASE_URL = get_env_variable("DATABASE_URL")
