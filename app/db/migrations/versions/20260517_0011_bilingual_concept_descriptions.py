"""add bilingual concept descriptions

Revision ID: 20260517_0011
Revises: 20260517_0010
Create Date: 2026-05-17 17:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260517_0011"
down_revision: str | None = "20260517_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("knowledge_concepts", sa.Column("id_desc", sa.Text(), nullable=True))
    op.add_column("knowledge_concepts", sa.Column("en_desc", sa.Text(), nullable=True))
    op.execute("UPDATE knowledge_concepts SET id_desc = description WHERE id_desc IS NULL")


def downgrade() -> None:
    op.drop_column("knowledge_concepts", "en_desc")
    op.drop_column("knowledge_concepts", "id_desc")
