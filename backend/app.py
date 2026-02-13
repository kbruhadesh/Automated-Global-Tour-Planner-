"""
FastAPI Application Entry Point

Run with:
    uvicorn backend.app:app --reload
    
Or:
    python -m backend.app
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.config import CORS_ORIGINS, API_HOST, API_PORT
from backend.routes.itinerary import router as itinerary_router

# ─── App Setup ────────────────────────────────────────────────────

app = FastAPI(
    title="🌍 Global Tour Planner API",
    description="Optimized travel itinerary generator with TSP routing, "
                "knapsack budget optimization, and interest-based country selection.",
    version="2.0.0",
)

# CORS — allow frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ───────────────────────────────────────────────────────

app.include_router(itinerary_router)

# Serve frontend static files (for Phase 2)
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}


# ─── Direct Run ───────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
    )
