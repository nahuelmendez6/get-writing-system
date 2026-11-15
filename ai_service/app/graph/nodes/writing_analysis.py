import re
from typing import Any

from app.core.config import settings
from app.core.logging import logger
from app.graph.state import EvaluationState


def mock_analyze_writing(text: str) -> list[dict[str, Any]]:
    """Deterministic rule-based mistake detection for development and mock mode."""
    mistakes: list[dict[str, Any]] = []

    patterns: list[tuple[str, str, str, str]] = [
        (
            r"\bthe technology\b",
            "technology",
            "grammar",
            "El sustantivo 'technology' en sentido general no requiere artículo determinado.",
        ),
        (
            r"\binformations\b",
            "information",
            "vocabulary",
            "'Information' es un sustantivo incontable en inglés y no tiene forma plural.",
        ),
        (
            r"\bpeople is\b",
            "people are",
            "grammar",
            "'People' es un sustantivo plural y requiere el verbo en plural 'are'.",
        ),
        (
            r"\bI am agree\b",
            "I agree",
            "grammar",
            "En inglés 'agree' es un verbo, por lo que se dice 'I agree' y no 'I am agree'.",
        ),
        (
            r"\bdefinitly\b",
            "definitely",
            "spelling",
            "Error ortográfico común: se escribe 'definitely' con 'i'.",
        ),
        (
            r"\buntill\b",
            "until",
            "spelling",
            "Error ortográfico: 'until' se escribe con una sola 'l'.",
        ),
    ]

    err_count = 1
    for pat, corr, cat, expl in patterns:
        for match in re.finditer(pat, text, re.IGNORECASE):
            mistakes.append(
                {
                    "id": f"err-{err_count}",
                    "start_index": match.start(),
                    "end_index": match.end(),
                    "quote": match.group(),
                    "correction": corr,
                    "category": cat,
                    "explanation": expl,
                }
            )
            err_count += 1

    return mistakes


async def writing_analysis_node(state: EvaluationState) -> dict[str, Any]:
    """Analyzes student text identifying orthographic, grammatical, and lexical errors."""
    text = state.get("sanitized_text", state.get("student_text", ""))
    logger.info(
        "Running writing_analysis_node for submission %s", state.get("submission_id")
    )

    if settings.LLM_PROVIDER == "mock":
        mistakes = mock_analyze_writing(text)
    else:
        # LLM integration point
        mistakes = mock_analyze_writing(text)

    return {"mistakes": mistakes}
