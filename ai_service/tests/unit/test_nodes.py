import pytest
from langgraph.graph import END

from app.graph.nodes.ai_detector import ai_detector_node
from app.graph.nodes.context_prep import context_prep_node, count_words, sanitize_pii
from app.graph.nodes.exemplar_gen import exemplar_gen_node
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
