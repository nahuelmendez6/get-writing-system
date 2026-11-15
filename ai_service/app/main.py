from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.core.logging import logger, setup_logging
from app.schemas.health import HealthCheckResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    logger.info(
        "Starting %s (v%s) in %s mode [ZDR Enforced=%s, Provider=%s]",
        settings.PROJECT_NAME,
        settings.VERSION,
        settings.ENVIRONMENT,
        settings.ENFORCE_ZDR,
        settings.LLM_PROVIDER,
    )
    yield
    logger.info("Stopping %s", settings.PROJECT_NAME)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/internal/v1/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_exception_handlers(app)

    # Root health check endpoint
    @app.get(
        "/health",
        response_model=HealthCheckResponse,
        status_code=status.HTTP_200_OK,
        tags=["Health"],
        summary="Root health endpoint",
    )
    async def root_health() -> HealthCheckResponse:
        return HealthCheckResponse(
            status="healthy",
            service="ai_service",
            environment=settings.ENVIRONMENT,
            version=settings.VERSION,
            zdr_enforced=settings.ENFORCE_ZDR,
            timestamp=datetime.now(UTC),
        )

    # Internal API routes mounted at /internal/v1
    app.include_router(api_router, prefix="/internal/v1")

    return app


app = create_app()
