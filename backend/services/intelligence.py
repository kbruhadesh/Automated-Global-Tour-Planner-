"""
Intelligence Service — Season Awareness, Currency Conversion, Smart Recommendations

Phase 3 module providing rich contextual intelligence for each trip stop.
"""

import math
from datetime import date
from typing import Dict, List, Optional, Tuple, Set


# ─── Month Name Mapping ──────────────────────────────────────────

MONTH_NAMES = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}


# ─── USD Exchange Rates (embedded snapshot — no external API needed) ──

EXCHANGE_RATES = {
    "USD": 1.0, "EUR": 0.92, "GBP": 0.79, "JPY": 149.50,
    "INR": 83.10, "AUD": 1.53, "CAD": 1.36, "CHF": 0.88,
    "CNY": 7.24, "SGD": 1.34, "MYR": 4.72, "THB": 35.50,
    "IDR": 15650.0, "VND": 24500.0, "KRW": 1320.0, "TWD": 31.50,
    "PHP": 56.20, "LKR": 320.0, "NPR": 133.0, "BDT": 110.0,
    "MVR": 15.40, "AED": 3.67, "SAR": 3.75, "OMR": 0.385,
    "QAR": 3.64, "BHD": 0.376, "KWD": 0.308, "JOD": 0.709,
    "ILS": 3.65, "TRY": 30.50, "EGP": 30.90, "MAD": 10.10,
    "ZAR": 18.80, "KES": 153.0, "TZS": 2520.0, "NGN": 1200.0,
    "GHS": 12.50, "ETB": 56.50, "BRL": 4.97, "MXN": 17.15,
    "ARS": 830.0, "COP": 3950.0, "PEN": 3.72, "CLP": 880.0,
    "CRC": 525.0, "DOP": 57.0, "GTQ": 7.80,
    "ISK": 138.0, "NOK": 10.55, "SEK": 10.45, "DKK": 6.88,
    "PLN": 4.05, "CZK": 22.80, "HUF": 355.0, "RON": 4.58,
    "HRK": 6.93, "BGN": 1.80, "RSD": 107.0,
    "RUB": 92.0, "UAH": 37.50, "GEL": 2.65,
    "KHR": 4100.0, "LAK": 20800.0, "MMK": 2100.0, "BTN": 83.10,
    "MNT": 3450.0, "KZT": 450.0, "UZS": 12300.0,
    "FJD": 2.24, "NZD": 1.63, "PGK": 3.75, "XPF": 110.0,
    "JMD": 155.0, "TTD": 6.78, "BBD": 2.0, "BSD": 1.0,
    "CUP": 24.0, "HTG": 133.0, "XCD": 2.70,
    "AOA": 830.0, "XOF": 605.0, "XAF": 605.0, "MGA": 4500.0,
    "MUR": 45.0, "SCR": 13.50, "BWP": 13.60, "NAD": 18.80,
    "MZN": 63.50, "ZMW": 25.80, "UGX": 3780.0, "RWF": 1250.0,
    "SZL": 18.80, "LRD": 188.0, "SLL": 20000.0,
    "MWK": 1680.0, "GMD": 66.0, "CVE": 101.0,
    "TMT": 3.50,
}


class IntelligenceService:
    """Provides season awareness, currency conversion, and smart recommendations."""

    def __init__(self, countries_data: Dict):
        self.countries_data = countries_data

    # ─── Season Awareness ─────────────────────────────────────────

    def parse_season_months(self, season_str: str) -> List[int]:
        """
        Parse a season string like 'March - May, September - November'
        into a list of month numbers [3, 4, 5, 9, 10, 11].
        """
        if not season_str:
            return list(range(1, 13))  # All months if no data

        months = []
        # Split by comma for multiple ranges
        ranges = [r.strip() for r in season_str.split(",")]

        for rng in ranges:
            parts = [p.strip().lower() for p in rng.split("-")]
            if len(parts) == 2:
                start_month = MONTH_NAMES.get(parts[0])
                end_month = MONTH_NAMES.get(parts[1])
                if start_month and end_month:
                    if start_month <= end_month:
                        months.extend(range(start_month, end_month + 1))
                    else:
                        # Wrap around (e.g., November - March)
                        months.extend(range(start_month, 13))
                        months.extend(range(1, end_month + 1))
            elif len(parts) == 1:
                m = MONTH_NAMES.get(parts[0])
                if m:
                    months.append(m)

        return sorted(set(months)) if months else list(range(1, 13))

    def check_season(
        self, country: str, start_date: date, end_date: date
    ) -> Dict:
        """
        Check if a country visit falls within its best travel season.

        Returns:
            {
                "is_best_season": bool,
                "season_rating": "ideal" | "partial" | "off-season",
                "best_months": str,
                "travel_months": [int],
                "warning": Optional[str],
                "tip": Optional[str],
            }
        """
        data = self.countries_data.get(country, {})
        best_season = data.get("best_season", "")

        if not best_season:
            return {
                "is_best_season": True,
                "season_rating": "ideal",
                "best_months": "Year-round",
                "travel_months": [],
                "warning": None,
                "tip": None,
            }

        best_months = self.parse_season_months(best_season)
        travel_months = set()

        current = start_date
        while current <= end_date:
            travel_months.add(current.month)
            current = current.replace(day=28) if current.month == 2 else current
            # Advance safely
            if current.month == 12:
                try:
                    current = current.replace(year=current.year + 1, month=1, day=1)
                except ValueError:
                    break
            else:
                try:
                    current = current.replace(month=current.month + 1, day=1)
                except ValueError:
                    break

        overlap = travel_months.intersection(set(best_months))
        overlap_ratio = len(overlap) / len(travel_months) if travel_months else 1.0

        if overlap_ratio >= 0.8:
            rating = "ideal"
            warning = None
            tip = f"Great timing! {country} is at its best during your visit."
        elif overlap_ratio >= 0.4:
            rating = "partial"
            warning = f"{country}: Your dates partially overlap with the best season ({best_season})"
            tip = f"Consider adjusting dates for optimal weather in {country}."
        else:
            rating = "off-season"
            warning = f"{country}: You're visiting during off-season. Best time is {best_season}"
            tip = f"Expect possible weather challenges. Benefits: fewer crowds and lower prices."

        return {
            "is_best_season": rating == "ideal",
            "season_rating": rating,
            "best_months": best_season,
            "travel_months": sorted(travel_months),
            "warning": warning,
            "tip": tip,
        }

    # ─── Currency Conversion ──────────────────────────────────────

    def get_currency_info(self, country: str, budget_usd: float) -> Dict:
        """
        Get currency conversion details for a country.

        Returns:
            {
                "currency_code": str,
                "exchange_rate": float,
                "budget_local": float,
                "daily_budget_local": float,
                "symbol": str,
            }
        """
        data = self.countries_data.get(country, {})
        currency = data.get("currency", "USD")
        rate = EXCHANGE_RATES.get(currency, 1.0)

        return {
            "currency_code": currency,
            "exchange_rate": round(rate, 2),
            "budget_local": round(budget_usd * rate, 0),
            "formatted": f"{budget_usd * rate:,.0f} {currency}",
        }

    def get_spending_guide(self, country: str, days: int) -> Dict:
        """
        Generate a spending guide for a country stop.

        Returns daily budget breakdown in local currency.
        """
        data = self.countries_data.get(country, {})
        currency = data.get("currency", "USD")
        rate = EXCHANGE_RATES.get(currency, 1.0)
        accom_per_day = data.get("avg_accommodation_cost", 100)

        # Estimated daily spending in USD
        meal_budget_usd = accom_per_day * 0.4  # rough estimate: 40% of accommodation
        transport_usd = accom_per_day * 0.2
        activities_usd = accom_per_day * 0.3

        return {
            "currency_code": currency,
            "daily_accommodation_local": round(accom_per_day * rate, 0),
            "daily_meals_local": round(meal_budget_usd * rate, 0),
            "daily_transport_local": round(transport_usd * rate, 0),
            "daily_activities_local": round(activities_usd * rate, 0),
            "daily_total_local": round((accom_per_day + meal_budget_usd + transport_usd + activities_usd) * rate, 0),
            "total_local": round((accom_per_day + meal_budget_usd + transport_usd + activities_usd) * rate * days, 0),
        }

    # ─── Smart Recommendations ────────────────────────────────────

    def generate_recommendations(
        self, country: str, interests: Set[str], days: int, start_date: date
    ) -> Dict:
        """
        Generate smart recommendations for a country based on
        the traveler's interests, duration, and travel dates.
        """
        data = self.countries_data.get(country, {})
        country_interests = set(data.get("interests", []))
        top_cities = data.get("top_cities", [])
        matching_interests = interests.intersection(country_interests)

        # Activity suggestions based on interests
        activities = self._suggest_activities(country, matching_interests, days)

        # City recommendations
        cities = self._suggest_cities(top_cities, days)

        # Packing tips based on season
        packing = self._suggest_packing(country, start_date)

        return {
            "suggested_activities": activities,
            "recommended_cities": cities,
            "packing_tips": packing,
            "matching_interests": sorted(matching_interests),
            "interest_match_pct": round(
                len(matching_interests) / max(len(interests), 1) * 100
            ),
        }

    def _suggest_activities(
        self, country: str, matching: Set[str], days: int
    ) -> List[Dict]:
        """Generate activity suggestions based on interests."""
        ACTIVITY_MAP = {
            "culture": [
                {"name": "Visit local museums & galleries", "duration": "Half day", "priority": "high"},
                {"name": "Attend a traditional performance", "duration": "Evening", "priority": "medium"},
                {"name": "Join a cultural walking tour", "duration": "3-4 hours", "priority": "high"},
            ],
            "food": [
                {"name": "Take a cooking class", "duration": "Half day", "priority": "high"},
                {"name": "Street food tour", "duration": "3-4 hours", "priority": "high"},
                {"name": "Fine dining experience", "duration": "Evening", "priority": "medium"},
            ],
            "beaches": [
                {"name": "Beach hopping day", "duration": "Full day", "priority": "high"},
                {"name": "Sunset beach walk", "duration": "2 hours", "priority": "medium"},
                {"name": "Water sports / snorkeling", "duration": "Half day", "priority": "high"},
            ],
            "nature": [
                {"name": "Guided nature hike", "duration": "Full day", "priority": "high"},
                {"name": "National park visit", "duration": "Full day", "priority": "high"},
                {"name": "Sunrise/sunset viewpoint", "duration": "2 hours", "priority": "medium"},
            ],
            "adventure": [
                {"name": "Adventure sports experience", "duration": "Half day", "priority": "high"},
                {"name": "Zip-lining or paragliding", "duration": "3-4 hours", "priority": "medium"},
                {"name": "Multi-day trekking", "duration": "2-3 days", "priority": "low"},
            ],
            "temples": [
                {"name": "Temple complex tour", "duration": "Half day", "priority": "high"},
                {"name": "Sunrise temple visit", "duration": "3 hours", "priority": "high"},
                {"name": "Meditation / spiritual retreat", "duration": "Half day", "priority": "low"},
            ],
            "historical": [
                {"name": "Historical landmark tour", "duration": "Full day", "priority": "high"},
                {"name": "Archaeological site visit", "duration": "Half day", "priority": "high"},
                {"name": "History museum deep-dive", "duration": "3-4 hours", "priority": "medium"},
            ],
            "nightlife": [
                {"name": "Nightlife district exploration", "duration": "Evening", "priority": "high"},
                {"name": "Rooftop bar hopping", "duration": "Evening", "priority": "medium"},
                {"name": "Live music venue", "duration": "Evening", "priority": "medium"},
            ],
            "shopping": [
                {"name": "Local market exploration", "duration": "Half day", "priority": "high"},
                {"name": "Artisan & craft shopping", "duration": "3-4 hours", "priority": "medium"},
                {"name": "Shopping district tour", "duration": "Half day", "priority": "medium"},
            ],
            "luxury": [
                {"name": "Spa & wellness experience", "duration": "Half day", "priority": "high"},
                {"name": "Fine dining at top restaurant", "duration": "Evening", "priority": "high"},
                {"name": "Private guided tour", "duration": "Full day", "priority": "medium"},
            ],
            "wildlife": [
                {"name": "Wildlife safari / tour", "duration": "Full day", "priority": "high"},
                {"name": "Wildlife sanctuary visit", "duration": "Half day", "priority": "high"},
                {"name": "Bird watching excursion", "duration": "3-4 hours", "priority": "low"},
            ],
            "diving": [
                {"name": "Scuba diving excursion", "duration": "Full day", "priority": "high"},
                {"name": "Snorkeling trip", "duration": "Half day", "priority": "high"},
                {"name": "Glass-bottom boat tour", "duration": "3 hours", "priority": "low"},
            ],
            "technology": [
                {"name": "Tech district / hub visit", "duration": "Half day", "priority": "high"},
                {"name": "Innovation museum or expo", "duration": "3-4 hours", "priority": "medium"},
                {"name": "Smart city tour", "duration": "Half day", "priority": "low"},
            ],
            "art": [
                {"name": "Art gallery tour", "duration": "Half day", "priority": "high"},
                {"name": "Street art walking tour", "duration": "3 hours", "priority": "high"},
                {"name": "Art workshop / class", "duration": "3-4 hours", "priority": "medium"},
            ],
            "architecture": [
                {"name": "Architecture walking tour", "duration": "Half day", "priority": "high"},
                {"name": "Iconic building visits", "duration": "3-4 hours", "priority": "high"},
                {"name": "Modern vs. historic contrast tour", "duration": "Full day", "priority": "medium"},
            ],
            "islands": [
                {"name": "Island hopping day trip", "duration": "Full day", "priority": "high"},
                {"name": "Beach & lagoon exploration", "duration": "Full day", "priority": "high"},
                {"name": "Boat tour / sailing", "duration": "Half day", "priority": "medium"},
            ],
            "photography": [
                {"name": "Golden hour photo walk", "duration": "3 hours", "priority": "high"},
                {"name": "Scenic viewpoint tour", "duration": "Half day", "priority": "high"},
                {"name": "Night photography session", "duration": "Evening", "priority": "medium"},
            ],
            "music": [
                {"name": "Live local music performance", "duration": "Evening", "priority": "high"},
                {"name": "Music festival or event", "duration": "Full day", "priority": "high"},
                {"name": "Traditional instrument workshop", "duration": "3 hours", "priority": "medium"},
            ],
            "wellness": [
                {"name": "Spa & massage experience", "duration": "Half day", "priority": "high"},
                {"name": "Yoga or meditation class", "duration": "2 hours", "priority": "high"},
                {"name": "Hot springs visit", "duration": "Half day", "priority": "medium"},
            ],
            "hiking": [
                {"name": "Day hike to scenic trail", "duration": "Full day", "priority": "high"},
                {"name": "Guided mountain trek", "duration": "Full day", "priority": "high"},
                {"name": "Multi-day trekking route", "duration": "2-3 days", "priority": "low"},
            ],
            "festivals": [
                {"name": "Attend local festival or celebration", "duration": "Full day", "priority": "high"},
                {"name": "Cultural carnival experience", "duration": "Evening", "priority": "high"},
                {"name": "Night market festival", "duration": "Evening", "priority": "medium"},
            ],
            "sports": [
                {"name": "Watch a local sports event", "duration": "3-4 hours", "priority": "high"},
                {"name": "Adventure sports activity", "duration": "Half day", "priority": "high"},
                {"name": "Golf or tennis session", "duration": "3 hours", "priority": "medium"},
            ],
            "surfing": [
                {"name": "Surfing lesson or session", "duration": "Half day", "priority": "high"},
                {"name": "Beach & surf culture tour", "duration": "Full day", "priority": "medium"},
                {"name": "Stand-up paddleboarding", "duration": "2 hours", "priority": "medium"},
            ],
            "skiing": [
                {"name": "Ski resort day pass", "duration": "Full day", "priority": "high"},
                {"name": "Snowboarding session", "duration": "Half day", "priority": "high"},
                {"name": "Après-ski experience", "duration": "Evening", "priority": "medium"},
            ],
            "romance": [
                {"name": "Sunset dinner cruise", "duration": "Evening", "priority": "high"},
                {"name": "Couples spa experience", "duration": "Half day", "priority": "high"},
                {"name": "Scenic picnic outing", "duration": "3 hours", "priority": "medium"},
            ],
            "family": [
                {"name": "Family-friendly amusement park", "duration": "Full day", "priority": "high"},
                {"name": "Interactive museum visit", "duration": "Half day", "priority": "high"},
                {"name": "Wildlife park or zoo", "duration": "Half day", "priority": "medium"},
            ],
            "desert": [
                {"name": "Desert safari excursion", "duration": "Full day", "priority": "high"},
                {"name": "Camel ride & dune experience", "duration": "Half day", "priority": "high"},
                {"name": "Desert stargazing night", "duration": "Evening", "priority": "medium"},
            ],
            "mountains": [
                {"name": "Mountain viewpoint visit", "duration": "Half day", "priority": "high"},
                {"name": "Cable car or gondola ride", "duration": "3 hours", "priority": "high"},
                {"name": "Alpine lake hike", "duration": "Full day", "priority": "medium"},
            ],
            "safari": [
                {"name": "Game drive safari", "duration": "Full day", "priority": "high"},
                {"name": "Bush walk guided tour", "duration": "Half day", "priority": "high"},
                {"name": "Night safari experience", "duration": "Evening", "priority": "medium"},
            ],
            "spiritual": [
                {"name": "Visit sacred sites & shrines", "duration": "Half day", "priority": "high"},
                {"name": "Meditation retreat session", "duration": "Half day", "priority": "high"},
                {"name": "Pilgrimage trail walk", "duration": "Full day", "priority": "medium"},
            ],
            "cruise": [
                {"name": "River or harbor cruise", "duration": "Half day", "priority": "high"},
                {"name": "Sunset boat tour", "duration": "3 hours", "priority": "high"},
                {"name": "Catamaran day trip", "duration": "Full day", "priority": "medium"},
            ],
            "camping": [
                {"name": "Overnight camping experience", "duration": "Full day", "priority": "high"},
                {"name": "Glamping resort stay", "duration": "Full day", "priority": "medium"},
                {"name": "Campfire & stargazing night", "duration": "Evening", "priority": "medium"},
            ],
            "cycling": [
                {"name": "City cycling tour", "duration": "Half day", "priority": "high"},
                {"name": "Countryside bike ride", "duration": "Full day", "priority": "high"},
                {"name": "Mountain biking trail", "duration": "Half day", "priority": "medium"},
            ],
        }

        activities = []
        for interest in sorted(matching):
            if interest in ACTIVITY_MAP:
                for act in ACTIVITY_MAP[interest]:
                    # Only suggest multi-day activities if enough time
                    if "days" in act["duration"].lower() and days < 4:
                        continue
                    activities.append({**act, "interest": interest})

        # Limit to reasonable number based on days
        max_activities = min(days * 2, 12)
        # Sort by priority (high first)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        activities.sort(key=lambda a: priority_order.get(a["priority"], 1))

        return activities[:max_activities]

    def _suggest_cities(self, top_cities: List[str], days: int) -> List[Dict]:
        """Recommend cities based on available days."""
        if not top_cities:
            return []

        max_cities = min(days // 2, len(top_cities), 4)
        return [
            {"name": city, "suggested_days": max(1, days // max(max_cities, 1))}
            for city in top_cities[:max_cities]
        ]

    def _suggest_packing(self, country: str, travel_date: date) -> List[str]:
        """Suggest packing items based on destination and season."""
        data = self.countries_data.get(country, {})
        interests = set(data.get("interests", []))
        month = travel_date.month
        lat = data.get("coordinates", [0])[0]

        tips = ["Passport & travel documents", "Travel adapter for local outlets"]

        # Temperature-based
        is_northern = lat > 0
        is_winter = (month in [12, 1, 2]) if is_northern else (month in [6, 7, 8])
        is_summer = (month in [6, 7, 8]) if is_northern else (month in [12, 1, 2])
        is_tropical = abs(lat) < 23.5

        if is_tropical:
            tips.extend(["Light, breathable clothing", "Strong sunscreen (SPF 50+)", "Insect repellent"])
        elif is_winter:
            tips.extend(["Warm layers & jacket", "Thermal undergarments", "Waterproof boots"])
        elif is_summer:
            tips.extend(["Light summer clothing", "Sunscreen & sunglasses", "Hat for sun protection"])
        else:
            tips.extend(["Layered clothing for variable weather", "Light rain jacket"])

        # Interest-based
        if "beaches" in interests or "islands" in interests:
            tips.append("Swimwear & quick-dry towel")
        if "adventure" in interests or "nature" in interests:
            tips.append("Comfortable hiking shoes")
        if "temples" in interests:
            tips.append("Modest clothing for temple visits (cover shoulders/knees)")
        if "diving" in interests:
            tips.append("Reef-safe sunscreen")

        return tips[:8]  # Cap at 8 items


# ─── Visa Requirement Data ────────────────────────────────────────
# Simplified visa matrix: from_country -> to_country -> requirement

VISA_POLICIES = {
    # Common visa-free / visa-on-arrival for Indian passport holders
    "India": {
        "visa_free": [
            "Bhutan", "Nepal", "Maldives", "Indonesia", "Thailand",
            "Sri Lanka", "Malaysia", "Singapore", "Oman", "Jordan",
            "Cambodia", "Vietnam", "Philippines", "Kenya", "Tanzania",
        ],
        "visa_on_arrival": [
            "Thailand", "Indonesia", "Cambodia", "Maldives", "Sri Lanka",
            "Jordan", "Oman", "Tanzania", "Kenya", "Nepal",
        ],
        "e_visa": [
            "Turkey", "UAE", "Australia", "Vietnam", "Taiwan",
            "South Korea", "Japan", "New Zealand", "United Kingdom",
        ],
        "visa_required": [
            "USA", "Canada", "France", "Germany", "Italy", "Spain",
            "Portugal", "Switzerland", "Norway", "Iceland", "Czechia",
            "Croatia", "Greece", "United Kingdom",
        ],
    },
    # USA passport holders — mostly visa-free
    "USA": {
        "visa_free": [
            "Canada", "Mexico", "United Kingdom", "France", "Germany",
            "Italy", "Spain", "Portugal", "Switzerland", "Norway",
            "Iceland", "Czechia", "Croatia", "Greece", "Japan",
            "South Korea", "Taiwan", "Singapore", "Malaysia", "Thailand",
            "Indonesia", "Philippines", "Israel", "UAE", "Oman",
            "Jordan", "Turkey", "Morocco", "South Africa", "Brazil",
            "Argentina", "Colombia", "Peru", "Chile", "New Zealand",
            "Australia",
        ],
        "visa_on_arrival": [
            "Cambodia", "Nepal", "Maldives", "Sri Lanka", "Tanzania",
            "Kenya", "Vietnam",
        ],
        "e_visa": ["India", "Vietnam", "Australia", "Turkey"],
        "visa_required": ["China", "Bhutan", "Egypt"],
    },
    # Generic fallback for other citizens
    "_default": {
        "visa_free": [],
        "visa_on_arrival": [
            "Nepal", "Maldives", "Cambodia", "Indonesia",
        ],
        "e_visa": [],
        "visa_required": [],
    },
}


def get_visa_info(home_country: str, destination: str) -> Dict:
    """
    Get visa requirement for traveling from home_country to destination.

    Returns:
        {
            "requirement": "visa_free" | "visa_on_arrival" | "e_visa" | "visa_required" | "unknown",
            "label": str,
            "color": str,  # for UI display
            "note": str,
        }
    """
    policies = VISA_POLICIES.get(home_country, VISA_POLICIES["_default"])

    if home_country == destination:
        return {
            "requirement": "home",
            "label": "Home Country",
            "color": "blue",
            "note": "No visa needed — this is your home country.",
        }

    if destination in policies.get("visa_free", []):
        return {
            "requirement": "visa_free",
            "label": "Visa Free",
            "color": "green",
            "note": f"No visa required for {home_country} citizens visiting {destination}.",
        }

    if destination in policies.get("visa_on_arrival", []):
        return {
            "requirement": "visa_on_arrival",
            "label": "Visa on Arrival",
            "color": "green",
            "note": f"Visa available on arrival for {home_country} citizens. Bring passport photos and fee.",
        }

    if destination in policies.get("e_visa", []):
        return {
            "requirement": "e_visa",
            "label": "e-Visa",
            "color": "yellow",
            "note": f"Apply for e-Visa online before travel. Processing usually takes 3-7 business days.",
        }

    if destination in policies.get("visa_required", []):
        return {
            "requirement": "visa_required",
            "label": "Visa Required",
            "color": "red",
            "note": f"Embassy/consulate visa required. Apply well in advance (4-8 weeks recommended).",
        }

    return {
        "requirement": "unknown",
        "label": "Check Requirements",
        "color": "gray",
        "note": f"Please verify visa requirements for {home_country} → {destination} with your local embassy.",
    }
