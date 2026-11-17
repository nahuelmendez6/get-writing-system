from typing import Any

from app.core.config import settings
from app.core.logging import logger
from app.graph.state import EvaluationState


def generate_feedback_deterministic(
    level: str,
    text_type: str,
    rubric_eval: dict[str, Any],
    mistakes: list[dict[str, Any]],
) -> dict[str, Any]:
    """Generates structured pedagogical feedback in Spanish based on rubric and mistake results."""
    institutional_score = rubric_eval.get("institutional_score", 7.0)
    length_penalty = rubric_eval.get("length_penalty", False)
    word_count_status = rubric_eval.get("word_count_status", "NORMAL")

    # 1. Overall feedback synthesis
    if institutional_score >= 8.0:
        overall_feedback = (
            f"Excelente desempeño general para el nivel {level}. Tu redacción demuestra "
            f"un dominio sólido del formato {text_type}, cumpliendo de forma eficaz "
            "con los objetivos comunicativos y manteniendo un registro apropiado."
        )
    elif institutional_score >= 6.0:
        overall_feedback = (
            f"Buen desempeño acorde a las expectativas del nivel {level}. El texto "
            f"comunica las ideas centrales del {text_type} con claridad, aunque "
            "se beneficiará de mayor precisión léxica y variedad en las estructuras complejas."
        )
    else:
        overall_feedback = (
            f"La redacción se encuentra por debajo del umbral de suficiencia para el nivel {level}. "
            "Es necesario reforzar el control gramatical, la coherencia entre párrafos y "
            "el cumplimiento exhaustivo de las instrucciones de la consigna."
        )

    # 2. Strengths (2 to 4 items)
    strengths: list[str] = [
        f"Adecuación al registro y convenciones formales del formato {text_type}.",
        "Desarrollo coherente de los argumentos principales orientados al lector meta.",
    ]
    if len(mistakes) <= 3:
        strengths.append("Buen control general de la ortografía y puntuación.")
    if not length_penalty:
        strengths.append(
            "Excelente gestión de la extensión ajustada a los límites requeridos."
        )

    # Ensure between 2 and 4 items
    strengths = strengths[:4]

    # 3. Areas for improvement (2 to 4 items)
    areas_for_improvement: list[str] = []
    if length_penalty:
        if word_count_status == "TOO_SHORT":
            areas_for_improvement.append(
                "Extensión insuficiente: Desarrollar con mayor profundidad cada punto de la consigna."
            )
        else:
            areas_for_improvement.append(
                "Exceso de palabras: Sintetizar las ideas para evitar redundancias y ajustarse al límite."
            )

    if mistakes:
        categories = {m.get("category", "grammar") for m in mistakes}
        if "grammar" in categories:
            areas_for_improvement.append(
                "Precisión gramatical: Revisar la concordancia sujeto-verbo y el uso de tiempos verbales."
            )
        if "vocabulary" in categories:
            areas_for_improvement.append(
                "Rango léxico: Evitar repeticiones incorporando colocaciones y sinónimos más avanzados."
            )
        if "spelling" in categories and len(areas_for_improvement) < 4:
            areas_for_improvement.append(
                "Ortografía: Prestar atención a palabras de grafía dudosa y falsos amigos comunes."
            )

    if len(areas_for_improvement) < 2:
        areas_for_improvement.append(
            "Uso de conectores: Incorporar una gama más variada de conectores discursivos (e.g. Furthermore, However)."
        )
    if len(areas_for_improvement) < 2:
        areas_for_improvement.append(
            "Párrafos balanceados: Asegurar que cada párrafo desarrolle una única idea central con su justificación."
        )

    areas_for_improvement = areas_for_improvement[:4]

    # 4. Actionable tips (exactly 3 items)
    actionable_tips: list[str] = [
        (
            "Planifica tu escritura en 3 fases: 5 minutos de lluvia de ideas y estructura, "
            "tiempo de redacción enfocado, y 5 minutos finales para auto-corregir."
        ),
        (
            f"Practica la incorporación de al menos 3 estructuras avanzadas de nivel {level} "
            "(como condicionales mixtos, inversiones o cláusulas relativas explicativas)."
        ),
        (
            "Crea un glosario personal con los errores recurrentes detectados en este feedback "
            "para repasarlo antes de redactar tu próxima entrega."
        ),
    ]

    return {
        "overall_feedback": overall_feedback,
        "strengths": strengths,
        "areas_for_improvement": areas_for_improvement,
        "actionable_tips": actionable_tips,
    }


async def feedback_gen_node(state: EvaluationState) -> dict[str, Any]:
    """Generates structured pedagogical feedback in Spanish tailored to the student."""
    level = state.get("level", "B2")
    text_type = state.get("text_type", "essay")
    rubric_eval = state.get("rubric_evaluation", {})
    mistakes = state.get("mistakes", [])

    logger.info(
        "Running feedback_gen_node for submission %s (level=%s, type=%s)",
        state.get("submission_id"),
        level,
        text_type,
    )

    if settings.LLM_PROVIDER == "mock":
        feedback_data = generate_feedback_deterministic(
            level=level,
            text_type=text_type,
            rubric_eval=rubric_eval,
            mistakes=mistakes,
        )
    else:
        # LLM inference integration
        feedback_data = generate_feedback_deterministic(
            level=level,
            text_type=text_type,
            rubric_eval=rubric_eval,
            mistakes=mistakes,
        )

    return {"feedback": feedback_data}
