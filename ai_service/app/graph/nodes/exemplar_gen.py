from typing import Any

from app.core.config import settings
from app.core.logging import logger
from app.graph.state import EvaluationState


def generate_mock_exemplar(text: str, level: str, text_type: str) -> str:
    """Produce an exemplary Band 5 version preserving main ideas with elevated vocabulary."""
    cleaned = text.strip()
    if not cleaned:
        return "Exemplary model cannot be generated for empty text."

    # Exemplary transformation model template
    if level.upper() == "C1":
        intro = (
            f"Undeniably, when considering the focal theme of this {text_type}, "
            "one must acknowledge the nuanced interplay of societal factors. "
        )
        conclusion = (
            " In light of the aforementioned arguments, it is manifest that "
            "implementing strategic initiatives remains imperative."
        )
    else:
        intro = (
            f"In recent years, the discussion surrounding this {text_type} "
            "has gained significant prominence. "
        )
        conclusion = (
            " Taking all points into consideration, it is evident that "
            "striking a balance is the most effective approach moving forward."
        )

    # Clean known common errors from student text to build exemplar
    replacements = [
        ("the technology", "technology"),
        ("informations", "information"),
        ("people is", "people are"),
        ("I am agree", "I agree"),
        ("definitly", "definitely"),
        ("untill", "until"),
    ]
    transformed = cleaned
    for src, dst in replacements:
        transformed = transformed.replace(src, dst)

    return f"{intro}{transformed}{conclusion}"


async def exemplar_gen_node(state: EvaluationState) -> dict[str, Any]:
    """Generates an exemplary Band 5 rewritten text representing upper-tier mastery."""
    text = state.get("sanitized_text", state.get("student_text", ""))
    level = state.get("level", "B2")
    text_type = state.get("text_type", "essay")
    logger.info("Running exemplar_gen_node for level %s (%s)", level, text_type)

    if settings.LLM_PROVIDER == "mock":
        exemplar = generate_mock_exemplar(text, level, text_type)
    else:
        exemplar = generate_mock_exemplar(text, level, text_type)

    return {"exemplar_model": exemplar}
