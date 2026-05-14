"""add education_level to learner_profiles

Revision ID: 20260514_0004
Revises: 20260514_0003
Create Date: 2026-05-14 00:30:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260514_0004"
down_revision: str | None = "20260514_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "learner_profiles",
        sa.Column("education_level", sa.String(length=64), nullable=False, server_default=""),
    )
    op.alter_column("learner_profiles", "education_level", server_default=None)


def downgrade() -> None:
    op.drop_column("learner_profiles", "education_level")
