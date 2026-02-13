"""
Pydantic schemas for request/response validation.
Phase 3: Added intelligence fields (season, currency, visa, recommendations).
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Set, Optional, Dict
from datetime import date


# ─── Request Schemas ──────────────────────────────────────────────

class ItineraryRequest(BaseModel):
    """Request body for generating a travel itinerary."""

    home_country: str = Field(
        ...,
        description="User's home/starting country",
        examples=["India"]
    )
    num_countries: int = Field(
        ...,
        ge=1,
        le=15,
        description="Number of countries to visit (1-15)"
    )
    interests: List[str] = Field(
        ...,
        min_length=1,
        description="List of travel interests",
        examples=[["culture", "food", "beaches"]]
    )
    budget: float = Field(
        ...,
        gt=0,
        description="Total trip budget in USD"
    )
    start_date: date = Field(
        ...,
        description="Trip start date (YYYY-MM-DD)"
    )
    end_date: date = Field(
        ...,
        description="Trip end date (YYYY-MM-DD)"
    )

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, v, info):
        if "start_date" in info.data and v <= info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v

    @field_validator("home_country")
    @classmethod
    def normalize_country(cls, v):
        return v.strip()


# ─── Intelligence Sub-schemas ─────────────────────────────────────

class SeasonInfo(BaseModel):
    """Season awareness data for a stop."""
    is_best_season: bool = True
    season_rating: str = "ideal"  # "ideal" | "partial" | "off-season"
    best_months: str = ""
    warning: Optional[str] = None
    tip: Optional[str] = None


class CurrencyInfo(BaseModel):
    """Currency conversion data for a stop."""
    currency_code: str = "USD"
    exchange_rate: float = 1.0
    budget_local: float = 0.0
    formatted: str = ""


class SpendingGuide(BaseModel):
    """Daily spending breakdown in local currency."""
    currency_code: str = "USD"
    daily_accommodation_local: float = 0
    daily_meals_local: float = 0
    daily_transport_local: float = 0
    daily_activities_local: float = 0
    daily_total_local: float = 0
    total_local: float = 0


class VisaInfo(BaseModel):
    """Visa requirement for the traveler."""
    requirement: str = "unknown"
    label: str = "Check Requirements"
    color: str = "gray"
    note: str = ""


class ActivitySuggestion(BaseModel):
    """A suggested activity for a destination."""
    name: str
    duration: str
    priority: str = "medium"
    interest: str = ""


class CityRecommendation(BaseModel):
    """A recommended city to visit."""
    name: str
    suggested_days: int = 1


class Recommendations(BaseModel):
    """Smart recommendations for a destination."""
    suggested_activities: List[ActivitySuggestion] = []
    recommended_cities: List[CityRecommendation] = []
    packing_tips: List[str] = []
    matching_interests: List[str] = []
    interest_match_pct: int = 0


# ─── Response Schemas ─────────────────────────────────────────────

class CountryStop(BaseModel):
    """A single country stop in the itinerary — enriched with intelligence."""

    country: str
    flag: str = ""
    days: int
    start_date: str
    end_date: str
    travel_cost: float
    accommodation_cost: float
    total_cost: float
    interests: List[str]
    coordinates: List[float]
    best_season: Optional[str] = None
    safety_score: Optional[str] = None
    currency: Optional[str] = None
    top_cities: List[str] = []

    # Phase 3 intelligence
    season_info: Optional[SeasonInfo] = None
    currency_info: Optional[CurrencyInfo] = None
    spending_guide: Optional[SpendingGuide] = None
    visa_info: Optional[VisaInfo] = None
    recommendations: Optional[Recommendations] = None


class RouteInfo(BaseModel):
    """Route information for the complete trip."""

    route: List[str]
    route_display: str
    total_distance_km: float


class BudgetSummary(BaseModel):
    """Financial summary of the trip."""

    total_cost: float
    budget: float
    remaining: float
    utilization_percent: float
    average_daily_cost: float
    total_days: int
    cost_saving_tips: List[str] = []


class ItineraryResponse(BaseModel):
    """Complete itinerary response with Phase 3 intelligence."""

    success: bool = True
    stops: List[CountryStop]
    route_info: RouteInfo
    budget_summary: BudgetSummary
    warnings: List[str] = []
    season_alerts: List[str] = []
    visa_alerts: List[str] = []


class ErrorResponse(BaseModel):
    """Error response."""

    success: bool = False
    error: str
    suggestions: List[str] = []


class CountryInfo(BaseModel):
    """Public country information for the frontend."""

    name: str
    flag: str = ""
    interests: List[str]
    avg_travel_cost: float
    avg_accommodation_cost: float
    coordinates: List[float]
    best_season: Optional[str] = None
    safety_score: Optional[str] = None
    currency: Optional[str] = None
    top_cities: List[str] = []


class AvailableDataResponse(BaseModel):
    """Response for available countries and interests."""

    countries: List[CountryInfo]
    all_interests: List[str]
    total_countries: int = 0
