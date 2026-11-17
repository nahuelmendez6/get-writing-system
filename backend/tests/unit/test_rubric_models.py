import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.seed_rubrics import (
    CAMBRIDGE_B2_RUBRIC_DATA,
    CAMBRIDGE_C1_RUBRIC_DATA,
    get_default_rubric_templates,
    seed_default_rubrics,
)
from app.models.rubric import Rubric, RubricCriterion
from app.schemas.rubric import (
    RubricCreate,
    RubricCriterionBase,
    calculate_institutional_score,
)


@pytest.mark.asyncio
async def test_rubric_and_criteria_relationship(db_session: AsyncSession) -> None:
    """Validate rubric creation with nested criteria and cascade delete."""
    rubric = Rubric(
        name="Custom Test Rubric",
        cefr_level="B2",
        description="Test rubric description",
        is_template=False,
        is_active=True,
    )
    criterion = RubricCriterion(
        name="Content",
        description="Assessment of task completion",
        weight=1.0,
        max_band=5,
        sort_order=0,
        descriptors={
            "5": "All content relevant.",
            "3": "Minor omissions.",
            "0": "Irrelevant.",
        },
    )
    rubric.criteria.append(criterion)

    db_session.add(rubric)
    await db_session.commit()
    await db_session.refresh(rubric)

    assert isinstance(rubric.id, uuid.UUID)
    assert len(rubric.criteria) == 1
    saved_crit = rubric.criteria[0]
    assert saved_crit.rubric_id == rubric.id
    assert saved_crit.descriptors["5"] == "All content relevant."

    # Test cascade delete
    await db_session.delete(rubric)
    await db_session.commit()

    crit_query = select(RubricCriterion).where(RubricCriterion.id == saved_crit.id)
    crit_result = await db_session.execute(crit_query)
    assert crit_result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_seed_default_rubrics_idempotency(db_session: AsyncSession) -> None:
    """Verify default seed creates B2 and C1 rubrics with 4 criteria each
    and is idempotent.
    """
    templates = get_default_rubric_templates()
    assert len(templates) == 2
    assert CAMBRIDGE_B2_RUBRIC_DATA["cefr_level"] == "B2"
    assert CAMBRIDGE_C1_RUBRIC_DATA["cefr_level"] == "C1"

    # 1. Seed once
    seeded_first = await seed_default_rubrics(db_session)
    assert len(seeded_first) == 2

    for rubric in seeded_first:
        assert rubric.cefr_level in ["B2", "C1"]
        assert len(rubric.criteria) == 4
        criteria_names = [c.name for c in rubric.criteria]
        assert "Content" in criteria_names
        assert "Communicative Achievement" in criteria_names
        assert "Organisation" in criteria_names
        assert "Language" in criteria_names
        for c in rubric.criteria:
            assert "0" in c.descriptors
            assert "5" in c.descriptors

    # 2. Seed second time to verify idempotency (no duplicate entries)
    seeded_second = await seed_default_rubrics(db_session)
    assert len(seeded_second) == 2

    all_rubrics = (await db_session.execute(select(Rubric))).scalars().all()
    assert len(all_rubrics) == 2


def test_calculate_institutional_score_boundaries() -> None:
    """Test institutional score mapping (0 to 10 scale)."""
    # Exact boundaries
    assert calculate_institutional_score(0.0, 20.0) == 0.0
    assert calculate_institutional_score(20.0, 20.0) == 10.0
    assert calculate_institutional_score(10.0, 20.0) == 5.0
    assert calculate_institutional_score(12.0, 20.0) == 6.0  # Pass mark

    # Clamping
    assert calculate_institutional_score(-5.0, 20.0) == 0.0
    assert calculate_institutional_score(25.0, 20.0) == 10.0

    # Zero / negative max_raw_score safeguard
    assert calculate_institutional_score(10.0, 0.0) == 0.0
    assert calculate_institutional_score(10.0, -5.0) == 0.0

    # Decimal rounding
    assert calculate_institutional_score(13.5, 20.0) == 6.75


def test_rubric_create_schema_validation() -> None:
    """Verify RubricCreate schema validation."""
    rubric_in = RubricCreate(
        name="Test",
        cefr_level="b2",
        criteria=[
            RubricCriterionBase(
                name="Content",
                weight=1.5,
                max_band=5,
                descriptors={"5": "Excellent"},
            )
        ],
    )
    assert rubric_in.name == "Test"
    assert len(rubric_in.criteria) == 1
    assert rubric_in.criteria[0].weight == 1.5
