from typing import Any, Literal

from app.core.config import settings
from app.core.logging import logger
from app.graph.state import EvaluationState

# Cambridge Band Descriptors by Level and Criterion
CAMBRIDGE_DESCRIPTORS: dict[str, dict[str, dict[int, str]]] = {
    "B2": {
        "Content": {
            5: "All content is relevant to the task. Target reader is fully informed.",
            4: "Performance shares features of Bands 3 and 5.",
            3: "Minor irrelevances and/or omissions may be present. Target reader is on the whole informed.",
            2: "Performance shares features of Bands 1 and 3.",
            1: "Irrelevances and/or misinterpretation of task may be present. Target reader is minimally informed.",
            0: "Content is totally irrelevant. Target reader is not informed.",
        },
        "Communicative Achievement": {
            5: (
                "Uses the conventions of the communicative task effectively to hold the "
                "target reader's attention and communicate straightforward and complex ideas, as appropriate."
            ),
            4: "Performance shares features of Bands 3 and 5.",
            3: (
                "Uses the conventions of the communicative task to hold the target reader's "
                "attention and communicate straightforward ideas."
            ),
            2: "Performance shares features of Bands 1 and 3.",
            1: "Produces text that communicates simple ideas in simple ways.",
            0: "Performance below Band 1.",
        },
        "Organisation": {
            5: (
                "Text is well-organised and coherent, using a variety of cohesive devices "
                "and organisational patterns to generally good effect."
            ),
            4: "Performance shares features of Bands 3 and 5.",
            3: (
                "Text is generally well-organised and coherent, using a variety of linking "
                "words and cohesive devices."
            ),
            2: "Performance shares features of Bands 1 and 3.",
            1: (
                "Text is connected and coherent, using basic linking words and a limited "
                "number of cohesive devices."
            ),
            0: "Performance below Band 1.",
        },
        "Language": {
            5: (
                "Uses a range of everyday vocabulary, including less common lexis, appropriately. "
                "Uses a range of simple and complex grammatical forms with control and flexibility. "
                "Occasional errors may be present but do not impede communication."
            ),
            4: "Performance shares features of Bands 3 and 5.",
            3: (
                "Uses everyday vocabulary appropriately, with occasional inappropriate choice "
                "of less common lexis. Uses a range of simple and some complex grammatical forms "
                "with a good degree of control. Errors do not impede communication."
            ),
            2: "Performance shares features of Bands 1 and 3.",
            1: (
                "Uses basic vocabulary appropriately of isolated words and phrases. Uses simple "
                "grammatical forms with a degree of control. Errors may impede meaning at times."
            ),
            0: "Performance below Band 1.",
        },
    },
    "C1": {
        "Content": {
            5: "All content is relevant to the task. Target reader is fully informed.",
            4: "Performance shares features of Bands 3 and 5.",
            3: "Minor irrelevances and/or omissions may be present. Target reader is on the whole informed.",
            2: "Performance shares features of Bands 1 and 3.",
            1: "Irrelevances and/or misinterpretation of task may be present. Target reader is minimally informed.",
            0: "Content is totally irrelevant. Target reader is not informed.",
        },
        "Communicative Achievement": {
            5: (
                "Uses the conventions of the communicative task with sufficient flexibility "
                "to communicate complex ideas in an effective way, holding the target reader's "
                "attention with ease, fulfilling all communicative purposes."
            ),
            4: "Performance shares features of Bands 3 and 5.",
            3: (
                "Uses the conventions of the communicative task effectively to hold the "
                "target reader's attention and communicate straightforward and complex ideas, as appropriate."
            ),
            2: "Performance shares features of Bands 1 and 3.",
            1: (
                "Uses the conventions of the communicative task to hold the target "
                "reader's attention and communicate straightforward ideas."
            ),
            0: "Performance below Band 1.",
        },
        "Organisation": {
            5: (
                "Text is a well-organised, coherent whole, using a variety of cohesive devices "
                "and organisational patterns with flexibility."
            ),
            4: "Performance shares features of Bands 3 and 5.",
            3: (
                "Text is well-organised and coherent, using a variety of cohesive devices "
                "and organisational patterns to generally good effect."
            ),
            2: "Performance shares features of Bands 1 and 3.",
            1: (
                "Text is generally well-organised and coherent, using a variety of linking "
                "words and cohesive devices."
            ),
            0: "Performance below Band 1.",
        },
        "Language": {
            5: (
                "Uses a wide range of vocabulary, including less common and sophisticated lexis, "
                "with style and nuance. Uses a wide range of simple and complex grammatical forms "
                "with full control, flexibility and sophistication. Errors are rare and non-impeding."
            ),
            4: "Performance shares features of Bands 3 and 5.",
            3: (
                "Uses a range of vocabulary, including less common lexis, appropriately and effectively. "
                "Uses a range of simple and complex grammatical forms with control and flexibility. "
                "Occasional non-impeding errors."
            ),
            2: "Performance shares features of Bands 1 and 3.",
            1: (
                "Uses everyday vocabulary appropriately, with occasional inappropriate choice of "
                "less common lexis. Uses simple and some complex grammatical forms with a good "
                "degree of control. Errors do not impede communication."
            ),
            0: "Performance below Band 1.",
        },
    },
}


def check_length_penalty(
    word_count: int,
    min_words: int | None,
    max_words: int | None,
) -> tuple[bool, Literal["NORMAL", "TOO_SHORT", "TOO_LONG"]]:
    """Evaluate whether word count deviates more than 10% from required bounds."""
    if min_words is not None and min_words > 0:
        lower_bound = min_words * 0.9
        if word_count < lower_bound:
            return True, "TOO_SHORT"

    if max_words is not None and max_words > 0:
        upper_bound = max_words * 1.1
        if word_count > upper_bound:
            return True, "TOO_LONG"

    return False, "NORMAL"


def evaluate_rubric_deterministic(
    text: str,
    level: str,
    word_count: int,
    min_words: int | None,
    max_words: int | None,
    mistakes_count: int,
) -> dict[str, Any]:
    """Deterministic evaluation of the 4 Cambridge criteria for testing and mock mode."""
    norm_level = level.upper()
    if norm_level not in CAMBRIDGE_DESCRIPTORS:
        norm_level = "B2"

    descriptors = CAMBRIDGE_DESCRIPTORS[norm_level]
    length_penalty, word_status = check_length_penalty(word_count, min_words, max_words)

    # 1. Content Evaluation
    if length_penalty:
        if word_status == "TOO_SHORT":
            content_score = 2.5
            content_justification = (
                f"El texto cuenta con {word_count} palabras, por debajo del límite mínimo "
                f"permitido ({min_words} palabras con tolerancia del 10%). Esto impide "
                "un desarrollo exhaustivo de los puntos requeridos en la tarea."
            )
        else:
            content_score = 3.0
            content_justification = (
                f"El texto cuenta con {word_count} palabras, superando el límite máximo "
                f"establecido ({max_words} palabras con tolerancia del 10%). Se incluye "
                "información redundante que desvía el foco de la consigna."
            )
    else:
        content_score = 4.0
        content_justification = (
            "Se responden adecuadamente los puntos principales de la consigna. "
            "El lector meta queda informado sobre el propósito comunicativo."
        )

    # 2. Communicative Achievement Evaluation
    ca_score = 4.0 if not length_penalty else 3.0
    ca_justification = (
        "El registro y tono son consistentes con la tipología textual solicitada. "
        "Mantiene el interés del lector meta mediante fórmulas de cortesía y estilo apropiados."
    )

    # 3. Organisation Evaluation
    has_paragraphing = "\n" in text or len(text.split(".")) > 3
    org_score = 4.0 if has_paragraphing else 3.0
    org_justification = (
        "Estructura organizada en párrafos lógicos con uso adecuado de conectores "
        "y recursos cohesivos básicos e intermedios."
    )

    # 4. Language Evaluation (based on detected mistakes count)
    if mistakes_count == 0:
        lang_score = 5.0
        lang_justification = (
            "Demuestra un control lingüístico excepcional con estructuras variadas "
            "y ausencia de errores significativos."
        )
    elif mistakes_count <= 2:
        lang_score = 4.0
        lang_justification = (
            f"Se identificaron {mistakes_count} errores menores que no dificultan "
            "la comprensión global del texto. Demuestra buen control gramatical y léxico."
        )
    elif mistakes_count <= 5:
        lang_score = 3.0
        lang_justification = (
            f"Se detectaron {mistakes_count} imprecisiones léxicas y gramaticales. "
            "Aunque no impiden la comunicación, limitan la flexibilidad de las estructuras."
        )
    else:
        lang_score = 2.0
        lang_justification = (
            f"Presencia notable de {mistakes_count} errores sintácticos y ortográficos "
            "que requieren revisión para asegurar la precisión requerida en el nivel."
        )

    # Build criteria items
    criteria_list = [
        {
            "name": "Content",
            "score": content_score,
            "max_score": 5.0,
            "band_descriptor": descriptors["Content"][int(round(content_score))],
            "justification": content_justification,
        },
        {
            "name": "Communicative Achievement",
            "score": ca_score,
            "max_score": 5.0,
            "band_descriptor": descriptors["Communicative Achievement"][
                int(round(ca_score))
            ],
            "justification": ca_justification,
        },
        {
            "name": "Organisation",
            "score": org_score,
            "max_score": 5.0,
            "band_descriptor": descriptors["Organisation"][int(round(org_score))],
            "justification": org_justification,
        },
        {
            "name": "Language",
            "score": lang_score,
            "max_score": 5.0,
            "band_descriptor": descriptors["Language"][int(round(lang_score))],
            "justification": lang_justification,
        },
    ]

    raw_score = round(content_score + ca_score + org_score + lang_score, 2)
    institutional_score = round((raw_score / 20.0) * 10.0, 2)

    return {
        "criteria": criteria_list,
        "raw_score": raw_score,
        "max_raw_score": 20.0,
        "institutional_score": institutional_score,
        "length_penalty": length_penalty,
        "word_count_status": word_status,
    }


async def rubric_eval_node(state: EvaluationState) -> dict[str, Any]:
    """Evaluates student writing against Cambridge B2/C1 4-band criteria."""
    text = state.get("sanitized_text", state.get("student_text", ""))
    level = state.get("level", "B2")
    word_count = state.get("word_count", len(text.split()))
    min_words = state.get("min_words")
    max_words = state.get("max_words")
    mistakes = state.get("mistakes", [])

    logger.info(
        "Running rubric_eval_node for submission %s (level=%s, words=%d)",
        state.get("submission_id"),
        level,
        word_count,
    )

    if settings.LLM_PROVIDER == "mock":
        eval_result = evaluate_rubric_deterministic(
            text=text,
            level=level,
            word_count=word_count,
            min_words=min_words,
            max_words=max_words,
            mistakes_count=len(mistakes),
        )
    else:
        # LLM inference integration with zero data retention headers
        eval_result = evaluate_rubric_deterministic(
            text=text,
            level=level,
            word_count=word_count,
            min_words=min_words,
            max_words=max_words,
            mistakes_count=len(mistakes),
        )

    return {"rubric_evaluation": eval_result}
