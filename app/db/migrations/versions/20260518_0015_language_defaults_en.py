"""set language column defaults to english

Revision ID: 20260518_0015_lang_defaults
Revises: 20260517_0014_bilingual_fix
Create Date: 2026-05-18 00:15:00
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260518_0015_lang_defaults"
down_revision: str | Sequence[str] | None = "20260517_0014_bilingual_fix"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


LANGUAGE_COLUMNS: tuple[tuple[str, str], ...] = (
    ("learner_profiles", "preferred_language"),
    ("learning_goal_resolutions", "language"),
    ("media_artifacts", "language"),
    ("question_bank_items", "language"),
)


def upgrade() -> None:
    _set_defaults("en")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if _has_column(inspector, tables, "learner_profiles", "preferred_language"):
        op.alter_column(
            "learner_profiles",
            "preferred_language",
            server_default=None,
            existing_type=sa.String(length=16),
            existing_nullable=False,
        )

    for table_name, column_name in LANGUAGE_COLUMNS[1:]:
        if _has_column(inspector, tables, table_name, column_name):
            op.alter_column(
                table_name,
                column_name,
                server_default=sa.text("'id'"),
                existing_type=sa.String(length=16),
                existing_nullable=False,
            )


def _set_defaults(language: str) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    for table_name, column_name in LANGUAGE_COLUMNS:
        if not _has_column(inspector, tables, table_name, column_name):
            continue
        op.alter_column(
            table_name,
            column_name,
            server_default=sa.text(f"'{language}'"),
            existing_type=sa.String(length=16),
            existing_nullable=False,
        )


def _has_column(
    inspector: sa.Inspector,
    tables: set[str],
    table_name: str,
    column_name: str,
) -> bool:
    if table_name not in tables:
        return False
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))
