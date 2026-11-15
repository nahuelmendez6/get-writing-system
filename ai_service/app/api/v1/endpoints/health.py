from datetime import UTC, datetime

from fastapi import APIRouter, status

from app.core.config import settings
from app.schemas.health import HealthCheckResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check operational health and Zero Data Retention policy status.",
)
async def get_health() -> HealthCheckResponse:
    return HealthCheckResponse(
        status="healthy",
        service="ai_service",
        environment=settings.ENVIRONMENT,
        version=settings.VERSION,
        zdr_enforced=settings.ENFORCE_ZDR,
        timestamp=datetime.now(UTC),
    )
