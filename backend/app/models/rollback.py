"""Rollback model."""

from typing import Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy import String, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class Rollback(BaseModel):
    """Rollback model."""

    __tablename__ = "rollbacks"

    deployment_id: Mapped[UUID] = mapped_column(ForeignKey("deployments.id"), index=True)
    target_release_id: Mapped[UUID] = mapped_column(ForeignKey("releases.id"))
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    initiated_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
