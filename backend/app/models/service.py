"""Service model."""

from typing import Optional
from uuid import UUID
from sqlalchemy import String, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class Service(BaseModel):
    """Service model."""

    __tablename__ = "services"

    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    repository_url: Mapped[str] = mapped_column(String(500))
    team_id: Mapped[UUID] = mapped_column(ForeignKey("teams.id"))
    slack_channel: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    owner_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
