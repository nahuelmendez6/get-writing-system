import uuid
from typing import Any

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.models import BaseModel


class Rubric(BaseModel):
    """Rubric entity representing an assessment scale and its configuration."""

    __tablename__ = "rubrics"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    cefr_level: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_template: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    criteria: Mapped[list["RubricCriterion"]] = relationship(
        "RubricCriterion",
        back_populates="rubric",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="RubricCriterion.sort_order",
    )


class RubricCriterion(BaseModel):
    """Individual assessment criterion belonging to a Rubric."""

    __tablename__ = "rubric_criteria"

    rubric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("rubrics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    max_band: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    descriptors: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        default=dict,
        nullable=False,
    )

    rubric: Mapped["Rubric"] = relationship(
        "Rubric",
        back_populates="criteria",
    )
