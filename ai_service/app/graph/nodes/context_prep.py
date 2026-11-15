import re
from typing import Any

from app.core.config import settings
from app.graph.prompts.templates import get_level_guidelines
from app.graph.state import EvaluationState


def sanitize_pii(text: str) -> str:
    """Mask student PII including emails and phone numbers."""
    if not settings.SANITIZE_PII:
        return text

    # Email sanitization
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    sanitized = re.sub(email_pattern, "[EMAIL_REDACTED]", text)

    # Phone / ID pattern sanitization
    phone_pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    sanitized = re.sub(phone_pattern, "[PHONE_REDACTED]", sanitized)

    return sanitized


def count_words(text: str) -> int:
    """Accurately count words in a writing text."""
    words = re.findall(r"\b[\w'-]+\b", text)
    return len(words)


async def context_prep_node(state: EvaluationState) -> dict[str, Any]:
    """Prepares the evaluation context, calculates word count, and enforces ZDR PII sanitization."""
    raw_text = state.get("student_text", "")
    sanitized = sanitize_pii(raw_text)
    words = count_words(raw_text)
    level = state.get("level", "B2")

    return {
        "sanitized_text": sanitized,
        "word_count": words,
        "context_guidelines": get_level_guidelines(level),
        "retry_count": state.get("retry_count", 0),
        "errors": state.get("errors", []),
    }
