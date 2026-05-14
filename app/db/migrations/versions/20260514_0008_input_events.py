"""create unified input event table

Revision ID: 20260514_0008
Revises: 20260514_0007
Create Date: 2026-05-14 21:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260514_0008"
down_revision: str | None = "20260514_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "input_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("assessment_session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("concept_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("selected_option_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("image_asset_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.String(length=32), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("text_payload", sa.Text(), nullable=False),
        sa.Column(
            "raw_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "parsed_problem",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "parsed_work",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("confidence", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["assessment_session_id"], ["assessment_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["concept_id"], ["knowledge_concepts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["selected_option_id"], ["assessment_options.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_session_id"], ["workspace_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_input_events_user_created",
        "input_events",
        ["user_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_input_events_workspace_created",
        "input_events",
        ["workspace_session_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_input_events_assessment_created",
        "input_events",
        ["assessment_session_id", "created_at"],
        unique=False,
    )

    op.add_column(
        "workspace_events",
        sa.Column("input_event_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_workspace_events_input_event_id",
        "workspace_events",
        "input_events",
        ["input_event_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_workspace_events_input_event_id",
        "workspace_events",
        type_="foreignkey",
    )
    op.drop_column("workspace_events", "input_event_id")
    op.drop_index("ix_input_events_assessment_created", table_name="input_events")
    op.drop_index("ix_input_events_workspace_created", table_name="input_events")
    op.drop_index("ix_input_events_user_created", table_name="input_events")
    op.drop_table("input_events")
