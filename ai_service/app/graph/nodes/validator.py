from typing import Any

from app.core.logging import logger
from app.graph.state import EvaluationState
from app.schemas.response import (
    AIDetectionResult,
    MistakeAnnotation,
    PedagogicalFeedback,
    RubricEvaluation,
)


def _default_rubric_evaluation() -> dict[str, Any]:
    """Default valid rubric evaluation structure when validation fails permanently."""
    return {
        "criteria": [
            {
                "name": "Content",
                "score": 3.0,
                "max_score": 5.0,
                "band_descriptor": (
                    "Minor irrelevances and/or omissions may be present. "
                    "Target reader is on the whole informed."
                ),
                "justification": "Evaluación predeterminada asignada por el sistema.",
            },
            {
                "name": "Communicative Achievement",
                "score": 3.0,
                "max_score": 5.0,
                "band_descriptor": (
                    "Uses the conventions of the communicative task to hold the "
                    "target reader's attention and communicate straightforward ideas."
                ),
                "justification": "Evaluación predeterminada asignada por el sistema.",
            },
            {
                "name": "Organisation",
                "score": 3.0,
                "max_score": 5.0,
                "band_descriptor": (
                    "Text is generally well-organised and coherent, using a variety "
                    "of linking words and cohesive devices."
                ),
                "justification": "Evaluación predeterminada asignada por el sistema.",
            },
            {
                "name": "Language",
                "score": 3.0,
                "max_score": 5.0,
                "band_descriptor": (
                    "Uses everyday vocabulary appropriately, with occasional "
                    "inappropriate choice of less common lexis."
                ),
                "justification": "Evaluación predeterminada asignada por el sistema.",
            },
        ],
        "raw_score": 12.0,
        "max_raw_score": 20.0,
        "institutional_score": 6.0,
        "length_penalty": False,
        "word_count_status": "NORMAL",
    }


def _default_feedback() -> dict[str, Any]:
    """Default valid pedagogical feedback structure when validation fails permanently."""
    return {
        "overall_feedback": (
            "Se completó la evaluación general del texto. Se recomienda revisar "
            "los comentarios específicos de cada criterio para continuar mejorando."
        ),
        "strengths": [
            "Cumplimiento del propósito comunicativo general.",
            "Estructuración comprensible del texto.",
        ],
        "areas_for_improvement": [
            "Revisar la precisión gramatical y ortográfica.",
            "Ampliar la variedad de conectores y recursos cohesivos.",
        ],
        "actionable_tips": [
            "Planifica un esquema de ideas antes de comenzar a redactar.",
            "Dedica los últimos minutos a revisar errores comunes de concordancia.",
            "Consulta modelos ejemplares para observar estructuras avanzadas.",
        ],
    }


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

    # 4. Validate Rubric Evaluation
    rubric_raw = state.get("rubric_evaluation", {})
    valid_rubric_dict: dict[str, Any]
    try:
        validated_rubric = RubricEvaluation.model_validate(rubric_raw)
        # Verify exactly 4 criteria are present
        if len(validated_rubric.criteria) != 4:
            raise ValueError(
                f"Expected 4 criteria, found {len(validated_rubric.criteria)}"
            )
        valid_rubric_dict = validated_rubric.model_dump()
    except Exception as e:
        errors.append(f"Rubric evaluation validation error: {e}")
        valid_rubric_dict = _default_rubric_evaluation()

    # 5. Validate Pedagogical Feedback
    feedback_raw = state.get("feedback", {})
    valid_feedback_dict: dict[str, Any]
    try:
        validated_feedback = PedagogicalFeedback.model_validate(feedback_raw)
        if len(validated_feedback.actionable_tips) != 3:
            raise ValueError(
                f"Expected 3 actionable tips, found {len(validated_feedback.actionable_tips)}"
            )
        valid_feedback_dict = validated_feedback.model_dump()
    except Exception as e:
        errors.append(f"Pedagogical feedback validation error: {e}")
        valid_feedback_dict = _default_feedback()

    # Determine if validation passed
    has_critical_error = bool(
        errors
        and (
            len(valid_mistakes) != len(mistakes_raw)
            or not rubric_raw
            or not feedback_raw
        )
    )

    if not has_critical_error and exemplar:
        logger.info(
            "Validation successful for submission %s", state.get("submission_id")
        )
        return {
            "mistakes": valid_mistakes,
            "ai_detection": valid_ai_dict,
            "exemplar_model": exemplar,
            "rubric_evaluation": valid_rubric_dict,
            "feedback": valid_feedback_dict,
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
        "rubric_evaluation": valid_rubric_dict,
        "feedback": valid_feedback_dict,
        "validation_passed": True,
        "status": "SUCCESS",
        "errors": errors,
    }
