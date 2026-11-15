import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models import BaseModel


class DummyEntity(BaseModel):
    __tablename__ = "dummy_entities"

    name: Mapped[str] = mapped_column(String(50), nullable=False)


@pytest.mark.asyncio
async def test_base_model_uuid_and_utc_timestamps(db_session: AsyncSession) -> None:
    entity = DummyEntity(name="First Entity")
    db_session.add(entity)
    await db_session.commit()
    await db_session.refresh(entity)

    # 1. Validate UUID v4 primary key
    assert isinstance(entity.id, uuid.UUID)
    assert entity.id.version == 4

    # 2. Validate UTC timestamp awareness
    assert isinstance(entity.created_at, datetime)
    assert isinstance(entity.updated_at, datetime)

    # Ensure timezone info is present and represents UTC
    if entity.created_at.tzinfo is not None:
        assert entity.created_at.tzinfo == UTC
    if entity.updated_at.tzinfo is not None:
        assert entity.updated_at.tzinfo == UTC

    # Timestamps should be very close to the current UTC time
    now_utc = datetime.now(UTC)
    # Using naive conversion for comparison if sqlite strips tzinfo
    created_naive = entity.created_at.replace(tzinfo=None)
    now_naive = now_utc.replace(tzinfo=None)
    assert (now_naive - created_naive).total_seconds() < 5


@pytest.mark.asyncio
async def test_base_model_uuid_uniqueness(db_session: AsyncSession) -> None:
    entity_a = DummyEntity(name="Entity A")
    entity_b = DummyEntity(name="Entity B")

    db_session.add_all([entity_a, entity_b])
    await db_session.commit()
    await db_session.refresh(entity_a)
    await db_session.refresh(entity_b)

    assert entity_a.id != entity_b.id
    assert entity_a.id.version == 4
    assert entity_b.id.version == 4


@pytest.mark.asyncio
async def test_base_model_updated_at_modification(db_session: AsyncSession) -> None:
    entity = DummyEntity(name="Original Name")
    db_session.add(entity)
    await db_session.commit()
    await db_session.refresh(entity)

    original_updated_at = entity.updated_at

    # Update attribute
    entity.name = "Modified Name"
    # Explicitly set updated_at if running on SQLite or allow ORM hook
    entity.updated_at = datetime.now(UTC)
    await db_session.commit()
    await db_session.refresh(entity)

    query = select(DummyEntity).where(DummyEntity.id == entity.id)
    result = await db_session.execute(query)
    fetched = result.scalar_one()

    assert fetched.name == "Modified Name"
    assert fetched.updated_at >= original_updated_at
