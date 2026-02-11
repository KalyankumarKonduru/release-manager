"""Deployment metric model."""

from uuid import UUID
from sqlalchemy import String, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class DeploymentMetric(BaseModel):
    """Deployment metric model."""

    __tablename__ = "deployment_metrics"

    deployment_id: Mapped[UUID] = mapped_column(ForeignKey("deployments.id"), index=True)
    metric_name: Mapped[str] = mapped_column(String(100), index=True)
    metric_value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(50))
