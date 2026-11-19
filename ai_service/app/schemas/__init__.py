"""Pydantic schemas for ai_service."""

from app.schemas.benchmark import (
    BenchmarkCriterionScores,
    BenchmarkEvaluationResult,
    BenchmarkReportSummary,
    BenchmarkSample,
    CriterionMetricSummary,
)
from app.schemas.health import HealthCheckResponse
from app.schemas.privacy import (
    ErasureRequest,
    ErasureResponse,
    GuardianConsentSchema,
    MinorConsentValidationRequest,
    MinorConsentValidationResponse,
    RedactionItem,
    SanitizeTextRequest,
    SanitizeTextResponse,
    ZDRStatusResponse,
)
from app.schemas.request import EvaluationRequest
from app.schemas.response import (
    AIDetectionResult,
    CriterionEvaluation,
    EvaluationResponse,
    MistakeAnnotation,
    PedagogicalFeedback,
    RubricEvaluation,
)

__all__ = [
    "HealthCheckResponse",
    "EvaluationRequest",
    "AIDetectionResult",
    "CriterionEvaluation",
    "EvaluationResponse",
    "MistakeAnnotation",
    "PedagogicalFeedback",
    "RubricEvaluation",
    "BenchmarkCriterionScores",
    "BenchmarkSample",
    "BenchmarkEvaluationResult",
    "CriterionMetricSummary",
    "BenchmarkReportSummary",
    "RedactionItem",
    "SanitizeTextRequest",
    "SanitizeTextResponse",
    "ZDRStatusResponse",
    "GuardianConsentSchema",
    "MinorConsentValidationRequest",
    "MinorConsentValidationResponse",
    "ErasureRequest",
    "ErasureResponse",
]
