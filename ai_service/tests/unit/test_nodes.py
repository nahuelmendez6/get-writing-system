import pytest
from langgraph.graph import END

from app.graph.nodes.ai_detector import ai_detector_node
from app.graph.nodes.context_prep import context_prep_node, count_words, sanitize_pii
from app.graph.nodes.exemplar_gen import exemplar_gen_node
from app.graph.nodes.feedback_gen import feedback_gen_node
from app.graph.nodes.rubric_eval import check_length_penalty, rubric_eval_node
from app.graph.nodes.validator import validator_node
from app.graph.nodes.writing_analysis import writing_analysis_node
from app.graph.pipeline import should_continue_or_retry
from app.graph.state import EvaluationState


def test_sanitize_pii() -> None:
    raw = "My email is student.doe@example.com and phone is +1-555-123-4567. Thanks."
    sanitized = sanitize_pii(raw)
    assert "student.doe@example.com" not in sanitized
    assert "[EMAIL_REDACTED]" in sanitized
    assert "+1-555-123-4567" not in sanitized
    assert "[PHONE_REDACTED]" in sanitized


def test_count_words() -> None:
    text = "Hello, this is a 7-word test sentence!"
    assert count_words(text) == 7


def test_check_length_penalty_boundaries() -> None:
    # Target 140 - 190. Tolerance 10%: min 126, max 209
    assert check_length_penalty(100, 140, 190) == (True, "TOO_SHORT")
    assert check_length_penalty(125, 140, 190) == (True, "TOO_SHORT")
    assert check_length_penalty(126, 140, 190) == (False, "NORMAL")
    assert check_length_penalty(160, 140, 190) == (False, "NORMAL")
    assert check_length_penalty(209, 140, 190) == (False, "NORMAL")
    assert check_length_penalty(210, 140, 190) == (True, "TOO_LONG")
    assert check_length_penalty(250, 140, 190) == (True, "TOO_LONG")

    # None boundaries
    assert check_length_penalty(150, None, None) == (False, "NORMAL")


@pytest.mark.asyncio
async def test_context_prep_node() -> None:
    state: EvaluationState = {
        "student_text": "Contact me at user@school.edu for information.",
        "level": "B2",
    }
    result = await context_prep_node(state)
    assert result["word_count"] == 8
    assert "[EMAIL_REDACTED]" in result["sanitized_text"]
    assert "context_guidelines" in result


@pytest.mark.asyncio
async def test_writing_analysis_node_finds_mistakes() -> None:
    text = "Many people is using the technology every day."
    state: EvaluationState = {"sanitized_text": text}
    result = await writing_analysis_node(state)
    mistakes = result["mistakes"]
    assert len(mistakes) >= 2

    # Verify character offsets match original substrings
    for m in mistakes:
        start = m["start_index"]
        end = m["end_index"]
        assert text[start:end] == m["quote"]


@pytest.mark.asyncio
async def test_exemplar_gen_node() -> None:
    state: EvaluationState = {
        "sanitized_text": "Technology is great.",
        "level": "C1",
        "text_type": "essay",
    }
    result = await exemplar_gen_node(state)
    exemplar = result["exemplar_model"]
    assert "essay" in exemplar
    assert len(exemplar) > 30


@pytest.mark.asyncio
async def test_rubric_eval_node_b2_normal_length() -> None:
    """Verify B2 rubric evaluation with 4 criteria and institutional score."""
    state: EvaluationState = {
        "submission_id": "sub-10",
        "sanitized_text": (
            "In recent years technology has revolutionized how people communicate. "
            "Firstly, it allows instant connectivity across the globe. "
            "Secondly, it enhances educational opportunities for everyone. "
            "In conclusion, technology brings immense benefits to modern society."
        ),
        "level": "B2",
        "text_type": "essay",
        "word_count": 160,
        "min_words": 140,
        "max_words": 190,
        "mistakes": [],
    }
    result = await rubric_eval_node(state)
    rubric = result["rubric_evaluation"]

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
    assert rubric["length_penalty"] is False
    assert rubric["word_count_status"] == "NORMAL"


@pytest.mark.asyncio
async def test_rubric_eval_node_length_penalty_too_short() -> None:
    """Scenario 5: Detección de Penalización por Conteo de Palabras (< -10%)."""
    state: EvaluationState = {
        "submission_id": "sub-11",
        "sanitized_text": "Short essay with only few words.",
        "level": "B2",
        "text_type": "essay",
        "word_count": 100,
        "min_words": 140,
        "max_words": 190,
        "mistakes": [],
    }
    result = await rubric_eval_node(state)
    rubric = result["rubric_evaluation"]

    assert rubric["length_penalty"] is True
    assert rubric["word_count_status"] == "TOO_SHORT"
    # Content score reflects the penalty
    content_criterion = next(c for c in rubric["criteria"] if c["name"] == "Content")
    assert content_criterion["score"] < 4.0
    assert "por debajo del límite mínimo" in content_criterion["justification"]


@pytest.mark.asyncio
async def test_feedback_gen_node_structure() -> None:
    """Scenario 4: Generación Estructurada de Feedback Pedagógico."""
    rubric_eval = {
        "criteria": [],
        "raw_score": 15.0,
        "max_raw_score": 20.0,
        "institutional_score": 7.5,
        "length_penalty": False,
        "word_count_status": "NORMAL",
    }
    state: EvaluationState = {
        "submission_id": "sub-12",
        "level": "B2",
        "text_type": "article",
        "rubric_evaluation": rubric_eval,
        "mistakes": [
            {
                "category": "grammar",
                "explanation": "Verb agreement error",
            }
        ],
    }
    result = await feedback_gen_node(state)
    feedback = result["feedback"]

    assert "overall_feedback" in feedback
    assert len(feedback["overall_feedback"]) > 20
    assert 2 <= len(feedback["strengths"]) <= 4
    assert 2 <= len(feedback["areas_for_improvement"]) <= 4
    assert len(feedback["actionable_tips"]) == 3


@pytest.mark.asyncio
async def test_ai_detector_node_natural_vs_synthetic() -> None:
    # 1. Natural student text
    natural_state: EvaluationState = {
        "sanitized_text": "I think that watching movies helps learn English better."
    }
    natural_res = await ai_detector_node(natural_state)
    assert natural_res["ai_detection"]["is_likely_ai"] is False
    assert natural_res["ai_detection"]["probability"] < 0.50

    # 2. Synthetic text with markers
    synthetic_state: EvaluationState = {
        "sanitized_text": (
            "In the contemporary era, education plays a pivotal role in the tapestry of society. "
            "In conclusion, it is vital to acknowledge this paradigm."
        )
    }
    synthetic_res = await ai_detector_node(synthetic_state)
    assert synthetic_res["ai_detection"]["is_likely_ai"] is True
    assert synthetic_res["ai_detection"]["probability"] >= 0.70


@pytest.mark.asyncio
async def test_validator_node_success_and_retry() -> None:
    # 1. Valid state
    valid_state: EvaluationState = {
        "submission_id": "sub-1",
        "mistakes": [
            {
                "id": "err-1",
                "start_index": 0,
                "end_index": 4,
                "quote": "text",
                "correction": "Text",
                "category": "spelling",
                "explanation": "Capital letter needed",
            }
        ],
        "exemplar_model": "Valid Band 5 text model.",
        "rubric_evaluation": {
            "criteria": [
                {
                    "name": "Content",
                    "score": 4.0,
                    "max_score": 5.0,
                    "band_descriptor": "Descriptor",
                    "justification": "Justification",
                },
                {
                    "name": "Communicative Achievement",
                    "score": 4.0,
                    "max_score": 5.0,
                    "band_descriptor": "Descriptor",
                    "justification": "Justification",
                },
                {
                    "name": "Organisation",
                    "score": 4.0,
                    "max_score": 5.0,
                    "band_descriptor": "Descriptor",
                    "justification": "Justification",
                },
                {
                    "name": "Language",
                    "score": 4.0,
                    "max_score": 5.0,
                    "band_descriptor": "Descriptor",
                    "justification": "Justification",
                },
            ],
            "raw_score": 16.0,
            "max_raw_score": 20.0,
            "institutional_score": 8.0,
            "length_penalty": False,
            "word_count_status": "NORMAL",
        },
        "feedback": {
            "overall_feedback": "General feedback.",
            "strengths": ["Strength 1", "Strength 2"],
            "areas_for_improvement": ["Area 1", "Area 2"],
            "actionable_tips": ["Tip 1", "Tip 2", "Tip 3"],
        },
        "ai_detection": {
            "probability": 0.2,
            "is_likely_ai": False,
            "confidence": "HIGH",
            "rationale": "Natural",
        },
        "retry_count": 0,
    }
    res_valid = await validator_node(valid_state)
    assert res_valid["validation_passed"] is True
    assert should_continue_or_retry(res_valid) == END

    # 2. Invalid state with retry available
    invalid_state: EvaluationState = {
        "submission_id": "sub-2",
        "mistakes": [{"invalid_key": 123}],  # Malformed
        "exemplar_model": "",
        "retry_count": 0,
    }
    res_retry = await validator_node(invalid_state)
    assert res_retry["validation_passed"] is False
    assert res_retry["retry_count"] == 1
    assert should_continue_or_retry(res_retry) == "writing_analysis"
