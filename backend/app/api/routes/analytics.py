"""Analytics and metrics routes."""

from typing import Annotated, Optional
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.deployment import Deployment
from app.models.service import Service
from app.models.environment import Environment
from app.schemas import (
    MetricsSummary,
)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


async def calculate_metrics_summary(
    db: AsyncSession,
    days: int = 30,
) -> MetricsSummary:
    """Calculate metrics summary for the given period."""
    start_date = datetime.utcnow() - timedelta(days=days)
    end_date = datetime.utcnow()

    result = await db.execute(
        select(Deployment).where(
            Deployment.created_at >= start_date,
            Deployment.created_at <= end_date,
        )
    )
    deployments = result.scalars().all()

    total_deployments = len(deployments)
    failed_deployments = sum(
        1 for d in deployments if d.status == "failed"
    )
    successful_deployments = total_deployments - failed_deployments

    change_failure_rate = (
        (failed_deployments / total_deployments * 100)
        if total_deployments > 0
        else 0
    )

    deployment_frequency = (
        total_deployments / days if days > 0 else 0
    )

    mttr = 0.0
    lead_time = 0.0

    if deployments:
        total_time = 0
        for d in deployments:
            if d.deployed_at and d.completed_at:
                duration = (d.completed_at - d.deployed_at).total_seconds()
                total_time += duration
        mttr = (total_time / len(deployments)) / 60 if deployments else 0

        created_to_deployed = 0
        count = 0
        for d in deployments:
            if d.deployed_at:
                duration = (d.deployed_at - d.created_at).total_seconds()
                created_to_deployed += duration
                count += 1
        lead_time = (created_to_deployed / count / 3600) if count > 0 else 0

    return MetricsSummary(
        mean_time_to_recovery=mttr,
        deployment_frequency=deployment_frequency,
        change_failure_rate=change_failure_rate,
        lead_time=lead_time,
        total_deployments=total_deployments,
        failed_deployments=failed_deployments,
        successful_deployments=successful_deployments,
        period_start=start_date,
        period_end=end_date,
    )


@router.get("/metrics/summary", response_model=MetricsSummary)
async def get_metrics_summary(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
) -> MetricsSummary:
    """
    Get metrics summary for DORA metrics.

    Returns:
    - MTTR (Mean Time To Recovery) in minutes
    - Deployment Frequency (deployments per day)
    - Change Failure Rate (percentage)
    - Lead Time (hours from creation to deployment)

    - **days**: Number of days to analyze (default 30)
    """
    try:
        return await calculate_metrics_summary(db, days)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get metrics summary",
        ) from e


@router.get("/metrics/trends", response_model=list[dict])
async def get_deployment_trends(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """
    Get deployment trends using window functions.

    Returns daily deployment counts and status breakdown.

    - **days**: Number of days to analyze
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)

        result = await db.execute(
            select(Deployment)
            .where(Deployment.created_at >= start_date)
            .order_by(Deployment.created_at)
        )
        deployments = result.scalars().all()

        trends = {}
        for deployment in deployments:
            date_key = deployment.created_at.date().isoformat()
            if date_key not in trends:
                trends[date_key] = {
                    "date": date_key,
                    "total": 0,
                    "successful": 0,
                    "failed": 0,
                    "pending": 0,
                }

            trends[date_key]["total"] += 1
            if deployment.status == "completed":
                trends[date_key]["successful"] += 1
            elif deployment.status == "failed":
                trends[date_key]["failed"] += 1
            else:
                trends[date_key]["pending"] += 1

        return sorted(trends.values(), key=lambda x: x["date"])

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get deployment trends",
        ) from e


@router.get("/metrics/by-service", response_model=list[dict])
async def get_metrics_by_service(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """
    Get metrics grouped by service.

    - **days**: Number of days to analyze
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)

        result = await db.execute(
            select(
                Service.id,
                Service.name,
                func.count(Deployment.id).label("total_deployments"),
                func.sum(
                    (Deployment.status == "completed").cast(int)
                ).label("successful_deployments"),
            )
            .join(
                Deployment,
                Service.id == Deployment.release_id,
                isouter=True,
            )
            .where(Deployment.created_at >= start_date)
            .group_by(Service.id, Service.name)
        )

        metrics = []
        for row in result:
            service_id, service_name, total, successful = row
            if total is None:
                total = 0
            if successful is None:
                successful = 0

            failure_rate = (
                ((total - successful) / total * 100) if total > 0 else 0
            )

            metrics.append({
                "service_id": str(service_id),
                "service_name": service_name,
                "total_deployments": total,
                "successful_deployments": successful,
                "failed_deployments": total - successful,
                "failure_rate": failure_rate,
            })

        return sorted(
            metrics,
            key=lambda x: x["total_deployments"],
            reverse=True,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get service metrics",
        ) from e


@router.get("/metrics/by-environment", response_model=list[dict])
async def get_metrics_by_environment(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """
    Get metrics grouped by environment.

    - **days**: Number of days to analyze
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)

        result = await db.execute(
            select(
                Environment.id,
                Environment.name,
                Environment.environment_type,
                func.count(Deployment.id).label("total_deployments"),
                func.sum(
                    (Deployment.status == "completed").cast(int)
                ).label("successful_deployments"),
            )
            .join(
                Deployment,
                Environment.id == Deployment.environment_id,
                isouter=True,
            )
            .where(Deployment.created_at >= start_date)
            .group_by(
                Environment.id,
                Environment.name,
                Environment.environment_type,
            )
        )

        metrics = []
        for row in result:
            env_id, env_name, env_type, total, successful = row
            if total is None:
                total = 0
            if successful is None:
                successful = 0

            failure_rate = (
                ((total - successful) / total * 100) if total > 0 else 0
            )

            metrics.append({
                "environment_id": str(env_id),
                "environment_name": env_name,
                "environment_type": env_type,
                "total_deployments": total,
                "successful_deployments": successful,
                "failed_deployments": total - successful,
                "failure_rate": failure_rate,
            })

        return sorted(
            metrics,
            key=lambda x: x["total_deployments"],
            reverse=True,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get environment metrics",
        ) from e
