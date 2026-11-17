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
async def test_evaluate_b2_happy_path_with_rubrics_and_feedback(
    async_client: AsyncClient, sample_b2_request: dict[str, Any]
) -> None:
    """Scenario 3: Evaluación Completa por Rúbrica Cambridge en ai_service.

    Given: Un texto de redacción B2 y un prompt de examen.
    When: POST /internal/v1/evaluate.
    Then: HTTP 200 con rubric_evaluation (4 bandas 0-5, raw_score /20,
          institutional_score /10, justificaciones) y feedback pedagógico (3 tips).
    """
    response = await async_client.post("/internal/v1/evaluate", json=sample_b2_request)
    assert response.status_code == 200
    data = response.json()

    assert data["submission_id"] == sample_b2_request["submission_id"]
    assert data["status"] == "SUCCESS"
    assert data["word_count"] > 0
    assert len(data["mistakes"]) >= 2
    assert "exemplar_model" in data
    assert len(data["exemplar_model"]) > 20

    # 1. Rubric Evaluation Validation
    rubric = data["rubric_evaluation"]
    assert len(rubric["criteria"]) == 4
    criteria_names = [c["name"] for c in rubric["criteria"]]
    assert criteria_names == [
        "Content",
        "Communicative Achievement",
        "Organisation",
        "Language",
    ]

    for c in rubric["criteria"]:
        assert 0.0 <= c["score"] <= 5.0
        assert c["max_score"] == 5.0
        assert len(c["band_descriptor"]) > 10
        assert len(c["justification"]) > 10

    assert 0.0 <= rubric["raw_score"] <= 20.0
    assert 0.0 <= rubric["institutional_score"] <= 10.0
    assert rubric["max_raw_score"] == 20.0

    # 2. Feedback Validation (Scenario 4)
    feedback = data["feedback"]
    assert "overall_feedback" in feedback
    assert len(feedback["overall_feedback"]) > 20
    assert 2 <= len(feedback["strengths"]) <= 4
    assert 2 <= len(feedback["areas_for_improvement"]) <= 4
    assert len(feedback["actionable_tips"]) == 3

    # 3. AI Detection metrics
    ai_det = data["ai_detection"]
    assert "probability" in ai_det
    assert ai_det["is_likely_ai"] is False
    assert ai_det["confidence"] in ["LOW", "MEDIUM", "HIGH"]
    assert "execution_time_seconds" in data


@pytest.mark.asyncio
async def test_evaluate_length_penalty_scenario(
    async_client: AsyncClient,
) -> None:
    """Scenario 5: Detección de Penalización por Conteo de Palabras.

    Given: Writing configurado con rango [140, 190] palabras y texto con ~100 palabras.
    When: POST /internal/v1/evaluate.
    Then: rubric_evaluation.length_penalty es true y word_count_status es TOO_SHORT.
    """
    short_text = " ".join(["word"] * 100)
    payload = {
        "submission_id": "test-sub-length-penalty",
        "student_text": short_text,
        "task_prompt": "Write an essay discussing environmental sustainability.",
        "level": "B2",
        "text_type": "essay",
        "min_words": 140,
        "max_words": 190,
    }

    response = await async_client.post("/internal/v1/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()

    rubric = data["rubric_evaluation"]
    assert rubric["length_penalty"] is True
    assert rubric["word_count_status"] == "TOO_SHORT"


@pytest.mark.asyncio
async def test_evaluate_normal_word_count(
    async_client: AsyncClient,
) -> None:
    """Verify normal word count evaluation without length penalty."""
    normal_text = " ".join(["word"] * 160)
    payload = {
        "submission_id": "test-sub-normal-length",
        "student_text": normal_text,
        "task_prompt": "Write an essay discussing remote education benefits.",
        "level": "B2",
        "text_type": "essay",
        "min_words": 140,
        "max_words": 190,
    }

    response = await async_client.post("/internal/v1/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()

    rubric = data["rubric_evaluation"]
    assert rubric["length_penalty"] is False
    assert rubric["word_count_status"] == "NORMAL"


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
