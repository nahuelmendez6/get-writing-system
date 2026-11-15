from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.health import HealthCheckResponse
from app.schemas.request import EvaluationRequest
from app.schemas.response import (
    AIDetectionResult,
    EvaluationResponse,
    MistakeAnnotation,
)


def test_valid_evaluation_request() -> None:
    req = EvaluationRequest(
        submission_id="sub-101",
        student_text="Valid English text submitted by candidate.",
        task_prompt="Write an essay.",
        level="B2",
        text_type="essay",
    )
    assert req.level == "B2"
    assert req.text_type == "essay"
    assert req.min_words is None


def test_invalid_level_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        EvaluationRequest(
            submission_id="sub-102",
            student_text="Some text",
            task_prompt="Prompt",
            level="X9",  # type: ignore[arg-type]
            text_type="essay",
        )


def test_empty_student_text_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        EvaluationRequest(
            submission_id="sub-103",
            student_text="",
            task_prompt="Prompt",
            level="B2",
            text_type="essay",
        )


def test_mistake_annotation_schema() -> None:
    mistake = MistakeAnnotation(
        id="err-1",
        start_index=5,
        end_index=15,
        quote="bad phrase",
        correction="good phrase",
        category="grammar",
        explanation="Explicación en español.",
    )
    assert mistake.category == "grammar"
    assert mistake.start_index == 5


def test_ai_detection_result_bounds() -> None:
    res = AIDetectionResult(
        probability=0.85,
        is_likely_ai=True,
        confidence="HIGH",
        rationale="Patrón sintético.",
    )
    assert res.probability == 0.85
    assert res.is_likely_ai is True

    # Test probability bounds
    with pytest.raises(ValidationError):
        AIDetectionResult(
            probability=1.5,
            is_likely_ai=True,
            confidence="HIGH",
            rationale="Out of bounds",
        )


def test_evaluation_response_schema() -> None:
    res = EvaluationResponse(
        submission_id="sub-101",
        word_count=120,
        mistakes=[],
        exemplar_model="Exemplary text",
        ai_detection=AIDetectionResult(
            probability=0.1,
            is_likely_ai=False,
            confidence="HIGH",
            rationale="Natural",
        ),
        status="SUCCESS",
        execution_time_seconds=1.25,
    )
    assert res.status == "SUCCESS"
    assert res.word_count == 120


def test_health_check_response_schema() -> None:
    health = HealthCheckResponse(
        status="healthy",
        service="ai_service",
        environment="development",
        version="0.1.0",
        zdr_enforced=True,
        timestamp=datetime.now(UTC),
    )
    assert health.zdr_enforced is True
    assert health.service == "ai_service"
