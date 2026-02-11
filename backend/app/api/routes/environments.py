"""Environment routes."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.models.environment import Environment
from app.models.deployment import Deployment
from app.models.user import User
from app.schemas import (
    EnvironmentCreate,
    EnvironmentUpdate,
    EnvironmentResponse,
    DeploymentResponse,
    MessageResponse,
)

router = APIRouter(prefix="/api/environments", tags=["environments"])


@router.post("", response_model=EnvironmentResponse, status_code=status.HTTP_201_CREATED)
async def create_environment(
    env_data: EnvironmentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> EnvironmentResponse:
    """
    Create a new environment.

    - **name**: Environment name
    - **environment_type**: Type of environment (dev, staging, production, test)
    - **description**: Optional environment description
    - **config_path**: Optional path to configuration
    """
    try:
        new_environment = Environment(
            name=env_data.name,
            description=env_data.description,
            environment_type=env_data.environment_type,
            config_path=env_data.config_path,
            is_active=True,
        )

        db.add(new_environment)
        await db.commit()
        await db.refresh(new_environment)

        return EnvironmentResponse.model_validate(new_environment)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create environment",
        ) from e


@router.get("", response_model=list[EnvironmentResponse])
async def list_environments(
    env_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[EnvironmentResponse]:
    """
    List environments with optional filters.

    - **env_type**: Filter by environment type
    - **skip**: Number of items to skip
    - **limit**: Number of items to return
    """
    try:
        query = select(Environment)

        if env_type:
            query = query.where(Environment.environment_type == env_type)

        result = await db.execute(
            query.order_by(desc(Environment.created_at)).offset(skip).limit(limit)
        )
        items = result.scalars().all()

        return [EnvironmentResponse.model_validate(item) for item in items]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list environments",
        ) from e


@router.get("/{environment_id}", response_model=EnvironmentResponse)
async def get_environment(
    environment_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> EnvironmentResponse:
    """Get a specific environment by ID."""
    try:
        result = await db.execute(
            select(Environment).where(Environment.id == environment_id)
        )
        environment = result.scalar_one_or_none()

        if not environment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found",
            )

        return EnvironmentResponse.model_validate(environment)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get environment",
        ) from e


@router.put("/{environment_id}", response_model=EnvironmentResponse)
async def update_environment(
    environment_id: UUID,
    env_data: EnvironmentUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> EnvironmentResponse:
    """Update an environment."""
    try:
        result = await db.execute(
            select(Environment).where(Environment.id == environment_id)
        )
        environment = result.scalar_one_or_none()

        if not environment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found",
            )

        update_data = env_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(environment, field, value)

        await db.commit()
        await db.refresh(environment)

        return EnvironmentResponse.model_validate(environment)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update environment",
        ) from e


@router.delete("/{environment_id}", response_model=MessageResponse)
async def delete_environment(
    environment_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Delete an environment."""
    try:
        result = await db.execute(
            select(Environment).where(Environment.id == environment_id)
        )
        environment = result.scalar_one_or_none()

        if not environment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found",
            )

        await db.delete(environment)
        await db.commit()

        return MessageResponse(message="Environment deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete environment",
        ) from e


@router.get("/{environment_id}/deployments", response_model=list[DeploymentResponse])
async def get_environment_deployments(
    environment_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[DeploymentResponse]:
    """
    Get all deployments for an environment.

    - **environment_id**: ID of the environment
    """
    try:
        result = await db.execute(
            select(Environment).where(Environment.id == environment_id)
        )
        environment = result.scalar_one_or_none()

        if not environment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found",
            )

        result = await db.execute(
            select(Deployment)
            .where(Deployment.environment_id == environment_id)
            .order_by(desc(Deployment.created_at))
            .offset(skip)
            .limit(limit)
        )
        deployments = result.scalars().all()

        return [DeploymentResponse.model_validate(d) for d in deployments]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get environment deployments",
        ) from e
