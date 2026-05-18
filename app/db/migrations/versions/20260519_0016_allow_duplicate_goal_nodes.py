"""allow multiple active learning goals for the same node

Revision ID: 20260519_0016_dup_goal_nodes
Revises: 20260518_0016_weekly_snapshots
Create Date: 2026-05-19 10:30:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260519_0016_dup_goal_nodes"
down_revision: str | Sequence[str] | None = "20260518_0016_weekly_snapshots"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INDEX_NAME = "uq_learning_goals_active_user_target"


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        with op.get_context().autocommit_block():
            op.execute(sa.text("SET lock_timeout TO '5s'"))
            op.execute(sa.text("SET statement_timeout TO '30s'"))
            try:
                op.execute(sa.text(f'DROP INDEX CONCURRENTLY IF EXISTS "{INDEX_NAME}"'))
            finally:
                op.execute(sa.text("RESET statement_timeout"))
                op.execute(sa.text("RESET lock_timeout"))
        return

    inspector = sa.inspect(bind)
    indexes = {index["name"] for index in inspector.get_indexes("learning_goals")}
    if INDEX_NAME in indexes:
        op.drop_index(INDEX_NAME, table_name="learning_goals")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indexes = {index["name"] for index in inspector.get_indexes("learning_goals")}
    if INDEX_NAME not in indexes:
        op.create_index(
            INDEX_NAME,
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
