"""
FastAPI application entry point for KBE action execution system.

This application provides REST APIs for:
- Executing building automation actions
- Validating action parameters
- Managing building/zone state
- Accessing action audit trail
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from src.api import actions_router, building_router, audit_router
from src.services import StateManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting KBE Action Execution API")

    # Import here to avoid circular imports
    from src.api.building import get_state_manager

    # Initialize services and demo zones
    state_manager = get_state_manager()

    # Initialize demo building zones (matching the web UI)
    demo_zones = [
        ("Z001", {
            "temperature_setpoint": 72.0,
            "current_temperature": 72.5,
            "hvac_mode": "auto",
            "occupancy_mode": "occupied",
            "power_usage": 15.2
        }),
        ("Z002", {
            "temperature_setpoint": 72.0,
            "current_temperature": 71.8,
            "hvac_mode": "auto",
            "occupancy_mode": "occupied",
            "power_usage": 8.5
        }),
        ("Z003", {
            "temperature_setpoint": 73.0,
            "current_temperature": 73.2,
            "hvac_mode": "auto",
            "occupancy_mode": "occupied",
            "power_usage": 6.8
        }),
        ("Z004", {
            "temperature_setpoint": 68.0,
            "current_temperature": 68.5,
            "hvac_mode": "auto",
            "occupancy_mode": "unoccupied",
            "power_usage": 22.1
        }),
        ("Z005", {
            "temperature_setpoint": 74.0,
            "current_temperature": 74.0,
            "hvac_mode": "auto",
            "occupancy_mode": "occupied",
            "power_usage": 4.2
        }),
    ]

    for zone_id, initial_state in demo_zones:
        await state_manager.initialize_zone(zone_id, initial_state)

    logger.info(f"Initialized {len(demo_zones)} demo zones: Z001-Z005")

    yield

    # Shutdown
    logger.info("Shutting down KBE Action Execution API")


# Create FastAPI application
app = FastAPI(
    title="KBE Action Execution API",
    description=(
        "REST API for Knowledge-Based Engineering (KBE) building automation. "
        "Provides endpoints for executing validated actions, managing building state, "
        "and accessing audit trails."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc)
        }
    )


# Health check endpoint
@app.get(
    "/health",
    tags=["system"],
    summary="Health check",
    description="Check if the API is running"
)
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "service": "KBE Action Execution API",
        "version": "0.1.0"
    }


# Serve static files for demo UI
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Root endpoint serves demo UI
    @app.get(
        "/",
        tags=["system"],
        summary="Demo Portal",
        description="KBE Demo Portal web interface"
    )
    async def root():
        """Serve the demo web UI."""
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        # Fallback to API info if UI not available
        return {
            "name": "KBE Action Execution API",
            "version": "0.1.0",
            "description": "Knowledge-Based Engineering building automation API",
            "endpoints": {
                "docs": "/docs",
                "redoc": "/redoc",
                "health": "/health",
                "actions": "/actions",
                "building": "/building",
                "audit": "/audit"
            }
        }
else:
    # Root endpoint with API information if no static files
    @app.get(
        "/",
        tags=["system"],
        summary="API information",
        description="Get basic API information and available endpoints"
    )
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "KBE Action Execution API",
            "version": "0.1.0",
            "description": "Knowledge-Based Engineering building automation API",
            "endpoints": {
                "docs": "/docs",
                "redoc": "/redoc",
                "health": "/health",
                "actions": "/actions",
                "building": "/building",
                "audit": "/audit"
            }
        }


# Include routers
app.include_router(actions_router)
app.include_router(building_router)
app.include_router(audit_router)


# Development server runner
if __name__ == "__main__":
    import uvicorn

    logger.info("Starting development server...")
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8008,
        reload=True,
        log_level="info"
    )
