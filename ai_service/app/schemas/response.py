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


class CriterionEvaluation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(
        ...,
        description="Assessment criterion (Content, Communicative Achievement, Organisation, Language)",
    )
    score: float = Field(
        ...,
        ge=0.0,
        le=5.0,
        description="Assigned band score from 0.0 to 5.0",
    )
    max_score: float = Field(
        default=5.0,
        ge=1.0,
        description="Maximum attainable band score",
    )
    band_descriptor: str = Field(
        ...,
        description="Official descriptor matching the assigned band",
    )
    justification: str = Field(
        ...,
        description="Detailed pedagogical justification citing textual evidence",
    )


class RubricEvaluation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    criteria: list[CriterionEvaluation] = Field(
        ...,
        description="Evaluation across the 4 Cambridge criteria",
    )
    raw_score: float = Field(
        ...,
        ge=0.0,
        le=20.0,
        description="Total raw score sum across criteria (0 to 20)",
    )
    max_raw_score: float = Field(
        default=20.0,
        description="Maximum raw score possible",
    )
    institutional_score: float = Field(
        ...,
        ge=0.0,
        le=10.0,
        description="Calculated internal grade mapped to a 0.0 - 10.0 scale",
    )
    length_penalty: bool = Field(
        default=False,
        description="Flag indicating if length penalty was applied",
    )
    word_count_status: Literal["NORMAL", "TOO_SHORT", "TOO_LONG"] = Field(
        default="NORMAL",
        description="Assessment of word length relative to required bounds",
    )


class PedagogicalFeedback(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    overall_feedback: str = Field(
        ...,
        description="Overall qualitative assessment summary in Spanish",
    )
    strengths: list[str] = Field(
        ...,
        description="Key strengths observed in the writing (2 to 4 points)",
    )
    areas_for_improvement: list[str] = Field(
        ...,
        description="Priority areas requiring correction and practice (2 to 4 points)",
    )
    actionable_tips: list[str] = Field(
        ...,
        description="Actionable tips for future writing assignments (exactly 3 items)",
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
    rubric_evaluation: RubricEvaluation = Field(
        ...,
        description="Detailed Cambridge rubric bands evaluation and institutional grade",
    )
    feedback: PedagogicalFeedback = Field(
        ...,
        description="Pedagogical feedback including strengths, improvements and actionable tips",
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
