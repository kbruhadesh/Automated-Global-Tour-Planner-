# Automated Global Tour Planner

A full-stack travel itinerary generator that optimizes international trips using algorithmic route planning, budget-aware country selection, and intelligent travel recommendations. Built with a FastAPI backend and a vanilla HTML/CSS/JavaScript frontend featuring an interactive map.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Algorithms](#algorithms)
- [Intelligence Layer](#intelligence-layer)
- [API Reference](#api-reference)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Tech Stack](#tech-stack)
- [Legacy System](#legacy-system)

---

## Overview

Planning international trips across multiple countries involves balancing competing constraints: budget limits, travel time, personal interests, geographic distances, visa requirements, and seasonal weather patterns. This project automates that process.

Given a home country, a set of travel interests, a budget, and trip dates, the system:

1. Selects the best-fit countries using a 0/1 Knapsack optimization
2. Computes an efficient visiting order using a TSP solver (Nearest Neighbor + 2-opt)
3. Distributes travel days proportionally based on interest overlap
4. Enforces budget constraints by removing the worst cost-to-interest-ratio countries
5. Enriches each stop with season advisories, currency conversion, visa info, activity suggestions, city recommendations, and packing tips

---

## Features

### Core Planning
- **Optimized Route Planning** -- Solves the Traveling Salesman Problem with Nearest Neighbor heuristic followed by 2-opt local search for 5-15% route improvement
- **Knapsack Country Selection** -- Selects countries using 0/1 Knapsack dynamic programming to maximize interest coverage within the budget
- **Interest-Weighted Day Distribution** -- Allocates more days to countries that match more of the traveler's interests, with a minimum of 2 days per stop
- **Smart Budget Enforcement** -- When over budget, removes the country with the worst cost-to-interest ratio instead of blindly dropping the last one

### Travel Intelligence
- **Season Awareness** -- Evaluates travel dates against each country's best season and returns ideal/partial/off-season ratings with tips
- **Currency Conversion** -- Embedded exchange rates for 80+ currencies with daily spending breakdowns in local currency
- **Visa Requirements** -- Color-coded visa status (visa-free, on-arrival, e-visa, embassy required) for each destination
- **Safety Scores** -- Visual safety indicators (green/blue/yellow/red) per country
- **Activity Recommendations** -- Rule-based activity suggestions tailored to the traveler's interests and destination
- **City Recommendations** -- Top cities per country with suggested visit durations
- **Packing Tips** -- Season-appropriate packing suggestions per destination

### Frontend
- **Interactive World Map** -- Leaflet.js-powered map with country markers, animated route polylines, and detail popups
- **Dark and Light Mode** -- Theme toggle with matching map tiles (dark mode uses CartoDB dark tiles)
- **Itinerary Timeline** -- Vertical stepper layout with expandable detail cards for each stop
- **Budget Dashboard** -- Visual cost breakdown with progress bars and per-country spending
- **Save and Load Trips** -- LocalStorage-based trip persistence
- **Responsive Design** -- Sidebar collapses on mobile; map and timeline adapt to screen size
- **Micro-Animations** -- Smooth card entrance animations, route drawing, loading skeletons, and hover effects

### Data Coverage
- **95 countries** across all continents with coordinates, interests, costs, best seasons, currencies, safety scores, visa data, and top cities

---

## Architecture

The application follows a clean client-server architecture:

```
Browser (Frontend)                    Server (Backend)
---------------------                 -------------------------
index.html                            FastAPI (app.py)
css/styles.css          <-- HTTP -->   routes/itinerary.py
js/app.js, map.js, ui.js              services/
                                        optimizer.py
                                        country_selector.py
                                        budget.py
                                        intelligence.py
                                      models/schemas.py
                                      data/countries.json
```

- The **frontend** is a single-page application served as static files by FastAPI. It communicates with the backend via REST API calls.
- The **backend** is a modular FastAPI application with clear separation between routing, business logic (services), data validation (Pydantic schemas), and configuration.

---

## Project Structure

```
Automated-Global-Tour-Planner/
|
|-- backend/
|   |-- app.py                        # FastAPI entry point, CORS, static file serving
|   |-- config.py                     # Centralized settings and algorithm constants
|   |-- __init__.py
|   |-- models/
|   |   |-- schemas.py                # Pydantic request/response models
|   |   +-- __init__.py
|   |-- services/
|   |   |-- optimizer.py              # Haversine distance, TSP solver, 2-opt, day distribution
|   |   |-- country_selector.py       # 0/1 Knapsack DP for country selection
|   |   |-- budget.py                 # Cost calculation, budget enforcement, financial summary
|   |   |-- intelligence.py           # Season, currency, visa, recommendations, packing
|   |   +-- __init__.py
|   |-- routes/
|   |   |-- itinerary.py              # API endpoint handlers
|   |   +-- __init__.py
|   +-- data/
|       |-- countries.json            # 95 countries with full metadata
|       +-- __init__.py               # JSON data loader
|
|-- frontend/
|   |-- index.html                    # Single-page application
|   |-- css/
|   |   +-- styles.css                # Complete design system (dark/light themes, animations)
|   +-- js/
|       |-- app.js                    # Main application logic, API calls, save/load
|       |-- map.js                    # Leaflet.js map initialization and route rendering
|       +-- ui.js                     # Timeline, charts, intelligence panels, UI updates
|
|-- Main.py                           # Legacy monolithic Tkinter application (kept for reference)
|-- data.json                         # Legacy country data (25 countries, kept for reference)
|-- requirements.txt                  # Python dependencies
|-- changes.md                        # Detailed upgrade roadmap and changelog
+-- README.md
```

---

## Algorithms

### Route Optimization (TSP)

The route is computed in two stages:

1. **Nearest Neighbor Heuristic** -- Starting from the home country, always visit the nearest unvisited country. Produces an initial route in O(n^2) time.
2. **2-Opt Local Search** -- Iteratively reverses route segments to eliminate crossings. Runs up to 100 iterations (configurable) and typically improves the initial route by 5-15%.

### Distance Calculation (Haversine)

All distances between countries use the Haversine formula for great-circle distance on a sphere. This replaces the original Euclidean distance calculation, which treated latitude/longitude as Cartesian coordinates and produced incorrect results (e.g., Japan to Australia being shorter than Japan to South Korea).

### Country Selection (0/1 Knapsack)

Countries are selected using dynamic programming knapsack optimization. Each country has a "weight" (its minimum cost) and a "value" (interest overlap score). The algorithm finds the combination of countries that maximizes total interest coverage without exceeding the budget.

### Day Distribution

Travel days are distributed proportionally based on how many of the traveler's interests each country matches. Every stop receives a minimum of 2 days. Remaining days are allocated to the country with the highest interest score.

### Budget Enforcement

When the total itinerary cost exceeds the budget, the system iteratively removes the country with the worst cost-to-interest ratio (highest cost per interest match). This preserves high-value destinations, unlike the original system which simply dropped the last country in the list.

### Complexity

| Component | Time Complexity |
|---|---|
| Nearest Neighbor TSP | O(n^2) |
| 2-Opt Improvement | O(n^2) per iteration, up to 100 iterations |
| 0/1 Knapsack Selection | O(n * B) where B is discretized budget |
| Day Distribution | O(n) |
| Budget Enforcement | O(n^2) worst case (remove one country per iteration) |

---

## Intelligence Layer

The intelligence service (`intelligence.py`) enriches each itinerary stop with contextual data:

| Feature | Description |
|---|---|
| **Season Check** | Parses each country's best travel months and compares against the trip dates. Returns a rating (ideal, partial, off-season) with warnings and tips. |
| **Currency Info** | Converts the allocated budget for each stop into local currency using embedded exchange rates for 80+ currencies. Provides daily spending breakdowns. |
| **Visa Requirements** | Determines visa status based on home country and destination. Returns color-coded badges (green for visa-free, yellow for e-visa, red for embassy required). |
| **Activity Suggestions** | Generates interest-specific activity lists with durations and priorities. For example, a "culture" interest in Japan yields temple visits, tea ceremonies, and museum tours. |
| **City Recommendations** | Recommends top cities per country with suggested visit durations based on available days. |
| **Packing Tips** | Suggests items based on destination climate and travel season. |

---

## API Reference

### GET /api/countries

Returns all available countries, their metadata, and the list of valid interests.

**Response:**
```json
{
  "countries": [
    {
      "name": "Japan",
      "flag": "...",
      "interests": ["culture", "food", "technology"],
      "avg_travel_cost": 1200,
      "avg_accommodation_cost": 150,
      "coordinates": [36.2048, 138.2529],
      "best_season": "March - May, October - November",
      "safety_score": "very_safe",
      "currency": "JPY",
      "top_cities": ["Tokyo", "Kyoto", "Osaka"]
    }
  ],
  "all_interests": ["culture", "food", "beaches", "adventure", "..."],
  "total_countries": 95
}
```

### POST /api/generate-itinerary

Generates an optimized itinerary based on the provided parameters.

**Request Body:**
```json
{
  "home_country": "India",
  "num_countries": 5,
  "interests": ["culture", "food", "beaches"],
  "budget": 8000,
  "start_date": "2026-06-01",
  "end_date": "2026-06-21"
}
```

**Response:**
```json
{
  "success": true,
  "stops": [
    {
      "country": "Thailand",
      "flag": "...",
      "days": 4,
      "start_date": "2026-06-01",
      "end_date": "2026-06-05",
      "travel_cost": 400,
      "accommodation_cost": 200,
      "total_cost": 600,
      "interests": ["beaches", "food", "culture"],
      "coordinates": [15.87, 100.9925],
      "season_info": { "season_rating": "partial", "warning": "..." },
      "currency_info": { "currency_code": "THB", "exchange_rate": 35.5 },
      "visa_info": { "requirement": "visa_on_arrival", "label": "Visa on Arrival" },
      "recommendations": { "suggested_activities": [], "recommended_cities": [] }
    }
  ],
  "route_info": {
    "route": ["India", "Thailand", "...", "India"],
    "route_display": "India -> Thailand -> ... -> India",
    "total_distance_km": 12500.0
  },
  "budget_summary": {
    "total_cost": 6800,
    "budget": 8000,
    "remaining": 1200,
    "utilization_percent": 85.0,
    "average_daily_cost": 340,
    "total_days": 20
  },
  "season_alerts": [],
  "visa_alerts": []
}
```

### GET /health

Returns the API health status.

---

## Getting Started

### Prerequisites

- Python 3.11 or higher

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/kbruhadesh/Automated-Global-Tour-Planner-.git
   cd Automated-Global-Tour-Planner-
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the server:
   ```bash
   python -m backend.app
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn backend.app:app --reload
   ```

4. Open the application:
   Navigate to `http://127.0.0.1:8000` in your browser. The frontend is served automatically by FastAPI.

### API Documentation

FastAPI generates interactive API docs automatically:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## Configuration

All settings are centralized in `backend/config.py`:

| Setting | Default | Description |
|---|---|---|
| `MIN_DAYS_PER_COUNTRY` | 2 | Minimum days allocated per country stop |
| `MAX_COUNTRIES` | 15 | Maximum number of countries in a single trip |
| `BUDGET_SAFETY_MARGIN` | 0.9 | Reserve 10% of budget as a safety buffer |
| `TSP_2OPT_MAX_ITERATIONS` | 100 | Maximum improvement iterations for 2-opt |
| `EARTH_RADIUS_KM` | 6371.0 | Earth radius used in Haversine calculation |
| `API_HOST` | 127.0.0.1 | Server host (overridable via `API_HOST` env var) |
| `API_PORT` | 8000 | Server port (overridable via `API_PORT` env var) |
| `CORS_ORIGINS` | * | Allowed CORS origins (overridable via `CORS_ORIGINS` env var) |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | FastAPI |
| **Data Validation** | Pydantic v2 |
| **Server** | Uvicorn (ASGI) |
| **Frontend** | Vanilla HTML5, CSS3, JavaScript (ES6+) |
| **Map** | Leaflet.js (CDN) |
| **Styling** | Custom CSS with CSS custom properties, dark/light theme system |
| **Data Storage** | Static JSON (countries), LocalStorage (saved trips) |

---

## Legacy System

The original application (`Main.py`) was a monolithic 500-line Tkinter desktop GUI with embedded logic. It has been preserved for reference. Key issues that were resolved in the current version:

| Issue | Original Behavior | Current Fix |
|---|---|---|
| Distance calculation | Euclidean distance on lat/lng (incorrect) | Haversine geodesic distance |
| TSP solver | Nearest Neighbor only | Nearest Neighbor + 2-opt improvement |
| Country selection | Greedy by interest score | 0/1 Knapsack dynamic programming |
| Budget enforcement | Removes last country blindly | Removes worst cost-to-interest ratio |
| List mutation | `solve_tsp()` mutates caller's list | Non-destructive copy |
| Input validation | No validation | Pydantic schema validation |
| Architecture | Single file, GUI-coupled | Modular backend/frontend separation |
