"""API module with router configuration."""

from fastapi import APIRouter

from app.api.routes import (
    auth,
    releases,
    deployments,
    services,
    environments,
    approvals,
    audit_logs,
    rollbacks,
    runbooks,
    analytics,
    health,
)

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router)
api_router.include_router(releases.router)
api_router.include_router(deployments.router)
api_router.include_router(services.router)
api_router.include_router(environments.router)
api_router.include_router(approvals.router)
api_router.include_router(audit_logs.router)
api_router.include_router(rollbacks.router)
api_router.include_router(runbooks.router)
api_router.include_router(analytics.router)
api_router.include_router(health.router)

__all__ = ["api_router"]
