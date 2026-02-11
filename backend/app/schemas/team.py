"""Team schemas."""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class TeamCreate(BaseModel):
    """Create team request."""

    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    slack_channel: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TeamUpdate(BaseModel):
    """Update team request."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    slack_channel: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TeamResponse(BaseModel):
    """Team response."""

    id: UUID
    name: str
    description: Optional[str]
    slack_channel: Optional[str]
    member_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
