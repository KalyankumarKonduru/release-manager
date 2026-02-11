"""
FastAPI application factory and configuration.

This module initializes the FastAPI application with:
- Lifespan context manager for startup/shutdown
- CORS middleware configuration
- Exception handlers
- Health check endpoint
- API router registration
- OpenAPI documentation setup
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import db
from app.core.redis import redis_manager

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


async def _seed_demo_user() -> None:
    """Create demo user if it doesn't exist (runs on startup)."""
    from sqlalchemy import select
    from app.core.security import hash_password
    from app.models.user import User

    async with db.get_session() as session:
        result = await session.execute(
            select(User).where(User.email == "demo@example.com")
        )
        if result.scalar_one_or_none():
            return
        user = User(
            email="demo@example.com",
            username="demo",
            full_name="Demo User",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_admin=True,
        )
        session.add(user)
        await session.commit()
        logger.info("Demo user seeded: demo@example.com")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles startup and shutdown events for the FastAPI application.
    - Startup: Initialize database and Redis connections
    - Shutdown: Close all connections gracefully

    Args:
        app: FastAPI application instance

    Yields:
        Control back to FastAPI during application run
    """
    # Startup
    logger.info("Starting up application...")

    try:
        # Initialize database
        logger.info("Initializing database...")
        await db.initialize()
        await db.create_tables()
        logger.info("Database initialized successfully")

        # Seed demo user on first run
        await _seed_demo_user()

        # Initialize Redis
        logger.info("Initializing Redis...")
        await redis_manager.initialize()
        logger.info("Redis initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")

    try:
        # Close Redis
        logger.info("Closing Redis connection...")
        await redis_manager.close()

        # Close database
        logger.info("Closing database connection...")
        await db.close()

        logger.info("Application shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="DevOps Release Manager API",
        version="1.0.0",
        lifespan=lifespan,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        Health check endpoint.

        Returns:
            Health status of application and dependencies
        """
        redis_healthy = await redis_manager.health_check()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "service": settings.APP_NAME,
                "version": "1.0.0",
                "database": "connected",
                "redis": "connected" if redis_healthy else "disconnected",
            },
        )

    # Exception handlers
    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc):
        """Handle ValueError exceptions."""
        logger.error(f"ValueError: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(RuntimeError)
    async def runtime_error_handler(request, exc):
        """Handle RuntimeError exceptions."""
        logger.error(f"RuntimeError: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        """Handle general exceptions."""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """
        Root endpoint with API information.

        Returns:
            API metadata and documentation links
        """
        return {
            "service": settings.APP_NAME,
            "version": "1.0.0",
            "docs": f"{settings.API_V1_PREFIX}/docs",
            "redoc": f"{settings.API_V1_PREFIX}/redoc",
        }

    # Register API routers
    from app.api import api_router
    app.include_router(api_router)

    logger.info(f"FastAPI application '{settings.APP_NAME}' created successfully")
    return app


# Create application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
