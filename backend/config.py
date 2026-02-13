"""
Application configuration.
Central place for all settings and constants.
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
COUNTRIES_FILE = DATA_DIR / "countries.json"

# Algorithm defaults
MIN_DAYS_PER_COUNTRY = 2
MAX_COUNTRIES = 15
BUDGET_SAFETY_MARGIN = 0.9  # Reserve 10% of budget as safety buffer
TSP_2OPT_MAX_ITERATIONS = 100  # Max improvement iterations for 2-opt

# Earth radius in kilometers (for Haversine)
EARTH_RADIUS_KM = 6371.0

# API settings
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
