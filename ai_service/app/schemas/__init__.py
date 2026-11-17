"""Pydantic schemas for ai_service."""

from app.schemas.health import HealthCheckResponse
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
]
