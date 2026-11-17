"""Create rubrics and rubric_criteria tables.

Revision ID: 001
Revises:
Create Date: 2026-11-16 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create rubrics table
    op.create_table(
        "rubrics",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("cefr_level", sa.String(length=10), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "is_template",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_rubrics_cefr_level",
        "rubrics",
        ["cefr_level"],
        unique=False,
    )

    # 2. Create rubric_criteria table
    op.create_table(
        "rubric_criteria",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "rubric_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("rubrics.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "weight",
            sa.Float(),
            server_default=sa.text("1.0"),
            nullable=False,
        ),
        sa.Column(
            "max_band",
            sa.Integer(),
            server_default=sa.text("5"),
            nullable=False,
        ),
        sa.Column(
            "sort_order",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "descriptors",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_rubric_criteria_rubric_id",
        "rubric_criteria",
        ["rubric_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_rubric_criteria_rubric_id", table_name="rubric_criteria")
    op.drop_table("rubric_criteria")
    op.drop_index("ix_rubrics_cefr_level", table_name="rubrics")
    op.drop_table("rubrics")
