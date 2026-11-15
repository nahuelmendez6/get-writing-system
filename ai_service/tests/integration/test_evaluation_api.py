from typing import Any

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoints(async_client: AsyncClient) -> None:
    # 1. Root /health
    resp_root = await async_client.get("/health")
    assert resp_root.status_code == 200
    data_root = resp_root.json()
    assert data_root["status"] == "healthy"
    assert data_root["service"] == "ai_service"
    assert data_root["zdr_enforced"] is True

    # 2. Versioned /internal/v1/health
    resp_v1 = await async_client.get("/internal/v1/health")
    assert resp_v1.status_code == 200
    data_v1 = resp_v1.json()
    assert data_v1["status"] == "healthy"


@pytest.mark.asyncio
async def test_evaluate_b2_happy_path(
    async_client: AsyncClient, sample_b2_request: dict[str, Any]
) -> None:
    response = await async_client.post("/internal/v1/evaluate", json=sample_b2_request)
    assert response.status_code == 200
    data = response.json()

    assert data["submission_id"] == sample_b2_request["submission_id"]
    assert data["status"] == "SUCCESS"
    assert data["word_count"] > 0
    assert len(data["mistakes"]) >= 2
    assert "exemplar_model" in data
    assert len(data["exemplar_model"]) > 20

    # AI Detection metrics
    ai_det = data["ai_detection"]
    assert "probability" in ai_det
    assert ai_det["is_likely_ai"] is False
    assert ai_det["confidence"] in ["LOW", "MEDIUM", "HIGH"]
    assert "execution_time_seconds" in data


@pytest.mark.asyncio
async def test_evaluate_ai_generated_alert(
    async_client: AsyncClient, sample_ai_generated_request: dict[str, Any]
) -> None:
    response = await async_client.post(
        "/internal/v1/evaluate", json=sample_ai_generated_request
    )
    assert response.status_code == 200
    data = response.json()

    ai_det = data["ai_detection"]
    assert ai_det["is_likely_ai"] is True
    assert ai_det["probability"] >= 0.70
    assert "rationale" in ai_det


@pytest.mark.asyncio
async def test_evaluate_invalid_level_returns_422(
    async_client: AsyncClient, sample_b2_request: dict[str, Any]
) -> None:
    payload = dict(sample_b2_request)
    payload["level"] = "INVALID_LEVEL"

    response = await async_client.post("/internal/v1/evaluate", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert data["detail"]["error_code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_404_error_formatting(async_client: AsyncClient) -> None:
    response = await async_client.get("/internal/v1/unknown-endpoint")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"]["error_code"] == "NOT_FOUND"
