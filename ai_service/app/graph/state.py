from typing import Any, TypedDict


class EvaluationState(TypedDict, total=False):
    """Explicit typed state schema representing the LangGraph pipeline execution."""

    submission_id: str
    student_text: str
    sanitized_text: str
    task_prompt: str
    level: str
    text_type: str
    min_words: int | None
    max_words: int | None
    word_count: int
    context_guidelines: str
    mistakes: list[dict[str, Any]]
    exemplar_model: str
    rubric_evaluation: dict[str, Any]
    feedback: dict[str, Any]
    ai_detection: dict[str, Any]
    validation_passed: bool
    retry_count: int
    errors: list[str]
    status: str
    execution_time_seconds: float
