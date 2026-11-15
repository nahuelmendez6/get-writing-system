from typing import Any

from app.core.logging import logger
from app.graph.state import EvaluationState
from app.schemas.response import AIDetectionResult, MistakeAnnotation


async def validator_node(state: EvaluationState) -> dict[str, Any]:
    """Validates the generated state against strict Pydantic schemas and controls retry logic."""
    errors: list[str] = list(state.get("errors", []))
    retry_count = state.get("retry_count", 0)

    # 1. Validate mistakes list
    mistakes_raw = state.get("mistakes", [])
    valid_mistakes: list[dict[str, Any]] = []
    for item in mistakes_raw:
        try:
            validated_item = MistakeAnnotation.model_validate(item)
            valid_mistakes.append(validated_item.model_dump())
        except Exception as e:
            errors.append(f"Mistake validation error: {e}")

    # 2. Validate AI detection structure
    ai_raw = state.get("ai_detection", {})
    try:
        validated_ai = AIDetectionResult.model_validate(ai_raw)
        valid_ai_dict = validated_ai.model_dump()
    except Exception as e:
        errors.append(f"AI Detection validation error: {e}")
        valid_ai_dict = {
            "probability": 0.0,
            "is_likely_ai": False,
            "confidence": "LOW",
            "rationale": "Evaluación por defecto tras fallo de validación.",
        }

    # 3. Validate exemplar model
    exemplar = state.get("exemplar_model", "").strip()
    if not exemplar:
        errors.append("Exemplar model was empty.")

    # Determine if validation passed
    has_critical_error = bool(errors and len(valid_mistakes) != len(mistakes_raw))
    if not has_critical_error and exemplar:
        logger.info(
            "Validation successful for submission %s", state.get("submission_id")
        )
        return {
            "mistakes": valid_mistakes,
            "ai_detection": valid_ai_dict,
            "exemplar_model": exemplar,
            "validation_passed": True,
            "status": "SUCCESS",
            "errors": errors,
        }

    # If critical errors occurred and we have remaining retries
    if retry_count < 2:
        logger.warning(
            "Validation failed, triggering retry %d for submission %s: %s",
            retry_count + 1,
            state.get("submission_id"),
            errors,
        )
        return {
            "validation_passed": False,
            "retry_count": retry_count + 1,
            "errors": errors,
        }

    # Max retries reached: fallback gracefully
    logger.error(
        "Max retries reached for submission %s. Proceeding with best-effort results.",
        state.get("submission_id"),
    )
    return {
        "mistakes": valid_mistakes,
        "ai_detection": valid_ai_dict,
        "exemplar_model": exemplar or "Modelo ejemplar no disponible.",
        "validation_passed": True,
        "status": "SUCCESS",
        "errors": errors,
    }
