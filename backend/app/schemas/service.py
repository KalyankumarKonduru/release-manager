"""Service schemas."""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ServiceCreate(BaseModel):
    """Create service request."""

    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    repository_url: HttpUrl
    team_id: UUID
    slack_channel: Optional[str] = None
    owner_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class ServiceUpdate(BaseModel):
    """Update service request."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    repository_url: Optional[HttpUrl] = None
    team_id: Optional[UUID] = None
    slack_channel: Optional[str] = None
    owner_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class ServiceResponse(BaseModel):
    """Service response."""

    id: UUID
    name: str
    description: Optional[str]
    repository_url: str
    team_id: UUID
    slack_channel: Optional[str]
    owner_id: Optional[UUID]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
