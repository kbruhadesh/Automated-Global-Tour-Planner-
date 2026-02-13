# 🌍 Automated Global Tour Planner — Upgrade Roadmap

---

## Current System Overview

| Aspect | Current State |
|---|---|
| **Architecture** | Monolithic single-file (`Main.py`, 502 lines) |
| **Frontend** | Tkinter desktop GUI — dated, non-responsive |
| **Backend** | No backend — logic embedded in GUI class |
| **Data Layer** | Static JSON file (`data.json`) with 25 countries |
| **Core Algorithm** | Nearest Neighbor TSP (O(n²)) + interest-weighted day distribution |
| **Dependencies** | `tkinter`, `numpy`, `tkcalendar`, `json` |
| **Deployment** | Local Python script only |

---

## Critical Bugs Identified

1. **Euclidean distance on geographic coordinates** — `np.sqrt((x1-x2)² + (y1-y2)²)` treats lat/lng as Cartesian. Japan → Australia calculates *shorter* than Japan → South Korea. Must use Haversine.
2. **List mutation in `solve_tsp()`** — `selected_countries.remove(home_country)` mutates the caller's list (line 32). Subtle side-effect bug.
3. **Budget enforcement pops wrong country** — `selected_countries.pop()` removes the *last* country (line 388), which may be the cheapest. Should remove worst cost-to-interest ratio.
4. **Hardcoded date format** — `'%m/%d/%y'` US format is fragile.
5. **No input validation** — JSON data trusted blindly, no schema validation.

---

## Target Project Structure

```
Automated-Global-Tour-Planner/
├── backend/
│   ├── app.py                    # FastAPI entry point
│   ├── config.py                 # Settings
│   ├── models/
│   │   └── schemas.py            # Pydantic models (Phase 3: intelligence schemas)
│   ├── services/
│   │   ├── optimizer.py          # TSP + 2-opt + day distribution
│   │   ├── budget.py             # Budget calculations
│   │   ├── country_selector.py   # Knapsack-based selection
│   │   └── intelligence.py       # Phase 3: Season, currency, visa, recommendations
│   ├── data/
│   │   └── countries.json        # 95 countries with rich data
│   └── routes/
│       └── itinerary.py          # API endpoints (intelligence-enriched)
├── frontend/                     # Vanilla HTML/CSS/JS
│   ├── index.html
│   ├── css/
│   │   └── styles.css            # 1500+ lines design system
│   ├── js/
│   │   ├── app.js                # Main logic, save/load trips
│   │   ├── map.js                # Leaflet.js with dark/light tile switching
│   │   └── ui.js                 # Timeline, charts, intelligence panels
│   └── assets/
├── Main.py                       # Legacy (kept for reference)
├── data.json                     # Legacy (kept for reference)
├── requirements.txt
├── changes.md
└── README.md
```

---

## 🔵 Phase 1: Core Fixes & Modularization

> **Goal:** Fix critical bugs, restructure the codebase, establish a clean backend  
> **Timeline:** Week 1  

| # | Task | Details | Priority |
|---|---|---|---|
| 1.1 | **Fix Haversine distance** | Replace broken Euclidean `np.sqrt((x1-x2)² + (y1-y2)²)` with proper geodesic Haversine formula. | 🔴 Critical |
| 1.2 | **Fix list mutation bug** | `solve_tsp()` mutates caller's list via `.remove()` — use a non-destructive copy. | 🔴 Critical |
| 1.3 | **Fix budget enforcement** | Remove country with worst cost-to-interest ratio instead of blindly popping last. | 🔴 Critical |
| 1.4 | **Modularize into clean structure** | Split 502-line monolith into focused modules: `models/`, `services/`, `routes/`. | 🔴 Critical |
| 1.5 | **Create FastAPI backend** | Expose `/api/generate-itinerary` POST endpoint with Pydantic validation. | 🔴 Critical |
| 1.6 | **Improve TSP with 2-opt** | After Nearest Neighbor initial route, run 2-opt local search for 5-15% distance improvement. | 🟡 High |
| 1.7 | **Knapsack country selection** | Replace greedy selection with 0/1 knapsack DP for optimal budget utilization. | 🟡 High |
| 1.8 | **Expand data model** | Add `best_season`, `visa_difficulty`, `safety_score`, `flag_emoji`, `currency`, `top_cities` to each country. | 🟢 Medium |

**Deliverable:** A working FastAPI backend with correct algorithms, clean architecture, and a rich API.

---

## 🟢 Phase 2: Modern Web Frontend

> **Goal:** Vanilla HTML + CSS + JavaScript — no React, no build tools  
> **Timeline:** Week 2  
> **Tech:** Pure HTML5 + Vanilla CSS + Vanilla JS + Leaflet.js (CDN) + Chart.js (CDN)

| # | Task | Details | Priority |
|---|---|---|---|
| 2.1 | **Design system in CSS** | CSS custom properties, Google Fonts (Inter/Outfit), dark mode with `prefers-color-scheme`, glassmorphism cards, gradients. | 🔴 Critical |
| 2.2 | **Input form** | Country selector, interest toggle chips, native `<input type="date">`, budget slider with live preview. Clean sidebar layout. | 🔴 Critical |
| 2.3 | **Interactive world map** | Leaflet.js via CDN. Country markers, animated route polylines, popups with details. | 🔴 Critical |
| 2.4 | **Itinerary timeline** | Vertical stepper/timeline with cards — flag emoji, dates, costs, interests, duration. Smooth reveal animations. | 🟡 High |
| 2.5 | **Budget dashboard** | Progress bar, donut/bar chart (Chart.js CDN or pure CSS), per-country cost breakdown. | 🟡 High |
| 2.6 | **Responsive layout** | CSS Grid/Flexbox. Sidebar collapses on mobile. Map full-width. | 🟡 High |
| 2.7 | **Micro-animations** | CSS transitions, card entrance animations, route drawing animation, loading skeletons. | 🟢 Medium |
| 2.8 | **Export** | PDF via `window.print()` with print CSS. Copy shareable link with query params. | 🟢 Medium |

**Deliverable:** A stunning, responsive single-page app connected to the FastAPI backend with an interactive map.

---

## 🟡 Phase 3: Intelligence & Rich Data

> **Goal:** Smart features that make this a genuinely useful travel tool  
> **Timeline:** Week 3-4  

| # | Task | Details | Status |
|---|---|---|---|
| 3.1 | **Expand to 95+ countries** | Global coverage across all continents — Europe, Africa, Americas, Asia, Oceania. Each with cities, seasonal data, currencies, safety. | ✅ Done |
| 3.2 | **Season/weather awareness** | Best travel months parsed from data, compared against trip dates. Ideal/Partial/Off-season rating with tips. | ✅ Done |
| 3.3 | **Currency conversion** | Embedded exchange rates for 80+ currencies. Budget shown in local currency with daily spending guides. | ✅ Done |
| 3.4 | **Visa info display** | Visa requirements by home country (visa-free, on-arrival, e-visa, embassy). Color-coded badges on cards. | ✅ Done |
| 3.5 | **Travel safety scores** | Safety ratings with visual indicator badges (green/blue/yellow/red) on timeline cards. | ✅ Done |
| 3.6 | **Smart activity recommendations** | Rule-based suggestions per interest/country — activities, durations, priorities. Packing tips per season. | ✅ Done |
| 3.7 | **City recommendations** | Top cities per country with recommended days. City chips displayed on cards. | ✅ Done |
| 3.8 | **Save & load itineraries** | LocalStorage persistence — save trip data and restore form state + results with one click. | ✅ Done |
| 3.9 | **Travel alerts panel** | Aggregated season warnings and visa requirements shown in a dedicated alerts panel. | ✅ Done |
| 3.10 | **Expandable detail cards** | Timeline cards have collapsible panels with spending guides, activity lists, packing tips, visa notes. | ✅ Done |

**Deliverable:** A feature-rich, intelligent travel planner with 95+ countries, season awareness, currency conversion, visa tracking, and smart recommendations.

---

## Algorithm Improvements Summary

| Component | Before | After |
|---|---|---|
| **Distance** | Euclidean (broken) | Haversine (geodesic) |
| **TSP** | Nearest Neighbor only | Nearest Neighbor + 2-opt local search |
| **Country Selection** | Greedy by interest | 0/1 Knapsack DP (optimal budget use) |
| **Budget Enforcement** | Pop last country | Remove worst cost/interest ratio |
| **Day Distribution** | Proportional (unchanged) | Proportional with min 2 days (preserved) |

---

## Progress Tracking

- [x] Phase 1: Core Fixes & Modularization ✅
- [x] Phase 2: Modern Web Frontend ✅
- [x] Phase 3: Intelligence & Rich Data ✅
