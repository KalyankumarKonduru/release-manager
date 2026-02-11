"""Deployment routes."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.models.deployment import Deployment
from app.models.release import Release
from app.models.environment import Environment
from app.models.user import User
from app.models.pipeline_stage import PipelineStage
from app.schemas import (
    DeploymentCreate,
    DeploymentUpdate,
    DeploymentResponse,
    DeploymentWithStages,
    MessageResponse,
)

router = APIRouter(prefix="/api/deployments", tags=["deployments"])


@router.post("", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED)
async def create_deployment(
    deployment_data: DeploymentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> DeploymentResponse:
    """
    Create a new deployment.

    - **release_id**: ID of the release to deploy
    - **environment_id**: ID of the target environment
    """
    try:
        result = await db.execute(
            select(Release).where(Release.id == deployment_data.release_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Release not found",
            )

        result = await db.execute(
            select(Environment).where(
                Environment.id == deployment_data.environment_id
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found",
            )

        new_deployment = Deployment(
            release_id=deployment_data.release_id,
            environment_id=deployment_data.environment_id,
            deployed_by=current_user.id,
            status="pending",
        )

        db.add(new_deployment)
        await db.commit()
        await db.refresh(new_deployment)

        return DeploymentResponse.model_validate(new_deployment)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create deployment",
        ) from e


@router.get("", response_model=list[DeploymentResponse])
async def list_deployments(
    release_id: Optional[UUID] = Query(None),
    environment_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[DeploymentResponse]:
    """
    List deployments with optional filters.

    - **release_id**: Filter by release ID
    - **environment_id**: Filter by environment ID
    - **status**: Filter by status
    - **skip**: Number of items to skip
    - **limit**: Number of items to return
    """
    try:
        query = select(Deployment)

        if release_id:
            query = query.where(Deployment.release_id == release_id)
        if environment_id:
            query = query.where(Deployment.environment_id == environment_id)
        if status:
            query = query.where(Deployment.status == status)

        result = await db.execute(
            query.order_by(desc(Deployment.created_at)).offset(skip).limit(limit)
        )
        items = result.scalars().all()

        return [DeploymentResponse.model_validate(item) for item in items]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list deployments",
        ) from e


@router.get("/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(
    deployment_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> DeploymentResponse:
    """Get a specific deployment by ID."""
    try:
        result = await db.execute(
            select(Deployment).where(Deployment.id == deployment_id)
        )
        deployment = result.scalar_one_or_none()

        if not deployment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deployment not found",
            )

        return DeploymentResponse.model_validate(deployment)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get deployment",
        ) from e


@router.put("/{deployment_id}", response_model=DeploymentResponse)
async def update_deployment(
    deployment_id: UUID,
    deployment_data: DeploymentUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> DeploymentResponse:
    """Update a deployment."""
    try:
        result = await db.execute(
            select(Deployment).where(Deployment.id == deployment_id)
        )
        deployment = result.scalar_one_or_none()

        if not deployment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deployment not found",
            )

        update_data = deployment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(deployment, field, value)

        await db.commit()
        await db.refresh(deployment)

        return DeploymentResponse.model_validate(deployment)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update deployment",
        ) from e


@router.delete("/{deployment_id}", response_model=MessageResponse)
async def delete_deployment(
    deployment_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Delete a deployment."""
    try:
        result = await db.execute(
            select(Deployment).where(Deployment.id == deployment_id)
        )
        deployment = result.scalar_one_or_none()

        if not deployment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deployment not found",
            )

        await db.delete(deployment)
        await db.commit()

        return MessageResponse(message="Deployment deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete deployment",
        ) from e


@router.post("/{deployment_id}/approve", response_model=MessageResponse)
async def approve_deployment(
    deployment_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """
    Approve a deployment.

    - **deployment_id**: ID of the deployment to approve
    """
    try:
        result = await db.execute(
            select(Deployment).where(Deployment.id == deployment_id)
        )
        deployment = result.scalar_one_or_none()

        if not deployment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deployment not found",
            )

        deployment.status = "in_progress"
        await db.commit()
        await db.refresh(deployment)

        return MessageResponse(message="Deployment approved")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve deployment",
        ) from e


@router.post("/{deployment_id}/rollback", response_model=MessageResponse)
async def rollback_deployment(
    deployment_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """
    Rollback a deployment.

    - **deployment_id**: ID of the deployment to rollback
    """
    try:
        result = await db.execute(
            select(Deployment).where(Deployment.id == deployment_id)
        )
        deployment = result.scalar_one_or_none()

        if not deployment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deployment not found",
            )

        deployment.status = "rolled_back"
        await db.commit()
        await db.refresh(deployment)

        return MessageResponse(message="Deployment rolled back")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rollback deployment",
        ) from e


@router.get("/{deployment_id}/stages", response_model=DeploymentWithStages)
async def get_deployment_stages(
    deployment_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> DeploymentWithStages:
    """Get deployment with all pipeline stages."""
    try:
        result = await db.execute(
            select(Deployment)
            .where(Deployment.id == deployment_id)
            .options(selectinload(Deployment.stages))
        )
        deployment = result.scalar_one_or_none()

        if not deployment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deployment not found",
            )

        return DeploymentWithStages.model_validate(deployment)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get deployment stages",
        ) from e


@router.get("/{deployment_id}/logs", response_model=dict)
async def get_deployment_logs(
    deployment_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get deployment logs."""
    try:
        result = await db.execute(
            select(Deployment).where(Deployment.id == deployment_id)
        )
        deployment = result.scalar_one_or_none()

        if not deployment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deployment not found",
            )

        return {
            "deployment_id": str(deployment.id),
            "status": deployment.status,
            "logs": "Deployment logs would be retrieved from external logging system",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get deployment logs",
        ) from e
