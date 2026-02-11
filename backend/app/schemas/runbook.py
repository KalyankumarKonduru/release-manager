"""Runbook schemas."""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class RunbookCreate(BaseModel):
    """Create runbook request."""

    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=10)
    service_id: Optional[UUID] = None
    environment_id: Optional[UUID] = None
    tags: Optional[list[str]] = None
    created_by: UUID

    model_config = ConfigDict(from_attributes=True)


class RunbookUpdate(BaseModel):
    """Update runbook request."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=10)
    tags: Optional[list[str]] = None

    model_config = ConfigDict(from_attributes=True)


class RunbookResponse(BaseModel):
    """Runbook response."""

    id: UUID
    title: str
    content: str
    service_id: Optional[UUID]
    environment_id: Optional[UUID]
    tags: Optional[list[str]]
    created_by: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
