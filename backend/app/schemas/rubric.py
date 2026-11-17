import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def calculate_institutional_score(
    raw_score: float,
    max_raw_score: float = 20.0,
) -> float:
    """Calculate institutional score mapped to a 0.0 - 10.0 scale.

    Formula: (raw_score / max_raw_score) * 10.0
    No trademarked names are referenced in outputs.
    """
    if max_raw_score <= 0:
        return 0.0
    score = (raw_score / max_raw_score) * 10.0
    clamped = max(0.0, min(10.0, score))
    return round(clamped, 2)


class RubricCriterionBase(BaseModel):
    name: str = Field(
        ...,
        max_length=100,
        description="Criterion name, e.g. Content",
    )
    description: str | None = Field(
        default=None,
        description="Detailed explanation of the criterion",
    )
    weight: float = Field(
        default=1.0,
        gt=0,
        description="Weighting multiplier for criterion",
    )
    max_band: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum band score attainable",
    )
    sort_order: int = Field(
        default=0,
        ge=0,
        description="Display sort ordering",
    )
    descriptors: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured dictionary with band descriptors (e.g., '0' to '5')",
    )


class RubricCriterionCreate(RubricCriterionBase):
    pass


class RubricCriterionRead(RubricCriterionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    rubric_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class RubricBase(BaseModel):
    name: str = Field(
        ...,
        max_length=100,
        description="Rubric template name",
    )
    cefr_level: str = Field(
        ...,
        max_length=10,
        description="Target CEFR level (e.g., B1, B2, C1, C2)",
    )
    description: str | None = Field(
        default=None,
        description="General description of the rubric scale",
    )
    is_template: bool = Field(
        default=True,
        description="Indicates if rubric acts as a system template",
    )
    is_active: bool = Field(
        default=True,
        description="Active status for rubric availability",
    )


class RubricCreate(RubricBase):
    criteria: list[RubricCriterionBase] = Field(
        default_factory=list,
        description="List of initial criteria to associate with the rubric",
    )


class RubricRead(RubricBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    criteria: list[RubricCriterionRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
