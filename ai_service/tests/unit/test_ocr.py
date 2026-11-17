"""Unit tests for multimodal OCR transcription node and Literal OCR Principle."""

import pytest

from app.core.image_processing import encode_image_to_base64
from app.graph.nodes.ocr_transcription import ocr_transcription_node
from app.graph.state import EvaluationState
from tests.unit.test_image_processing import create_dummy_image


@pytest.mark.asyncio
async def test_ocr_node_digital_submission_bypasses_ocr() -> None:
    state: EvaluationState = {
        "submission_id": "test-dig-01",
        "student_text": "This is a direct digital submission text without any image attached.",
    }
    result = await ocr_transcription_node(state)

    assert result["ocr_applied"] is False
    assert result["extracted_text"] == state["student_text"]
    assert result["ocr_confidence"] == 1.0
    assert result["word_count"] == len(state["student_text"].split())


@pytest.mark.asyncio
async def test_ocr_node_handwritten_image_performs_literal_ocr() -> None:
    dummy_img = create_dummy_image("PNG")
    b64_img = encode_image_to_base64(dummy_img)

    state: EvaluationState = {
        "submission_id": "test-img-01",
        "image_base64": b64_img,
        "student_text": "Nowadays remote working is popular everyday. Working from home have many positive aspects.",
    }
    result = await ocr_transcription_node(state)

    assert result["ocr_applied"] is True
    assert result["ocr_confidence"] > 0.90
    assert len(result["extracted_text"]) > 0
    # Verifies literal transcription preserved the spelling/grammar slips
    assert "everyday" in result["extracted_text"]
    assert "have many" in result["extracted_text"]


@pytest.mark.asyncio
async def test_ocr_node_fallback_when_student_text_empty_and_mock() -> None:
    dummy_img = create_dummy_image("JPEG")
    b64_img = encode_image_to_base64(dummy_img)

    state: EvaluationState = {
        "submission_id": "test-img-02",
        "image_base64": b64_img,
        "student_text": "",
    }
    result = await ocr_transcription_node(state)

    assert result["ocr_applied"] is True
    assert len(result["extracted_text"]) > 50
    assert result["word_count"] > 10
