"""Deployment model."""

from typing import Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy import String, ForeignKey, DateTime, event
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Deployment(BaseModel):
    """Deployment model."""

    __tablename__ = "deployments"

    release_id: Mapped[UUID] = mapped_column(ForeignKey("releases.id"), index=True)
    environment_id: Mapped[UUID] = mapped_column(ForeignKey("environments.id"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    deployed_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    deployed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    stages: Mapped[list] = relationship("PipelineStage", back_populates="deployment")
