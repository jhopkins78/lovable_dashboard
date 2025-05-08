"""
main.py
--------
Entry point for the FastAPI application. Initializes the app and includes API routers.
"""

from fastapi import FastAPI

# Import routers (to be implemented in the routes package)
from app.routes import auth_routes, lead_routes, insight_routes

app = FastAPI(
    title="Lead Commander Backend",
    description="Backend API for Lead Commander platform.",
    version="0.1.0"
)

# Include routers from the routes package
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(lead_routes.router, prefix="/leads", tags=["leads"])
app.include_router(insight_routes.router, prefix="/insights", tags=["insights"])

# Root endpoint for health check
@app.get("/")
async def root():
    """
    Health check endpoint.
    """
    return {"message": "Lead Commander Backend is running."}
