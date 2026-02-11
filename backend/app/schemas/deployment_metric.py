"""Deployment metric schemas."""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class DeploymentMetricResponse(BaseModel):
    """Deployment metric response."""

    id: UUID
    deployment_id: UUID
    metric_name: str
    metric_value: float
    unit: str
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MetricsSummary(BaseModel):
    """Metrics summary."""

    mean_time_to_recovery: float = Field(description="MTTR in minutes")
    deployment_frequency: float = Field(description="Deployments per day")
    change_failure_rate: float = Field(description="Percentage of deployments that failed")
    lead_time: float = Field(description="Lead time in hours")
    total_deployments: int
    failed_deployments: int
    successful_deployments: int
    period_start: datetime
    period_end: datetime

    model_config = ConfigDict(from_attributes=True)
