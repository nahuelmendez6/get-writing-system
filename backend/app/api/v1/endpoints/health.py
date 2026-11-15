from datetime import UTC, datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db_session
from app.core.logging import logger
from app.schemas.health import HealthCheckResponse

router = APIRouter()


async def check_system_health(db: AsyncSession) -> HealthCheckResponse:
    """Perform health verification pinging the database."""
    db_status = "connected"
    service_status = "healthy"

    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.warning("Database health ping failed: %s", str(exc))
        db_status = "disconnected"
        service_status = "degraded"

    return HealthCheckResponse(
        status=service_status,
        environment=settings.ENVIRONMENT,
        version=settings.VERSION,
        database=db_status,
        timestamp=datetime.now(UTC),
    )


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    description="Check operational health and database connectivity.",
)
async def health_check(
    db: AsyncSession = Depends(get_db_session),
) -> HealthCheckResponse:
    """Returns application health and database connection status."""
    return await check_system_health(db)
