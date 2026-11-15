from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class HealthCheckResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str = Field(
        ..., description="Estado general del servicio ('healthy', 'degraded')"
    )
    environment: str = Field(
        ...,
        description="Entorno ('development', 'staging', 'production')",
    )
    version: str = Field(..., description="Versión del backend")
    database: str = Field(..., description="Estado BD ('connected', 'disconnected')")
    timestamp: datetime = Field(
        ..., description="Marca temporal UTC de la verificación"
    )


class ErrorDetail(BaseModel):
    error_code: str = Field(..., description="Código de error canónico")
    message: str = Field(..., description="Mensaje explicativo para el cliente")
    details: dict[str, Any] = Field(
        default_factory=dict, description="Metadatos adicionales del fallo"
    )


class StandardErrorResponse(BaseModel):
    detail: ErrorDetail
