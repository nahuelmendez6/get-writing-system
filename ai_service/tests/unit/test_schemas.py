from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.health import HealthCheckResponse
from app.schemas.request import EvaluationRequest
from app.schemas.response import (
    AIDetectionResult,
    CriterionEvaluation,
    EvaluationResponse,
    MistakeAnnotation,
    PedagogicalFeedback,
    RubricEvaluation,
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


def test_criterion_evaluation_schema() -> None:
    criterion = CriterionEvaluation(
        name="Content",
        score=4.0,
        max_score=5.0,
        band_descriptor="All content is relevant to the task.",
        justification="Evidencia textual adecuada.",
    )
    assert criterion.score == 4.0
    assert criterion.max_score == 5.0

    # Bounds validation
    with pytest.raises(ValidationError):
        CriterionEvaluation(
            name="Content",
            score=6.0,  # exceeds max 5.0
            max_score=5.0,
            band_descriptor="Descriptor",
            justification="Justification",
        )


def test_rubric_evaluation_schema() -> None:
    criteria = [
        CriterionEvaluation(
            name="Content",
            score=4.0,
            band_descriptor="Descriptor",
            justification="Justification",
        ),
        CriterionEvaluation(
            name="Communicative Achievement",
            score=4.0,
            band_descriptor="Descriptor",
            justification="Justification",
        ),
        CriterionEvaluation(
            name="Organisation",
            score=4.0,
            band_descriptor="Descriptor",
            justification="Justification",
        ),
        CriterionEvaluation(
            name="Language",
            score=4.0,
            band_descriptor="Descriptor",
            justification="Justification",
        ),
    ]
    rubric = RubricEvaluation(
        criteria=criteria,
        raw_score=16.0,
        max_raw_score=20.0,
        institutional_score=8.0,
        length_penalty=False,
        word_count_status="NORMAL",
    )
    assert rubric.raw_score == 16.0
    assert rubric.institutional_score == 8.0
    assert rubric.length_penalty is False


def test_pedagogical_feedback_schema() -> None:
    feedback = PedagogicalFeedback(
        overall_feedback="Buen trabajo general.",
        strengths=["Coherencia textual", "Registro adecuado"],
        areas_for_improvement=["Mayor precisión gramatical", "Ampliar conectores"],
        actionable_tips=["Tip 1", "Tip 2", "Tip 3"],
    )
    assert len(feedback.strengths) == 2
    assert len(feedback.actionable_tips) == 3


def test_evaluation_response_schema() -> None:
    res = EvaluationResponse(
        submission_id="sub-101",
        word_count=120,
        mistakes=[],
        exemplar_model="Exemplary text",
        rubric_evaluation=RubricEvaluation(
            criteria=[
                CriterionEvaluation(
                    name="Content",
                    score=4.0,
                    band_descriptor="Descriptor",
                    justification="Justification",
                )
            ],
            raw_score=4.0,
            max_raw_score=20.0,
            institutional_score=2.0,
            length_penalty=False,
            word_count_status="NORMAL",
        ),
        feedback=PedagogicalFeedback(
            overall_feedback="Buen trabajo.",
            strengths=["Fortaleza 1", "Fortaleza 2"],
            areas_for_improvement=["Mejora 1", "Mejora 2"],
            actionable_tips=["Tip 1", "Tip 2", "Tip 3"],
        ),
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
    assert res.rubric_evaluation.raw_score == 4.0
    assert len(res.feedback.actionable_tips) == 3


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
