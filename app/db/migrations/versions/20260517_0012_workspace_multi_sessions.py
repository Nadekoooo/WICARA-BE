"""allow multiple workspace sessions per module

Revision ID: 20260517_0012_workspace_multi
Revises: 20260517_0011_bilingual_desc
Create Date: 2026-05-17 21:45:00
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260517_0012_workspace_multi"
down_revision: str | Sequence[str] | None = "20260517_0011_bilingual_desc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "uq_workspace_sessions_user_track_module",
        "workspace_sessions",
        type_="unique",
    )


def downgrade() -> None:
    op.create_unique_constraint(
        "uq_workspace_sessions_user_track_module",
        "workspace_sessions",
        ["user_id", "track_id", "module_id"],
    )
