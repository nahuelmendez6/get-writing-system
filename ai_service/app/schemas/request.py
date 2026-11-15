from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EvaluationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    submission_id: str = Field(
        ...,
        description="UUID or unique identifier of the student submission",
    )
    student_text: str = Field(
        ...,
        min_length=1,
        description="Student written submission text",
    )
    task_prompt: str = Field(
        ...,
        min_length=1,
        description="Assignment writing prompt and instructions",
    )
    level: Literal["B1", "B2", "C1", "C2"] = Field(
        ...,
        description="Target Cambridge / CEFR examination level",
    )
    text_type: Literal[
        "essay", "article", "report", "review", "email", "proposal", "story"
    ] = Field(..., description="Target text genre")
    min_words: int | None = Field(
        default=None,
        ge=1,
        description="Minimum expected word count",
    )
    max_words: int | None = Field(
        default=None,
        ge=1,
        description="Maximum expected word count",
    )
