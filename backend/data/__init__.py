"""
Data loading module.
Loads and validates the country database.
"""

import json
from pathlib import Path
from typing import Dict

from backend.config import COUNTRIES_FILE


def load_countries(filepath: Path = None) -> Dict:
    """
    Load country data from JSON file.

    Args:
        filepath: Optional custom path. Defaults to config COUNTRIES_FILE.

    Returns:
        Dictionary of country data

    Raises:
        FileNotFoundError: If the data file doesn't exist
        ValueError: If the JSON is malformed or missing required fields
    """
    path = filepath or COUNTRIES_FILE

    if not path.exists():
        raise FileNotFoundError(
            f"Country data file not found at {path}. "
            f"Expected enriched countries.json in backend/data/"
        )

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Validate structure
    required_fields = {"interests", "avg_travel_cost", "avg_accommodation_cost", "coordinates"}

    for country, info in data.items():
        missing = required_fields - set(info.keys())
        if missing:
            raise ValueError(
                f"Country '{country}' is missing required fields: {missing}"
            )

        if not isinstance(info["coordinates"], list) or len(info["coordinates"]) != 2:
            raise ValueError(
                f"Country '{country}' has invalid coordinates: {info['coordinates']}"
            )

    return data
