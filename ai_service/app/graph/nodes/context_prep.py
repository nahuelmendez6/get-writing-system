import re
from typing import Any

from app.core.config import settings
from app.core.sanitizer import PIISanitizer
from app.graph.prompts.templates import get_level_guidelines
from app.graph.state import EvaluationState


def count_words(text: str) -> int:
    """Accurately count words in a writing text."""
    words = re.findall(r"\b[\w'-]+\b", text)
    return len(words)


def sanitize_pii(text: str) -> str:
    """Mask student PII including emails, phones, IDs, and personal names."""
    return PIISanitizer.sanitize(text).clean_text


async def context_prep_node(state: EvaluationState) -> dict[str, Any]:
    """Prepares the evaluation context, calculates word count, and enforces ZDR PII sanitization."""
    raw_text = state.get("student_text", "")
    sanitization_res = PIISanitizer.sanitize(raw_text)
    words = count_words(raw_text)
    level = state.get("level", "B2")

    return {
        "sanitized_text": sanitization_res.clean_text,
        "sanitized_pii_count": sanitization_res.pii_detected_count,
        "pii_types_detected": sanitization_res.pii_types,
        "zdr_enforced": settings.ENFORCE_ZDR,
        "word_count": words,
        "context_guidelines": get_level_guidelines(level),
        "retry_count": state.get("retry_count", 0),
        "errors": state.get("errors", []),
    }
