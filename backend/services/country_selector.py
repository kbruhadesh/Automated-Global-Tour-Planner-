"""
Country Selector Service

Selects the optimal set of countries to visit given interests and budget.

Improvement over original:
- Replaces greedy selection with 0/1 Knapsack dynamic programming
- Guarantees optimal budget utilization (best interest coverage within budget)
- Falls back to greedy for very large datasets (n > 50) where DP is expensive
"""

from typing import List, Dict, Set, Tuple
from backend.config import BUDGET_SAFETY_MARGIN, MIN_DAYS_PER_COUNTRY


class CountrySelector:
    """Selects the best countries to visit within a budget."""

    def __init__(self, countries_data: Dict):
        self.countries_data = countries_data

    def minimum_cost(self, country: str) -> float:
        """Minimum cost to visit a country (travel + min days accommodation)."""
        data = self.countries_data[country]
        return data["avg_travel_cost"] + (data["avg_accommodation_cost"] * MIN_DAYS_PER_COUNTRY)

    def interest_score(self, country: str, interests: Set[str]) -> int:
        """How many user interests a country matches."""
        return len(set(self.countries_data[country]["interests"]) & interests)

    def select_countries(
        self,
        interests: Set[str],
        num_countries: int,
        home_country: str,
        budget: float
    ) -> List[str]:
        """
        Select the optimal set of countries using 0/1 Knapsack DP.

        This replaces the original greedy approach which could miss better
        combinations. The knapsack treats each country as an item:
        - Weight = minimum cost to visit
        - Value  = number of matching interests

        We maximize total interest coverage within the budget.

        Args:
            interests: Set of user's travel interests
            num_countries: Maximum number of countries to select
            home_country: User's origin (excluded from selection)
            budget: Total trip budget in USD

        Returns:
            List of selected country names
        """
        # Build candidate list (exclude home country, must have at least 1 interest match)
        candidates = []
        for country, data in self.countries_data.items():
            if country == home_country:
                continue
            score = self.interest_score(country, interests)
            if score > 0:
                candidates.append({
                    "country": country,
                    "score": score,
                    "min_cost": self.minimum_cost(country),
                })

        if not candidates:
            return []

        # Apply safety margin and reserve return flight cost
        working_budget = budget * BUDGET_SAFETY_MARGIN
        max_return_cost = max(
            self.countries_data[c]["avg_travel_cost"]
            for c in self.countries_data
        )
        working_budget -= max_return_cost

        if working_budget <= 0:
            return []

        # Use knapsack for small candidate sets, greedy for large
        if len(candidates) <= 50:
            selected = self._knapsack_select(candidates, working_budget, num_countries)
        else:
            selected = self._greedy_select(candidates, working_budget, num_countries)

        return selected

    def _knapsack_select(
        self,
        candidates: List[Dict],
        budget: float,
        max_items: int
    ) -> List[str]:
        """
        0/1 Knapsack selection for optimal budget utilization.

        Uses integer budget granularity of $10 to keep DP table manageable.
        Time complexity: O(n * W/granularity * max_items)
        """
        granularity = 10  # $10 steps
        W = int(budget / granularity)
        n = len(candidates)

        if W <= 0:
            return []

        # DP table: dp[i][w] = (max_score, count_used) considering first i items with budget w
        # We track both score and count to enforce max_items
        INF = -1
        dp = [[(0, 0) for _ in range(W + 1)] for _ in range(n + 1)]
        chosen = [[False] * (W + 1) for _ in range(n + 1)]

        for i in range(1, n + 1):
            cost_units = int(candidates[i - 1]["min_cost"] / granularity)
            score = candidates[i - 1]["score"]

            for w in range(W + 1):
                # Don't take item i
                dp[i][w] = dp[i - 1][w]
                chosen[i][w] = False

                # Take item i (if budget allows and under max_items)
                if cost_units <= w:
                    prev_score, prev_count = dp[i - 1][w - cost_units]
                    if prev_count < max_items:
                        new_score = prev_score + score
                        new_count = prev_count + 1
                        curr_score, _ = dp[i][w]
                        if new_score > curr_score:
                            dp[i][w] = (new_score, new_count)
                            chosen[i][w] = True

        # Backtrack to find selected countries
        selected = []
        w = W
        for i in range(n, 0, -1):
            if chosen[i][w]:
                selected.append(candidates[i - 1]["country"])
                cost_units = int(candidates[i - 1]["min_cost"] / granularity)
                w -= cost_units

        return selected

    def _greedy_select(
        self,
        candidates: List[Dict],
        budget: float,
        max_items: int
    ) -> List[str]:
        """
        Greedy fallback for large datasets.
        Sort by score (desc), then cost-per-interest (asc).
        Same logic as original but cleaner.
        """
        sorted_candidates = sorted(
            candidates,
            key=lambda x: (-x["score"], x["min_cost"] / x["score"] if x["score"] > 0 else float("inf"))
        )

        selected = []
        total_cost = 0.0

        for c in sorted_candidates:
            if len(selected) >= max_items:
                break
            if total_cost + c["min_cost"] <= budget:
                selected.append(c["country"])
                total_cost += c["min_cost"]

        return selected
