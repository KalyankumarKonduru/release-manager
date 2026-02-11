"""Deployment orchestration service for managing releases across environments."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.deployment import Deployment
from app.models.deployment_metric import DeploymentMetric
from app.models.pipeline_stage import PipelineStage
from app.models.release import Release
from app.models.rollback import Rollback
from app.services.audit import AuditService


class DeploymentService:
    """Service for managing deployments and releases."""

    @staticmethod
    async def create_deployment(
        db: AsyncSession,
        release_id: UUID,
        environment_id: UUID,
        user_id: UUID,
    ) -> Deployment:
        """
        Create a new deployment record.

        Args:
            db: Database session
            release_id: ID of the release to deploy
            environment_id: ID of the target environment
            user_id: ID of the user creating the deployment

        Returns:
            The created Deployment record
        """
        deployment = Deployment(
            release_id=release_id,
            environment_id=environment_id,
            status="pending",
            deployed_by=user_id,
            deployed_at=datetime.utcnow(),
        )
        db.add(deployment)
        await db.flush()

        # Log the action
        await AuditService.log_action(
            db=db,
            user_id=user_id,
            action="create_deployment",
            resource_type="deployment",
            resource_id=deployment.id,
            metadata={
                "release_id": str(release_id),
                "environment_id": str(environment_id),
                "status": deployment.status,
            },
        )

        return deployment

    @staticmethod
    async def promote_release(
        db: AsyncSession,
        release_id: UUID,
        target_env_id: UUID,
        user_id: UUID,
    ) -> Deployment:
        """
        Promote a release to the target environment.

        This handles the pipeline progression logic, creating a deployment
        and initializing pipeline stages.

        Args:
            db: Database session
            release_id: ID of the release to promote
            target_env_id: ID of the target environment
            user_id: ID of the user performing the promotion

        Returns:
            The created Deployment record
        """
        # Verify release exists
        release_result = await db.execute(select(Release).where(Release.id == release_id))
        release = release_result.scalar_one_or_none()

        if not release:
            raise ValueError(f"Release {release_id} not found")

        # Update release status
        release.status = "promoted"
        await db.flush()

        # Create deployment
        deployment = await DeploymentService.create_deployment(
            db=db,
            release_id=release_id,
            environment_id=target_env_id,
            user_id=user_id,
        )

        # Initialize pipeline stages
        stage_names = ["build", "test", "security_scan", "deploy", "smoke_test"]

        for idx, stage_name in enumerate(stage_names):
            stage = PipelineStage(
                deployment_id=deployment.id,
                name=stage_name,
                order=idx,
                status="pending",
                timeout_seconds=3600,
            )
            db.add(stage)

        await db.flush()

        # Log the promotion action
        await AuditService.log_action(
            db=db,
            user_id=user_id,
            action="promote_release",
            resource_type="release",
            resource_id=release_id,
            metadata={
                "deployment_id": str(deployment.id),
                "target_environment_id": str(target_env_id),
                "release_version": release.version,
            },
        )

        return deployment

    @staticmethod
    async def execute_rollback(
        db: AsyncSession,
        deployment_id: UUID,
        user_id: UUID,
        reason: str,
    ) -> Rollback:
        """
        Execute a rollback for a failed deployment.

        Args:
            db: Database session
            deployment_id: ID of the deployment to rollback
            user_id: ID of the user initiating the rollback
            reason: Reason for the rollback

        Returns:
            The created Rollback record
        """
        # Get the deployment
        deployment_result = await db.execute(
            select(Deployment).where(Deployment.id == deployment_id)
        )
        deployment = deployment_result.scalar_one_or_none()

        if not deployment:
            raise ValueError(f"Deployment {deployment_id} not found")

        # Get the release
        release_result = await db.execute(
            select(Release).where(Release.id == deployment.release_id)
        )
        release = release_result.scalar_one_or_none()

        if not release:
            raise ValueError(f"Release {release.id} not found")

        # Find the previous stable version (most recent completed release)
        previous_release_result = await db.execute(
            select(Release)
            .where(
                and_(
                    Release.service_id == release.service_id,
                    Release.id != release.id,
                    Release.status == "completed",
                )
            )
            .order_by(Release.created_at.desc())
            .limit(1)
        )
        previous_release = previous_release_result.scalar_one_or_none()

        if not previous_release:
            raise ValueError(f"No previous stable release found for rollback")

        # Create rollback record
        rollback = Rollback(
            deployment_id=deployment_id,
            target_release_id=previous_release.id,
            reason=reason,
            status="in-progress",
            initiated_by=user_id,
        )
        db.add(rollback)
        await db.flush()

        # Update deployment status
        deployment.status = "rolled_back"
        deployment.completed_at = datetime.utcnow()

        # Update release status
        release.status = "rolled_back"

        await db.flush()

        # Log the rollback action
        await AuditService.log_action(
            db=db,
            user_id=user_id,
            action="execute_rollback",
            resource_type="deployment",
            resource_id=deployment_id,
            metadata={
                "rollback_id": str(rollback.id),
                "from_version": release.version,
                "to_version": previous_release.version,
                "reason": reason,
            },
        )

        return rollback

    @staticmethod
    async def get_deployment_with_stages(
        db: AsyncSession,
        deployment_id: UUID,
    ) -> Optional[Deployment]:
        """
        Get a deployment with all its pipeline stages.

        Args:
            db: Database session
            deployment_id: ID of the deployment to fetch

        Returns:
            The Deployment record with stages, or None if not found
        """
        result = await db.execute(
            select(Deployment)
            .where(Deployment.id == deployment_id)
            .options(selectinload(Deployment.stages))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_deployment_with_metrics(
        db: AsyncSession,
        deployment_id: UUID,
    ) -> Optional[dict]:
        """
        Get a deployment with its associated metrics and stages.

        Args:
            db: Database session
            deployment_id: ID of the deployment to fetch

        Returns:
            Dictionary containing deployment details with metrics and stages
        """
        # Get deployment with stages
        deployment_result = await db.execute(
            select(Deployment)
            .where(Deployment.id == deployment_id)
            .options(selectinload(Deployment.stages))
        )
        deployment = deployment_result.scalar_one_or_none()

        if not deployment:
            return None

        # Get metrics
        metrics_result = await db.execute(
            select(DeploymentMetric).where(DeploymentMetric.deployment_id == deployment_id)
        )
        metrics = metrics_result.scalars().all()

        return {
            "deployment": deployment,
            "metrics": metrics,
            "stages": deployment.stages,
        }

    @staticmethod
    async def update_pipeline_stage(
        db: AsyncSession,
        stage_id: UUID,
        status: str,
        output: Optional[str] = None,
    ) -> PipelineStage:
        """
        Update the status of a pipeline stage.

        Args:
            db: Database session
            stage_id: ID of the stage to update
            status: New status for the stage
            output: Optional output/logs from the stage

        Returns:
            The updated PipelineStage record
        """
        stage_result = await db.execute(
            select(PipelineStage).where(PipelineStage.id == stage_id)
        )
        stage = stage_result.scalar_one_or_none()

        if not stage:
            raise ValueError(f"Pipeline stage {stage_id} not found")

        stage.status = status
        if output:
            stage.output = output

        if status == "in-progress" and not stage.started_at:
            stage.started_at = datetime.utcnow()
        elif status == "completed" and not stage.completed_at:
            stage.completed_at = datetime.utcnow()
        elif status == "failed" and not stage.completed_at:
            stage.completed_at = datetime.utcnow()

        await db.flush()
        return stage

    @staticmethod
    async def record_deployment_metrics(
        db: AsyncSession,
        deployment_id: UUID,
        metric_name: str,
        metric_value: float,
        unit: str,
    ) -> DeploymentMetric:
        """
        Record a metric for a deployment.

        Args:
            db: Database session
            deployment_id: ID of the deployment
            metric_name: Name of the metric
            metric_value: Value of the metric
            unit: Unit of measurement

        Returns:
            The created DeploymentMetric record
        """
        metric = DeploymentMetric(
            deployment_id=deployment_id,
            metric_name=metric_name,
            metric_value=metric_value,
            unit=unit,
        )
        db.add(metric)
        await db.flush()
        return metric
