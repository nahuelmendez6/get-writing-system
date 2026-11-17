"""Pydantic schemas package."""

from app.schemas.health import (
    ErrorDetail,
    HealthCheckResponse,
    StandardErrorResponse,
)
from app.schemas.rubric import (
    RubricBase,
    RubricCreate,
    RubricCriterionBase,
    RubricCriterionCreate,
    RubricCriterionRead,
    RubricRead,
    calculate_institutional_score,
)

__all__ = [
    "ErrorDetail",
    "HealthCheckResponse",
    "StandardErrorResponse",
    "RubricBase",
    "RubricCreate",
    "RubricCriterionBase",
    "RubricCriterionCreate",
    "RubricCriterionRead",
    "RubricRead",
    "calculate_institutional_score",
]
