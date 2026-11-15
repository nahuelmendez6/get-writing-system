from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MistakeAnnotation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique mistake identifier")
    start_index: int = Field(
        ...,
        ge=0,
        description="Character start offset in the original text",
    )
    end_index: int = Field(
        ...,
        ge=0,
        description="Character end offset in the original text",
    )
    quote: str = Field(..., description="Original excerpt containing the mistake")
    correction: str = Field(..., description="Suggested correction")
    category: Literal["grammar", "spelling", "punctuation", "vocabulary", "style"] = (
        Field(..., description="Pedagogical category of the mistake")
    )
    explanation: str = Field(
        ...,
        description="Pedagogical explanation in Spanish explaining why it is an error",
    )


class AIDetectionResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Estimated probability of synthetic AI generation",
    )
    is_likely_ai: bool = Field(
        ...,
        description="Alert flag indicating probable AI generation",
    )
    confidence: Literal["LOW", "MEDIUM", "HIGH"] = Field(
        ...,
        description="Confidence band of the detection assessment",
    )
    rationale: str = Field(
        ...,
        description="Detailed justification of stylistic and syntactic indicators",
    )


class EvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    submission_id: str = Field(..., description="Submission identifier")
    word_count: int = Field(
        ...,
        ge=0,
        description="Total words counted in the student submission",
    )
    mistakes: list[MistakeAnnotation] = Field(
        default_factory=list,
        description="List of identified errors with character offsets",
    )
    exemplar_model: str = Field(
        ...,
        description="Band 5 exemplary rewritten version of the text",
    )
    ai_detection: AIDetectionResult = Field(
        ...,
        description="AI text authorship evaluation result",
    )
    status: Literal["SUCCESS", "FAILED"] = Field(
        default="SUCCESS",
        description="Overall pipeline execution status",
    )
    execution_time_seconds: float = Field(
        ...,
        ge=0.0,
        description="Total execution time in seconds",
    )
