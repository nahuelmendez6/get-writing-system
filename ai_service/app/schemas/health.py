from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HealthCheckResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str = Field(..., description="Operational status of the service")
    service: str = Field(..., description="Service name")
    environment: str = Field(..., description="Runtime environment")
    version: str = Field(..., description="Service version")
    zdr_enforced: bool = Field(
        ..., description="Indicates if Zero Data Retention is active"
    )
    timestamp: datetime = Field(..., description="Verification timestamp UTC")
