import time
from typing import Any

from langgraph.graph import END, START, StateGraph

from app.core.logging import logger
from app.graph.nodes.ai_detector import ai_detector_node
from app.graph.nodes.context_prep import context_prep_node
from app.graph.nodes.exemplar_gen import exemplar_gen_node
from app.graph.nodes.validator import validator_node
from app.graph.nodes.writing_analysis import writing_analysis_node
from app.graph.state import EvaluationState
from app.schemas.request import EvaluationRequest
from app.schemas.response import (
    AIDetectionResult,
    EvaluationResponse,
    MistakeAnnotation,
)


def should_continue_or_retry(state: EvaluationState | dict[str, Any]) -> str:
    """Route to END if validated, otherwise loop back to writing analysis for retry."""
    if state.get("validation_passed", False):
        return END
    logger.info("Routing back to writing_analysis for retry attempt")
    return "writing_analysis"


def build_evaluation_graph() -> Any:
    """Construct and compile the 5-node LangGraph evaluation StateGraph."""
    workflow = StateGraph(EvaluationState)

    # 1. Add nodes
    workflow.add_node("context_prep", context_prep_node)
    workflow.add_node("writing_analysis", writing_analysis_node)
    workflow.add_node("exemplar_gen", exemplar_gen_node)
    workflow.add_node("ai_detector", ai_detector_node)
    workflow.add_node("validator", validator_node)

    # 2. Add sequential edges
    workflow.add_edge(START, "context_prep")
    workflow.add_edge("context_prep", "writing_analysis")
    workflow.add_edge("writing_analysis", "exemplar_gen")
    workflow.add_edge("exemplar_gen", "ai_detector")
    workflow.add_edge("ai_detector", "validator")

    # 3. Add conditional edge for validation and retry loop
    workflow.add_conditional_edges(
        "validator",
        should_continue_or_retry,
        {
            "writing_analysis": "writing_analysis",
            END: END,
        },
    )

    return workflow.compile()


evaluation_graph = build_evaluation_graph()


async def run_evaluation_pipeline(payload: EvaluationRequest) -> EvaluationResponse:
    """Entry point executing the LangGraph pipeline against an evaluation request."""
    start_time = time.perf_counter()

    initial_state: EvaluationState = {
        "submission_id": payload.submission_id,
        "student_text": payload.student_text,
        "task_prompt": payload.task_prompt,
        "level": payload.level,
        "text_type": payload.text_type,
        "min_words": payload.min_words,
        "max_words": payload.max_words,
        "retry_count": 0,
        "errors": [],
    }

    logger.info(
        "Starting LangGraph evaluation pipeline for submission %s (%s - %s)",
        payload.submission_id,
        payload.level,
        payload.text_type,
    )

    final_state: EvaluationState = await evaluation_graph.ainvoke(initial_state)

    execution_duration = round(time.perf_counter() - start_time, 2)

    # Format output mistakes
    mistakes = [
        MistakeAnnotation.model_validate(m) for m in final_state.get("mistakes", [])
    ]
    ai_det = AIDetectionResult.model_validate(final_state.get("ai_detection", {}))

    return EvaluationResponse(
        submission_id=final_state.get("submission_id", payload.submission_id),
        word_count=final_state.get("word_count", 0),
        mistakes=mistakes,
        exemplar_model=final_state.get("exemplar_model", ""),
        ai_detection=ai_det,
        status="SUCCESS",
        execution_time_seconds=execution_duration,
    )
