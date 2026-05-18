"""ensure bilingual concept description columns exist

Revision ID: 20260517_0014_bilingual_fix
Revises: 20260517_0013_goal_per_node
Create Date: 2026-05-17 23:35:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260517_0014_bilingual_fix"
down_revision: str | Sequence[str] | None = "20260517_0013_goal_per_node"
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
        columns.add("en_desc")

    if "id_desc" in columns:
        op.execute(
            sa.text(
                "UPDATE knowledge_concepts "
                "SET id_desc = description "
                "WHERE id_desc IS NULL"
            )
        )


def downgrade() -> None:
    # No-op by design: this migration repairs existing databases that skipped
    # the earlier bilingual-description migration after a revision graph fix.
    pass
