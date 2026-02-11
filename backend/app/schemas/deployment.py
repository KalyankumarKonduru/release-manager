"""Deployment schemas."""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class DeploymentCreate(BaseModel):
    """Create deployment request."""

    release_id: UUID
    environment_id: UUID
    deployed_by: UUID

    model_config = ConfigDict(from_attributes=True)


class DeploymentUpdate(BaseModel):
    """Update deployment request."""

    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed|failed|rolled_back)$")

    model_config = ConfigDict(from_attributes=True)


class DeploymentResponse(BaseModel):
    """Deployment response."""

    id: UUID
    release_id: UUID
    environment_id: UUID
    status: str
    deployed_by: UUID
    deployed_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PipelineStageDetail(BaseModel):
    """Pipeline stage detail."""

    id: UUID
    name: str
    order: int
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class DeploymentWithStages(DeploymentResponse):
    """Deployment with pipeline stages."""

    stages: List[PipelineStageDetail] = []

    model_config = ConfigDict(from_attributes=True)
