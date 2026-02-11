"""Pipeline stage schemas."""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PipelineStageCreate(BaseModel):
    """Create pipeline stage request."""

    deployment_id: UUID
    name: str = Field(min_length=1, max_length=255)
    order: int = Field(ge=0)
    timeout_seconds: int = Field(default=3600, ge=60)

    model_config = ConfigDict(from_attributes=True)


class PipelineStageUpdate(BaseModel):
    """Update pipeline stage request."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    order: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(pending|running|completed|failed|skipped)$")
    timeout_seconds: Optional[int] = Field(None, ge=60)

    model_config = ConfigDict(from_attributes=True)


class PipelineStageResponse(BaseModel):
    """Pipeline stage response."""

    id: UUID
    deployment_id: UUID
    name: str
    order: int
    status: str
    timeout_seconds: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    output: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
