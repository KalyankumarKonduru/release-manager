"""Rollback routes."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.models.rollback import Rollback
from app.models.deployment import Deployment
from app.models.release import Release
from app.models.user import User
from app.schemas import (
    RollbackCreate,
    RollbackResponse,
    MessageResponse,
)

router = APIRouter(prefix="/api/rollbacks", tags=["rollbacks"])


@router.post("", response_model=RollbackResponse, status_code=status.HTTP_201_CREATED)
async def create_rollback(
    rollback_data: RollbackCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> RollbackResponse:
    """
    Initiate a rollback.

    - **deployment_id**: ID of the deployment to rollback
    - **target_release_id**: ID of the release to rollback to
    - **reason**: Reason for the rollback
    """
    try:
        result = await db.execute(
            select(Deployment).where(Deployment.id == rollback_data.deployment_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deployment not found",
            )

        result = await db.execute(
            select(Release).where(Release.id == rollback_data.target_release_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target release not found",
            )

        new_rollback = Rollback(
            deployment_id=rollback_data.deployment_id,
            target_release_id=rollback_data.target_release_id,
            reason=rollback_data.reason,
            initiated_by=current_user.id,
            status="pending",
        )

        db.add(new_rollback)
        await db.commit()
        await db.refresh(new_rollback)

        return RollbackResponse.model_validate(new_rollback)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create rollback",
        ) from e


@router.get("", response_model=list[RollbackResponse])
async def list_rollbacks(
    deployment_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[RollbackResponse]:
    """
    List rollbacks with optional filters.

    - **deployment_id**: Filter by deployment ID
    - **status**: Filter by status (pending, in_progress, completed, failed)
    - **skip**: Number of items to skip
    - **limit**: Number of items to return
    """
    try:
        query = select(Rollback)

        if deployment_id:
            query = query.where(Rollback.deployment_id == deployment_id)
        if status:
            query = query.where(Rollback.status == status)

        result = await db.execute(
            query.order_by(desc(Rollback.created_at)).offset(skip).limit(limit)
        )
        items = result.scalars().all()

        return [RollbackResponse.model_validate(item) for item in items]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list rollbacks",
        ) from e


@router.get("/{rollback_id}", response_model=RollbackResponse)
async def get_rollback(
    rollback_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> RollbackResponse:
    """Get a specific rollback by ID."""
    try:
        result = await db.execute(
            select(Rollback).where(Rollback.id == rollback_id)
        )
        rollback = result.scalar_one_or_none()

        if not rollback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rollback not found",
            )

        return RollbackResponse.model_validate(rollback)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get rollback",
        ) from e


@router.get("/{rollback_id}/status", response_model=dict)
async def get_rollback_status(
    rollback_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get rollback status and progress.

    - **rollback_id**: ID of the rollback
    """
    try:
        result = await db.execute(
            select(Rollback).where(Rollback.id == rollback_id)
        )
        rollback = result.scalar_one_or_none()

        if not rollback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rollback not found",
            )

        return {
            "rollback_id": str(rollback.id),
            "status": rollback.status,
            "deployment_id": str(rollback.deployment_id),
            "target_release_id": str(rollback.target_release_id),
            "reason": rollback.reason,
            "initiated_by": str(rollback.initiated_by),
            "completed_at": rollback.completed_at,
            "progress": 50,  # Placeholder for actual progress tracking
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get rollback status",
        ) from e
