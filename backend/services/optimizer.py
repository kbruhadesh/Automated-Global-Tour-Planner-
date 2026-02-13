"""
Tour Optimizer Service

Core algorithm module containing:
- Haversine distance calculation (replaces broken Euclidean)
- Nearest Neighbor TSP solver + 2-opt local search improvement
- Interest-weighted day distribution

This is the heart of the original project's algorithm, now corrected and enhanced.
"""

from math import radians, sin, cos, sqrt, atan2
from typing import List, Dict, Set, Tuple
from backend.config import EARTH_RADIUS_KM, MIN_DAYS_PER_COUNTRY, TSP_2OPT_MAX_ITERATIONS


class TourOptimizer:
    """
    Optimizes tour routes and day distribution.
    
    Improvements over original:
    - Haversine distance instead of Euclidean (critical fix)
    - 2-opt local search after Nearest Neighbor (5-15% better routes)
    - No mutation of input lists (bug fix)
    """

    def __init__(self, countries_data: Dict):
        self.countries_data = countries_data
        # Pre-compute distance matrix for efficiency
        self._distance_cache: Dict[Tuple[str, str], float] = {}

    # ─── Distance Calculation ─────────────────────────────────────

    def haversine_distance(self, coord1: List[float], coord2: List[float]) -> float:
        """
        Calculate the great-circle distance between two points on Earth
        using the Haversine formula.

        This replaces the original Euclidean distance which was mathematically
        incorrect for geographic coordinates (lat/lng are not Cartesian).

        Args:
            coord1: [latitude, longitude] of point 1
            coord2: [latitude, longitude] of point 2

        Returns:
            Distance in kilometers
        """
        lat1, lon1 = radians(coord1[0]), radians(coord1[1])
        lat2, lon2 = radians(coord2[0]), radians(coord2[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return EARTH_RADIUS_KM * c

    def get_distance(self, country_a: str, country_b: str) -> float:
        """Get distance between two countries, with caching."""
        key = (country_a, country_b)
        reverse_key = (country_b, country_a)

        if key in self._distance_cache:
            return self._distance_cache[key]
        if reverse_key in self._distance_cache:
            return self._distance_cache[reverse_key]

        dist = self.haversine_distance(
            self.countries_data[country_a]["coordinates"],
            self.countries_data[country_b]["coordinates"]
        )
        self._distance_cache[key] = dist
        return dist

    # ─── TSP Solver ───────────────────────────────────────────────

    def nearest_neighbor_tsp(self, countries: List[str], home: str) -> List[str]:
        """
        Nearest Neighbor heuristic for TSP.
        
        Builds a route by always visiting the closest unvisited country next.
        Time complexity: O(n²)
        
        NOTE: Unlike the original, this does NOT mutate the input list.
        """
        # Create a working copy — fixes the original mutation bug
        to_visit = [c for c in countries if c != home]

        if not to_visit:
            return [home, home]

        route = [home]
        current = home

        while to_visit:
            nearest = min(to_visit, key=lambda x: self.get_distance(current, x))
            route.append(nearest)
            to_visit.remove(nearest)
            current = nearest

        route.append(home)  # Return home
        return route

    def two_opt_improve(self, route: List[str]) -> List[str]:
        """
        2-opt local search improvement for TSP routes.
        
        Iteratively reverses segments of the route to find shorter paths.
        Typically improves Nearest Neighbor solutions by 5-15%.
        
        The first and last elements (home country) are fixed.
        """
        if len(route) <= 4:  # Need at least 2 intermediate stops to swap
            return route

        best_route = route[:]
        best_distance = self._route_total_distance(best_route)
        improved = True
        iterations = 0

        while improved and iterations < TSP_2OPT_MAX_ITERATIONS:
            improved = False
            iterations += 1

            # Only swap intermediate nodes (keep home country fixed at start/end)
            for i in range(1, len(best_route) - 2):
                for j in range(i + 1, len(best_route) - 1):
                    new_route = best_route[:i] + best_route[i:j + 1][::-1] + best_route[j + 1:]
                    new_distance = self._route_total_distance(new_route)

                    if new_distance < best_distance:
                        best_route = new_route
                        best_distance = new_distance
                        improved = True

        return best_route

    def solve_tsp(self, countries: List[str], home: str) -> List[str]:
        """
        Full TSP solver: Nearest Neighbor + 2-opt improvement.
        
        Args:
            countries: List of countries to visit (will NOT be mutated)
            home: Starting/ending country
            
        Returns:
            Optimized route [home, country1, country2, ..., home]
        """
        initial_route = self.nearest_neighbor_tsp(countries, home)
        optimized_route = self.two_opt_improve(initial_route)
        return optimized_route

    def _route_total_distance(self, route: List[str]) -> float:
        """Calculate total distance of a route."""
        total = 0.0
        for i in range(len(route) - 1):
            total += self.get_distance(route[i], route[i + 1])
        return total

    def get_route_total_distance(self, route: List[str]) -> float:
        """Public method — total route distance in km."""
        return self._route_total_distance(route)

    # ─── Day Distribution ─────────────────────────────────────────

    def distribute_days(
        self,
        total_days: int,
        route: List[str],
        selected_interests: Set[str]
    ) -> Dict[str, int]:
        """
        Distribute travel days across countries based on interest overlap.
        
        Countries matching more user interests get proportionally more days,
        with a minimum of MIN_DAYS_PER_COUNTRY days per stop.
        
        Algorithm preserved from original — it's a solid heuristic.
        """
        countries = route[1:-1]  # Exclude home at start/end

        if not countries:
            return {}

        # Calculate interest scores
        interest_scores = {
            country: len(set(self.countries_data[country]["interests"]) & selected_interests)
            for country in countries
        }

        total_score = sum(interest_scores.values())
        days_per_country: Dict[str, int] = {}

        if total_score == 0:
            # No interest overlap — distribute equally
            base_days = total_days // len(countries)
            days_per_country = {country: max(base_days, MIN_DAYS_PER_COUNTRY) for country in countries}
        else:
            # Assign minimum days first
            remaining_days = total_days
            for country in countries:
                days_per_country[country] = MIN_DAYS_PER_COUNTRY
                remaining_days -= MIN_DAYS_PER_COUNTRY

            # Distribute remaining days proportionally to interest scores
            for country in countries:
                if total_score > 0 and remaining_days > 0:
                    additional = int((remaining_days * interest_scores[country]) / total_score)
                    days_per_country[country] += additional

            # Distribute any leftover days to highest-interest countries
            distributed = sum(days_per_country.values())
            leftover = total_days - distributed

            sorted_countries = sorted(
                countries,
                key=lambda x: (interest_scores[x], -days_per_country[x]),
                reverse=True
            )

            for country in sorted_countries:
                if leftover > 0:
                    days_per_country[country] += 1
                    leftover -= 1
                else:
                    break

        return days_per_country

    def calculate_interest_score(self, country: str, interests: Set[str]) -> int:
        """Score a country by how many user interests it matches."""
        country_interests = set(self.countries_data[country]["interests"])
        return len(country_interests & interests)
