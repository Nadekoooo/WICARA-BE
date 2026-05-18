"""add weekly report snapshots table

Revision ID: 20260518_0016_weekly_snapshots
Revises: 20260518_0015_lang_defaults
Create Date: 2026-05-18 15:10:00
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260518_0016_weekly_snapshots"
down_revision: str | Sequence[str] | None = "20260518_0015_lang_defaults"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "weekly_report_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("range_start", sa.Date(), nullable=False),
        sa.Column("range_end", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("source", sa.String(length=96), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("active_days", sa.Integer(), nullable=False),
        sa.Column("fixed_gaps", sa.Integer(), nullable=False),
        sa.Column("remaining_gaps", sa.Integer(), nullable=False),
        sa.Column("overdue_reviews", sa.Integer(), nullable=False),
        sa.Column("new_gaps", sa.Integer(), nullable=False),
        sa.Column("paired_concept_count", sa.Integer(), nullable=False),
        sa.Column(
            "payload_json",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "range_start",
            "range_end",
            name="uq_weekly_report_snapshots_user_range",
        ),
    )
    op.create_index(
        "ix_weekly_report_snapshots_user_start",
        "weekly_report_snapshots",
        ["user_id", "range_start"],
    )


def downgrade() -> None:
    op.drop_index("ix_weekly_report_snapshots_user_start", table_name="weekly_report_snapshots")
    op.drop_table("weekly_report_snapshots")
