"""Pydantic schemas for the AI benchmark, multimodal OCR, and calibration engine."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BenchmarkCriterionScores(BaseModel):
    """Criterion-level scores for Cambridge 4-band evaluation."""

    model_config = ConfigDict(extra="forbid")

    content: float = Field(..., ge=0.0, le=5.0, description="Content band score (0-5)")
    communicative_achievement: float = Field(
        ..., ge=0.0, le=5.0, description="Communicative Achievement band score (0-5)"
    )
    organisation: float = Field(
        ..., ge=0.0, le=5.0, description="Organisation band score (0-5)"
    )
    language: float = Field(
        ..., ge=0.0, le=5.0, description="Language band score (0-5)"
    )
    raw_score: float = Field(
        ..., ge=0.0, le=20.0, description="Total raw score (sum of 4 criteria, 0-20)"
    )
    institutional_score: float = Field(
        ..., ge=0.0, le=10.0, description="Institutional scale grade (0-10)"
    )


class BenchmarkSample(BaseModel):
    """A writing sample within the benchmark dataset with teacher ground truth or photo."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Unique sample ID (e.g. BENCH-001)")
    cefr_level: Literal["B1", "B2", "C1", "C2"] = Field(
        ..., description="Target CEFR proficiency level"
    )
    task_type: Literal[
        "essay", "article", "email", "review", "report", "story", "proposal"
    ] = Field(..., description="Genre or task type")
    title: str = Field(..., min_length=3, description="Descriptive writing title")
    prompt: str = Field(
        ..., min_length=10, description="Task assignment prompt instructions"
    )
    student_text: str | None = Field(
        default=None, description="Pre-transcribed or digital student text"
    )
    image_path: str | None = Field(
        default=None, description="Relative or absolute path to handwritten image file"
    )
    image_base64: str | None = Field(
        default=None, description="Base64 encoded string of handwritten image"
    )
    word_count: int | None = Field(
        default=None, description="Pre-computed or expected word count"
    )
    min_words: int | None = Field(default=None, description="Minimum word boundary")
    max_words: int | None = Field(default=None, description="Maximum word boundary")
    human_scores: BenchmarkCriterionScores | None = Field(
        default=None,
        description="Reference scores awarded by Cambridge examiner/teacher",
    )
    expected_length_penalty: bool = Field(
        default=False, description="Whether length deviation triggers a penalty"
    )
    expected_ai_generated: bool = Field(
        default=False, description="Whether text is flagged as synthetic AI"
    )
    teacher_notes: str | None = Field(
        default=None, description="Examiner notes or pedagogical comments"
    )


class BenchmarkEvaluationResult(BaseModel):
    """Comparison result of a single writing evaluated by AI vs human ground truth."""

    model_config = ConfigDict(extra="forbid")

    sample_id: str
    cefr_level: str
    task_type: str
    ocr_applied: bool = Field(
        default=False, description="Whether OCR was used to extract text"
    )
    extracted_text: str = Field(
        default="", description="Text extracted from image or input"
    )
    human_scores: BenchmarkCriterionScores | None = None
    ai_scores: BenchmarkCriterionScores
    criterion_errors: dict[str, float] = Field(
        default_factory=dict,
        description="Absolute difference |human - ai| for each of the 4 criteria",
    )
    raw_score_error: float | None = None
    institutional_score_error: float | None = None
    exact_matches: int = Field(default=0, ge=0, le=4)
    within_one_band_matches: int = Field(default=0, ge=0, le=4)
    length_penalty_predicted: bool
    length_penalty_expected: bool | None = None
    ai_generated_predicted: bool
    ai_generated_expected: bool | None = None


class CriterionMetricSummary(BaseModel):
    """Aggregated statistical metrics for a specific criterion."""

    model_config = ConfigDict(extra="forbid")

    criterion: str
    mae: float = Field(..., description="Mean Absolute Error across all samples")
    mse: float = Field(..., description="Mean Squared Error")
    exact_match_pct: float = Field(
        ..., ge=0.0, le=100.0, description="Percentage of exact score matches"
    )
    within_one_band_pct: float = Field(
        ..., ge=0.0, le=100.0, description="Percentage of predictions within +-1 band"
    )
    max_error: float = Field(..., description="Maximum absolute error encountered")


class BenchmarkReportSummary(BaseModel):
    """Overall consolidated report across the entire benchmark dataset."""

    model_config = ConfigDict(extra="forbid")

    total_samples: int
    evaluated_with_human_ground_truth: int
    levels_evaluated: list[str]
    ocr_processed_count: int
    overall_mae: float = Field(
        ..., description="Global Mean Absolute Error across all 4 criteria"
    )
    overall_within_one_band_pct: float = Field(
        ...,
        description="Global percentage of criteria within +-1 band (Target: >= 80%)",
    )
    overall_exact_match_pct: float = Field(
        ..., description="Global percentage of criteria with exact match"
    )
    passed: bool = Field(
        ...,
        description="True if overall_mae <= 0.5 and overall_within_one_band_pct >= 80.0",
    )
    criteria_metrics: dict[str, CriterionMetricSummary]
    level_breakdown: dict[str, dict[str, float]]
    penalty_accuracy_pct: float | None = None
    ai_detection_accuracy_pct: float | None = None
    detailed_results: list[BenchmarkEvaluationResult] = Field(default_factory=list)
