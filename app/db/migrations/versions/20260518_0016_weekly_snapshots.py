"""compatibility placeholder for weekly snapshots revision

Revision ID: 20260518_0016_weekly_snapshots
Revises: 20260518_0015_lang_defaults
Create Date: 2026-05-18 01:00:00
"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "20260518_0016_weekly_snapshots"
down_revision: str | Sequence[str] | None = "20260518_0015_lang_defaults"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
