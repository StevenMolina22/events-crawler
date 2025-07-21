"""FastAPI application factory and main app instance.

This module creates and configures the main FastAPI application instance
with all necessary middleware, routers, and settings.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .router import api_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="Show Up API",
        description="Event crawler and data API for discovering and managing events",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware to allow cross-origin requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include the main API router
    app.include_router(api_router, prefix="/api/v1")
    
    # Root endpoint outside of API versioning
    @app.get("/")
    async def root() -> dict[str, str]:
        """Root endpoint providing basic service information."""
        return {
            "service": "Show Up API",
            "status": "running",
            "docs": "/docs"
        }
    
    return app


# Create the main application instance
app = create_app()
