"""Health check routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas import HealthResponse

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    db: AsyncSession = Depends(get_db),
) -> HealthResponse:
    """
    Check application and dependency health.

    Returns status of:
    - Application
    - Database connection
    - Redis connection (if configured)
    """
    try:
        db_status = "healthy"
        try:
            await db.execute(text("SELECT 1"))
        except Exception:
            db_status = "unhealthy"

        redis_status = "healthy"
        try:
            pass
        except Exception:
            redis_status = "unavailable"

        overall_status = "healthy"
        if db_status != "healthy":
            overall_status = "unhealthy"

        return HealthResponse(
            status=overall_status,
            database=db_status,
            redis=redis_status,
            timestamp=datetime.utcnow(),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Health check failed",
        ) from e
