"""add bilingual concept descriptions

Revision ID: 20260517_0011_bilingual_desc
Revises: 20260517_0011
Create Date: 2026-05-17 17:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260517_0011_bilingual_desc"
down_revision: str | None = "20260517_0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {
        column["name"]
        for column in inspector.get_columns("knowledge_concepts")
    }

    if "id_desc" not in columns:
        op.add_column("knowledge_concepts", sa.Column("id_desc", sa.Text(), nullable=True))
        columns.add("id_desc")
    if "en_desc" not in columns:
        op.add_column("knowledge_concepts", sa.Column("en_desc", sa.Text(), nullable=True))

    op.execute("UPDATE knowledge_concepts SET id_desc = description WHERE id_desc IS NULL")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {
        column["name"]
        for column in inspector.get_columns("knowledge_concepts")
    }

    if "en_desc" in columns:
        op.drop_column("knowledge_concepts", "en_desc")
    if "id_desc" in columns:
        op.drop_column("knowledge_concepts", "id_desc")
