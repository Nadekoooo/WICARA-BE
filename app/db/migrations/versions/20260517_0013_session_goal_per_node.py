"""enforce one active session-goal per user per target node

Revision ID: 20260517_0013_session_goal_per_node
Revises: 20260517_0012_workspace_multi
Create Date: 2026-05-17 22:40:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260517_0013_session_goal_per_node"
down_revision: str | Sequence[str] | None = "20260517_0012_workspace_multi"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index("uq_learning_goals_active_user", table_name="learning_goals")
    op.create_index(
        "uq_learning_goals_active_user_target",
        "learning_goals",
        ["user_id", "target_concept_id"],
        unique=True,
        postgresql_where=sa.text(
            "target_concept_id is not null and status in ('confirmed', 'pretest_in_progress', 'diagnosed', 'in_progress')"
        ),
        sqlite_where=sa.text(
            "target_concept_id is not null and status in ('confirmed', 'pretest_in_progress', 'diagnosed', 'in_progress')"
        ),
    )


def downgrade() -> None:
    op.drop_index("uq_learning_goals_active_user_target", table_name="learning_goals")
    op.create_index(
        "uq_learning_goals_active_user",
        "learning_goals",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text(
            "status in ('confirmed', 'pretest_in_progress', 'diagnosed', 'in_progress')"
        ),
        sqlite_where=sa.text(
            "status in ('confirmed', 'pretest_in_progress', 'diagnosed', 'in_progress')"
        ),
    )
