# Global Tour Planner

A smart and user-friendly travel itinerary generator that optimizes international trips based on user preferences, budget, and time constraints.

---

## Features

- **Interactive Interface**: Easy-to-use GUI for inputting travel preferences.
- **Optimized Route Planning**: Implements a Traveling Salesman Problem (TSP) solver for efficient routing.
- **Interest-Based Filtering**: Select destinations based on personal interests.
- **Day Distribution**: Dynamic allocation of days across destinations based on interest scores.
- **Budget Management**: Estimates travel costs and ensures adherence to user-defined budgets.

---

## Problem Statement

Planning international trips can be overwhelming due to constraints like time, budget, and interests. This project automates the process, reducing time and effort while maximizing travel experiences.

---

## Algorithm Details

- **Route Optimization**: Nearest Neighbor algorithm for solving TSP.
- **Day Allocation**: Proportional distribution of days based on user interests.
- **Efficiency**: Provides a practical balance between accuracy and speed, outperforming exhaustive algorithms like A* in terms of time complexity.

---

## Time Complexity Analysis

- **TSP Solver (Nearest Neighbor)**: O(n^2)
- **Day Distribution**: O(n)
- **Overall Complexity**: O(n^2), suitable for moderate dataset sizes.

---

## How to Run the Project

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/global-tour-planner.git
   cd global-tour-planner
