import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    """Return the current datetime in UTC with timezone information."""
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Declarative Base class for all SQLAlchemy entities."""

    pass


class TimestampMixin:
    """Mixin providing created_at and updated_at UTC timestamp fields."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class UUIDPrimaryKeyMixin:
    """Mixin providing a UUID version 4 primary key."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )


class BaseModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Abstract base model inheriting UUID primary key and timestamp mixins."""

    __abstract__ = True
