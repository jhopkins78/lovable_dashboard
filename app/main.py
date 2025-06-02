"""
main.py
--------
Entry point for the FastAPI application. Initializes the app and includes API routers.
"""

from app import config
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

# Import routers (to be implemented in the routes package)
from app.routes import auth_routes, lead_routes, insight_routes, utility_routes, connector_routes, webhook_routes
from app.routes import dataset_routes
from app.routes import auto_analysis_routes, strategy_routes, report_routes, forecast_routes, analysis_routes

app = FastAPI(
    title="Lead Commander Backend",
    description="Backend API for Lead Commander platform.",
    version="0.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a main API router and include all sub-routers
api_router = APIRouter()
api_router.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
api_router.include_router(lead_routes.router, tags=["leads"])
api_router.include_router(insight_routes.router, tags=["insights"])
api_router.include_router(utility_routes.router, tags=["utility"])
api_router.include_router(connector_routes.router, tags=["connector"])
api_router.include_router(webhook_routes.router, tags=["webhook"])
api_router.include_router(dataset_routes.router, tags=["datasets"])
api_router.include_router(auto_analysis_routes.router, tags=["ml"])
api_router.include_router(strategy_routes.router, tags=["strategy"])
api_router.include_router(report_routes.router, tags=["reports"])
api_router.include_router(forecast_routes.router, tags=["forecast"])
api_router.include_router(analysis_routes.router, prefix="/analysis", tags=["analysis"])

# Mount the API router at /api
app.include_router(api_router, prefix="/api")

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
