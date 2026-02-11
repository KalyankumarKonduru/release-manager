"""Pipeline stage model."""

from typing import Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy import String, ForeignKey, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class PipelineStage(BaseModel):
    """Pipeline stage model."""

    __tablename__ = "pipeline_stages"

    deployment_id: Mapped[UUID] = mapped_column(ForeignKey("deployments.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    order: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=3600)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    deployment: Mapped["Deployment"] = relationship("Deployment", back_populates="stages")
