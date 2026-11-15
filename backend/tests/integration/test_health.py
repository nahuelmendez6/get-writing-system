from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.main import app


@pytest.mark.asyncio
async def test_health_check_happy_path(async_client: AsyncClient) -> None:
    # 1. Root /health endpoint
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["environment"] == "development"
    assert data["version"] == "0.1.0"
    assert "timestamp" in data

    # 2. Versioned /api/v1/health endpoint
    v1_response = await async_client.get("/api/v1/health")
    assert v1_response.status_code == 200
    v1_data = v1_response.json()
    assert v1_data["status"] == "healthy"
    assert v1_data["database"] == "connected"
    assert v1_data["environment"] == "development"
    assert v1_data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_health_check_degraded_mode(async_client: AsyncClient) -> None:
    # Mock database session that raises an error when executing SELECT 1
    mock_failing_session = AsyncMock(spec=AsyncSession)
    mock_failing_session.execute.side_effect = ConnectionRefusedError(
        "Database unreachable"
    )

    async def _override_failing_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_failing_session

    app.dependency_overrides[get_db_session] = _override_failing_db

    try:
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["database"] == "disconnected"
        assert data["environment"] == "development"
        assert data["version"] == "0.1.0"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_standard_error_format_on_404(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/non-existent-route")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "error_code" in data["detail"]
    assert data["detail"]["error_code"] == "NOT_FOUND"
    assert "message" in data["detail"]
    assert "details" in data["detail"]


@pytest.mark.asyncio
async def test_custom_app_exception_and_500_handling(async_client: AsyncClient) -> None:
    from app.core.exceptions import AppException

    # Temporarily mount test routes to verify error handlers
    @app.get("/test-custom-app-error")
    async def route_custom_error() -> None:
        raise AppException(
            error_code="CUSTOM_FAILURE",
            message="Error de prueba",
            status_code=400,
            details={"foo": "bar"},
        )

    @app.get("/test-unhandled-error")
    async def route_unhandled_error() -> None:
        raise RuntimeError("Unexpected failure!")

    # 1. Custom AppException
    resp_app_err = await async_client.get("/test-custom-app-error")
    assert resp_app_err.status_code == 400
    err_data = resp_app_err.json()
    assert err_data["detail"]["error_code"] == "CUSTOM_FAILURE"
    assert err_data["detail"]["message"] == "Error de prueba"
    assert err_data["detail"]["details"] == {"foo": "bar"}

    # 2. Unhandled Exception (sanitized 500)
    resp_unhandled = await async_client.get("/test-unhandled-error")
    assert resp_unhandled.status_code == 500
    unhandled_data = resp_unhandled.json()
    assert unhandled_data["detail"]["error_code"] == "INTERNAL_SERVER_ERROR"
    assert unhandled_data["detail"]["message"] == "Ha ocurrido un error inesperado."
