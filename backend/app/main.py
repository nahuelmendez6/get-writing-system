from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.health import check_system_health
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import engine, get_db_session
from app.core.exceptions import setup_exception_handlers
from app.core.logging import logger, setup_logging
from app.schemas.health import HealthCheckResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager handling startup and shutdown events."""
    setup_logging()
    logger.info(
        "Starting %s (v%s) in %s mode",
        settings.PROJECT_NAME,
        settings.VERSION,
        settings.ENVIRONMENT,
    )
    yield
    logger.info("Shutting down %s, disposing database engine", settings.PROJECT_NAME)
    await engine.dispose()


def create_application() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global Exception Handlers
    setup_exception_handlers(app)

    # Root Health Check endpoint: GET /health
    @app.get(
        "/health",
        response_model=HealthCheckResponse,
        status_code=status.HTTP_200_OK,
        tags=["Health"],
        summary="Root health check",
        description="Verify service health and database connectivity at root path.",
    )
    async def root_health_check(
        db: AsyncSession = Depends(get_db_session),
    ) -> HealthCheckResponse:
        return await check_system_health(db)

    # API v1 Router: includes GET /api/v1/health
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_application()
