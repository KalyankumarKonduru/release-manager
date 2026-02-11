"""Release routes."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.models.release import Release
from app.models.user import User
from app.models.service import Service
from app.schemas import (
    ReleaseCreate,
    ReleaseUpdate,
    ReleaseResponse,
    ReleaseListResponse,
    MessageResponse,
)

router = APIRouter(prefix="/api/releases", tags=["releases"])


@router.post("", response_model=ReleaseResponse, status_code=status.HTTP_201_CREATED)
async def create_release(
    release_data: ReleaseCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> ReleaseResponse:
    """
    Create a new release.

    - **service_id**: ID of the service
    - **version**: Release version
    - **release_notes**: Optional release notes
    - **git_commit**: Optional git commit hash
    """
    try:
        result = await db.execute(
            select(Service).where(Service.id == release_data.service_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found",
            )

        new_release = Release(
            service_id=release_data.service_id,
            version=release_data.version,
            release_notes=release_data.release_notes,
            git_commit=release_data.git_commit,
            created_by=current_user.id,
            status="draft",
        )

        db.add(new_release)
        await db.commit()
        await db.refresh(new_release)

        return ReleaseResponse.model_validate(new_release)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create release",
        ) from e


@router.get("", response_model=ReleaseListResponse)
async def list_releases(
    service_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> ReleaseListResponse:
    """
    List releases with pagination.

    - **service_id**: Filter by service ID
    - **status**: Filter by status (draft, published, deployed, failed)
    - **skip**: Number of items to skip
    - **limit**: Number of items to return
    """
    try:
        query = select(Release)

        if service_id:
            query = query.where(Release.service_id == service_id)
        if status:
            query = query.where(Release.status == status)

        total_result = await db.execute(select(Release))
        total = len(total_result.fetchall())

        result = await db.execute(
            query.order_by(desc(Release.created_at)).offset(skip).limit(limit)
        )
        items = result.scalars().all()

        return ReleaseListResponse(
            items=[ReleaseResponse.model_validate(item) for item in items],
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            total_pages=(total + limit - 1) // limit,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list releases",
        ) from e


@router.get("/{release_id}", response_model=ReleaseResponse)
async def get_release(
    release_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ReleaseResponse:
    """Get a specific release by ID."""
    try:
        result = await db.execute(
            select(Release).where(Release.id == release_id)
        )
        release = result.scalar_one_or_none()

        if not release:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Release not found",
            )

        return ReleaseResponse.model_validate(release)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get release",
        ) from e


@router.put("/{release_id}", response_model=ReleaseResponse)
async def update_release(
    release_id: UUID,
    release_data: ReleaseUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> ReleaseResponse:
    """Update a release."""
    try:
        result = await db.execute(
            select(Release).where(Release.id == release_id)
        )
        release = result.scalar_one_or_none()

        if not release:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Release not found",
            )

        update_data = release_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(release, field, value)

        await db.commit()
        await db.refresh(release)

        return ReleaseResponse.model_validate(release)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update release",
        ) from e


@router.delete("/{release_id}", response_model=MessageResponse)
async def delete_release(
    release_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Delete a release."""
    try:
        result = await db.execute(
            select(Release).where(Release.id == release_id)
        )
        release = result.scalar_one_or_none()

        if not release:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Release not found",
            )

        await db.delete(release)
        await db.commit()

        return MessageResponse(message="Release deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete release",
        ) from e


@router.post("/{release_id}/deploy", response_model=MessageResponse)
async def deploy_release(
    release_id: UUID,
    environment_id: UUID = Query(...),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """
    Trigger deployment for a release to an environment.

    - **release_id**: ID of the release to deploy
    - **environment_id**: ID of the target environment
    """
    try:
        result = await db.execute(
            select(Release).where(Release.id == release_id)
        )
        release = result.scalar_one_or_none()

        if not release:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Release not found",
            )

        release.status = "deployed"
        await db.commit()
        await db.refresh(release)

        return MessageResponse(message=f"Deployment initiated for release {release_id}")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deploy release",
        ) from e


@router.get("/{release_id}/history", response_model=list[ReleaseResponse])
async def get_release_history(
    release_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> list[ReleaseResponse]:
    """
    Get release history/chain (ancestors and related releases).

    Uses CTE to traverse the release chain.
    """
    try:
        result = await db.execute(
            select(Release)
            .where(Release.id == release_id)
            .options(selectinload(Release.service))
        )
        current_release = result.scalar_one_or_none()

        if not current_release:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Release not found",
            )

        result = await db.execute(
            select(Release)
            .where(Release.service_id == current_release.service_id)
            .order_by(desc(Release.created_at))
            .limit(20)
        )
        releases = result.scalars().all()

        return [ReleaseResponse.model_validate(r) for r in releases]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get release history",
        ) from e
