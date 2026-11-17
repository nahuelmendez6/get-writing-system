from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EvaluationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    submission_id: str = Field(
        ...,
        description="UUID or unique identifier of the student submission",
    )
    student_text: str = Field(
        default="",
        description="Student written submission text (can be empty if image_base64 is provided)",
    )
    image_base64: str | None = Field(
        default=None,
        description="Optional Base64 encoded photograph of handwritten writing for multimodal OCR",
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

    @model_validator(mode="after")
    def validate_content_presence(self) -> "EvaluationRequest":
        has_text = bool(self.student_text and self.student_text.strip())
        has_image = bool(self.image_base64 and self.image_base64.strip())
        if not has_text and not has_image:
            raise ValueError(
                "Either student_text or image_base64 must be provided and non-empty."
            )
        return self
