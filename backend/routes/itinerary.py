"""
Itinerary API Routes — Phase 3: Intelligence Enriched

REST endpoints for generating and querying travel itineraries
with season awareness, currency conversion, visa info, and recommendations.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta, date
from typing import Set

from backend.models.schemas import (
    ItineraryRequest,
    ItineraryResponse,
    ErrorResponse,
    CountryStop,
    RouteInfo,
    BudgetSummary,
    AvailableDataResponse,
    CountryInfo,
    SeasonInfo,
    CurrencyInfo,
    SpendingGuide,
    VisaInfo,
    Recommendations,
    ActivitySuggestion,
    CityRecommendation,
)
from backend.services.optimizer import TourOptimizer
from backend.services.country_selector import CountrySelector
from backend.services.budget import BudgetService
from backend.services.intelligence import IntelligenceService, get_visa_info
from backend.data import load_countries

router = APIRouter(prefix="/api", tags=["itinerary"])

# Load data and initialize services
countries_data = load_countries()
optimizer = TourOptimizer(countries_data)
selector = CountrySelector(countries_data)
budget_service = BudgetService(countries_data)
intelligence = IntelligenceService(countries_data)


@router.get("/countries", response_model=AvailableDataResponse)
async def get_available_countries():
    """Get all available countries and interests for the frontend."""
    all_interests = sorted(list(set(
        interest
        for data in countries_data.values()
        for interest in data["interests"]
    )))

    country_list = [
        CountryInfo(
            name=name,
            flag=data.get("flag", ""),
            interests=data["interests"],
            avg_travel_cost=data["avg_travel_cost"],
            avg_accommodation_cost=data["avg_accommodation_cost"],
            coordinates=data["coordinates"],
            best_season=data.get("best_season"),
            safety_score=data.get("safety_score"),
            currency=data.get("currency"),
            top_cities=data.get("top_cities", []),
        )
        for name, data in sorted(countries_data.items())
    ]

    return AvailableDataResponse(
        countries=country_list,
        all_interests=all_interests,
        total_countries=len(country_list),
    )


@router.post("/generate-itinerary", response_model=ItineraryResponse)
async def generate_itinerary(request: ItineraryRequest):
    """
    Generate an optimized travel itinerary with Phase 3 intelligence.

    This endpoint:
    1. Selects the best countries via knapsack optimization
    2. Optimizes the route with TSP (Nearest Neighbor + 2-opt)
    3. Distributes days based on interest overlap
    4. Enforces budget by removing worst-value countries if needed
    5. Enriches each stop with season, currency, visa, and recommendation data
    6. Returns a complete itinerary with all intelligence layers
    """
    # Validate home country exists
    if request.home_country not in countries_data:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown country: {request.home_country}. "
                   f"Available: {', '.join(sorted(countries_data.keys()))}"
        )

    interests: Set[str] = set(request.interests)
    total_days = (request.end_date - request.start_date).days + 1

    if total_days < request.num_countries * 2:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough days ({total_days}) for {request.num_countries} countries. "
                   f"Need at least {request.num_countries * 2} days (2 per country)."
        )

    # Step 1: Select countries (knapsack optimization)
    selected = selector.select_countries(
        interests=interests,
        num_countries=request.num_countries,
        home_country=request.home_country,
        budget=request.budget,
    )

    if not selected:
        return ItineraryResponse(
            success=False,
            stops=[],
            route_info=RouteInfo(route=[], route_display="No route", total_distance_km=0),
            budget_summary=BudgetSummary(
                total_cost=0,
                budget=request.budget,
                remaining=request.budget,
                utilization_percent=0,
                average_daily_cost=0,
                total_days=total_days,
                cost_saving_tips=["Increase your budget or select different interests"],
            ),
            warnings=["Budget too low for any matching countries"],
        )

    # Step 2: Optimize route (TSP + 2-opt)
    route = optimizer.solve_tsp(selected, request.home_country)

    # Step 3: Distribute days
    days_distribution = optimizer.distribute_days(total_days, route, interests)

    # Step 4: Enforce budget (removes worst-value countries if over budget)
    total_cost = budget_service.calculate_total_cost(route, days_distribution)
    warnings = []

    if total_cost > request.budget:
        selected, budget_warnings, days_distribution = budget_service.enforce_budget(
            countries=selected,
            home_country=request.home_country,
            budget=request.budget,
            interests=interests,
            optimizer=optimizer,
        )
        warnings.extend(budget_warnings)

        if not selected:
            return ItineraryResponse(
                success=False,
                stops=[],
                route_info=RouteInfo(route=[], route_display="No route", total_distance_km=0),
                budget_summary=BudgetSummary(
                    total_cost=0,
                    budget=request.budget,
                    remaining=request.budget,
                    utilization_percent=0,
                    average_daily_cost=0,
                    total_days=total_days,
                ),
                warnings=warnings,
            )

        # Re-route with the reduced set
        route = optimizer.solve_tsp(selected, request.home_country)
        days_distribution = optimizer.distribute_days(total_days, route, interests)

    # Step 5: Build enriched response
    stops = []
    season_alerts = []
    visa_alerts = []
    current_date = datetime.combine(request.start_date, datetime.min.time())

    for country in route[1:-1]:
        days = days_distribution.get(country, 2)
        end_date = current_date + timedelta(days=days - 1)
        country_info = countries_data[country]
        costs = budget_service.calculate_country_cost(country, days)

        # ── Intelligence enrichment ──
        stop_start = current_date.date()
        stop_end = end_date.date()

        # Season awareness
        season_data = intelligence.check_season(country, stop_start, stop_end)
        season_info = SeasonInfo(
            is_best_season=season_data["is_best_season"],
            season_rating=season_data["season_rating"],
            best_months=season_data["best_months"],
            warning=season_data["warning"],
            tip=season_data["tip"],
        )
        if season_data["warning"]:
            season_alerts.append(season_data["warning"])

        # Currency conversion
        per_stop_budget = costs["total"]
        currency_data = intelligence.get_currency_info(country, per_stop_budget)
        currency_info = CurrencyInfo(
            currency_code=currency_data["currency_code"],
            exchange_rate=currency_data["exchange_rate"],
            budget_local=currency_data["budget_local"],
            formatted=currency_data["formatted"],
        )

        # Spending guide
        spending_data = intelligence.get_spending_guide(country, days)
        spending_guide = SpendingGuide(**spending_data)

        # Visa info
        visa_data = get_visa_info(request.home_country, country)
        visa_info_obj = VisaInfo(**visa_data)
        if visa_data["requirement"] in ("visa_required", "e_visa"):
            visa_alerts.append(f"{country}: {visa_data['label']} — {visa_data['note']}")

        # Recommendations
        rec_data = intelligence.generate_recommendations(
            country, interests, days, stop_start
        )
        recommendations = Recommendations(
            suggested_activities=[ActivitySuggestion(**a) for a in rec_data["suggested_activities"]],
            recommended_cities=[CityRecommendation(**c) for c in rec_data["recommended_cities"]],
            packing_tips=rec_data["packing_tips"],
            matching_interests=rec_data["matching_interests"],
            interest_match_pct=rec_data["interest_match_pct"],
        )

        stops.append(CountryStop(
            country=country,
            flag=country_info.get("flag", ""),
            days=days,
            start_date=current_date.strftime("%B %d, %Y"),
            end_date=end_date.strftime("%B %d, %Y"),
            travel_cost=costs["travel_cost"],
            accommodation_cost=costs["accommodation_cost"],
            total_cost=costs["total"],
            interests=country_info["interests"],
            coordinates=country_info["coordinates"],
            best_season=country_info.get("best_season"),
            safety_score=country_info.get("safety_score"),
            currency=country_info.get("currency"),
            top_cities=country_info.get("top_cities", []),
            season_info=season_info,
            currency_info=currency_info,
            spending_guide=spending_guide,
            visa_info=visa_info_obj,
            recommendations=recommendations,
        ))

        current_date = end_date + timedelta(days=1)

    # Final cost recalculation
    final_cost = budget_service.calculate_total_cost(route, days_distribution)
    total_distance = optimizer.get_route_total_distance(route)
    summary = budget_service.generate_summary(final_cost, request.budget, total_days)

    return ItineraryResponse(
        success=True,
        stops=stops,
        route_info=RouteInfo(
            route=route,
            route_display=" → ".join(route),
            total_distance_km=round(total_distance, 1),
        ),
        budget_summary=BudgetSummary(**summary),
        warnings=warnings,
        season_alerts=season_alerts,
        visa_alerts=visa_alerts,
    )
