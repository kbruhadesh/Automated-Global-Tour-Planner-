"""
Budget Service

Handles all cost calculations, budget enforcement, and financial summaries.

Improvement over original:
- Budget enforcement removes worst value country (not last country)
- Separated from GUI — can be used by API or any other consumer
- Clear cost breakdown structure
"""

from typing import List, Dict, Set, Tuple
from backend.config import MIN_DAYS_PER_COUNTRY


class BudgetService:
    """Handles all budget-related calculations."""

    def __init__(self, countries_data: Dict):
        self.countries_data = countries_data

    def calculate_country_cost(self, country: str, days: int) -> Dict[str, float]:
        """Calculate full cost for visiting a country."""
        data = self.countries_data[country]
        travel_cost = data["avg_travel_cost"]
        accommodation_cost = data["avg_accommodation_cost"] * days
        return {
            "travel_cost": travel_cost,
            "accommodation_cost": accommodation_cost,
            "total": travel_cost + accommodation_cost,
        }

    def calculate_total_cost(
        self,
        route: List[str],
        days_distribution: Dict[str, int]
    ) -> float:
        """
        Calculate total itinerary cost including return flight.

        Includes:
        - Travel cost to each country
        - Accommodation for allocated days
        - Return flight from last country back home
        """
        total = 0.0

        # Cost for each visited country
        for country in route[1:-1]:
            days = days_distribution.get(country, MIN_DAYS_PER_COUNTRY)
            costs = self.calculate_country_cost(country, days)
            total += costs["total"]

        # Return flight from last visited country
        if len(route) >= 2:
            last_visited = route[-2]
            total += self.countries_data[last_visited]["avg_travel_cost"]

        return total

    def enforce_budget(
        self,
        countries: List[str],
        home_country: str,
        budget: float,
        interests: Set[str],
        optimizer  # TourOptimizer instance
    ) -> Tuple[List[str], List[str], Dict[str, int]]:
        """
        Enforce budget by iteratively removing the worst-value country.

        CRITICAL FIX over original: The original did `selected_countries.pop()`
        which removes the LAST country — potentially the cheapest and most
        relevant one. This version removes the country with the worst
        cost-to-interest ratio, preserving the best value destinations.

        Args:
            countries: Selected countries
            home_country: Starting country
            budget: Total budget
            interests: User interests
            optimizer: TourOptimizer instance for routing

        Returns:
            (final_countries, warnings, days_distribution)
        """
        warnings = []
        working = countries[:]  # Don't mutate input

        while working:
            route = optimizer.solve_tsp(working, home_country)
            total_days = max(len(working) * MIN_DAYS_PER_COUNTRY, 1)
            days_dist = optimizer.distribute_days(total_days, route, interests)
            total_cost = self.calculate_total_cost(route, days_dist)

            if total_cost <= budget:
                return working, warnings, days_dist

            if len(working) <= 1:
                warnings.append(
                    f"Budget ${budget:,.0f} is insufficient even for 1 country. "
                    f"Minimum needed: ${total_cost:,.0f}"
                )
                return [], warnings, {}

            # Find the worst value country (highest cost per interest match)
            worst = self._find_worst_value(working, interests)
            removed_cost = self.calculate_country_cost(worst, MIN_DAYS_PER_COUNTRY)["total"]
            warnings.append(
                f"Removed {worst} (cost: ${removed_cost:,.0f}) to stay within budget"
            )
            working.remove(worst)

        return working, warnings, {}

    def _find_worst_value(self, countries: List[str], interests: Set[str]) -> str:
        """Find the country with the worst cost-to-interest ratio."""
        worst_country = countries[0]
        worst_ratio = 0.0

        for country in countries:
            data = self.countries_data[country]
            min_cost = data["avg_travel_cost"] + data["avg_accommodation_cost"] * MIN_DAYS_PER_COUNTRY
            interest_match = len(set(data["interests"]) & interests)

            # Higher ratio = worse value (more expensive per interest)
            ratio = min_cost / interest_match if interest_match > 0 else float("inf")

            if ratio > worst_ratio:
                worst_ratio = ratio
                worst_country = country

        return worst_country

    def generate_summary(
        self,
        total_cost: float,
        budget: float,
        total_days: int
    ) -> Dict:
        """Generate a financial summary with tips."""
        remaining = budget - total_cost
        utilization = (total_cost / budget) * 100 if budget > 0 else 0
        daily_avg = total_cost / total_days if total_days > 0 else 0

        tips = []
        if utilization >= 85:
            tips = [
                "Consider hostels or guesthouses in expensive destinations",
                "Look for flight deals or alternative travel dates",
                "Research free activities and attractions",
                "Consider local transportation options",
            ]
        elif remaining > 500:
            tips = [
                "You have room to extend stays at favorite destinations",
                "Consider upgrading accommodation at key stops",
                "Budget available for special experiences and excursions",
            ]

        return {
            "total_cost": round(total_cost, 2),
            "budget": budget,
            "remaining": round(remaining, 2),
            "utilization_percent": round(utilization, 1),
            "average_daily_cost": round(daily_avg, 2),
            "total_days": total_days,
            "cost_saving_tips": tips,
        }

    def calculate_minimum_trip_cost(
        self,
        countries: List[str],
        home_country: str
    ) -> float:
        """Calculate the absolute minimum cost for a set of countries."""
        total = 0.0
        for country in countries:
            data = self.countries_data[country]
            total += data["avg_travel_cost"]
            total += data["avg_accommodation_cost"] * MIN_DAYS_PER_COUNTRY

        # Return flight
        if countries:
            total += self.countries_data[countries[-1]]["avg_travel_cost"]

        return total
