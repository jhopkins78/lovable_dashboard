"""
main.py
--------
Entry point for the FastAPI application. Initializes the app and includes API routers.
"""

from app import config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers (to be implemented in the routes package)
from app.routes import auth_routes, lead_routes, insight_routes, utility_routes, connector_routes, webhook_routes
from app.routes import dataset_routes
from app.routes import auto_analysis_routes, strategy_routes, report_routes, forecast_routes

app = FastAPI(
    title="Lead Commander Backend",
    description="Backend API for Lead Commander platform.",
    version="0.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify Lovable + Vercel domain(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from the routes package
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(lead_routes.router, tags=["leads"])
app.include_router(insight_routes.router, tags=["insights"])
app.include_router(utility_routes.router, tags=["utility"])
app.include_router(connector_routes.router, tags=["connector"])
app.include_router(webhook_routes.router, tags=["webhook"])
app.include_router(dataset_routes.router, tags=["datasets"])
app.include_router(auto_analysis_routes.router, tags=["ml"])
app.include_router(strategy_routes.router, tags=["strategy"])
app.include_router(report_routes.router, tags=["reports"])
app.include_router(forecast_routes.router, tags=["forecast"])

# Root endpoint for health check (optional, /health is also available)
@app.get("/")
async def root():
    """
    Health check endpoint.
    """
    return {"status": "OK"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint for Render.
    """
    return {"status": "healthy"}
