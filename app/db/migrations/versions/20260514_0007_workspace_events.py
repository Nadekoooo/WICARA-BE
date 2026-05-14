"""create workspace session and event tables

Revision ID: 20260514_0007
Revises: 20260514_0006
Create Date: 2026-05-14 20:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260514_0007"
down_revision: str | None = "20260514_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "workspace_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("track_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("module_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("current_topic", sa.String(length=255), nullable=False),
        sa.Column("content_mode", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["module_id"], ["track_modules.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["track_id"], ["learning_tracks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "track_id",
            "module_id",
            name="uq_workspace_sessions_user_track_module",
        ),
    )
    op.create_index(
        "ix_workspace_sessions_user_status",
        "workspace_sessions",
        ["user_id", "status"],
        unique=False,
    )

    op.create_table(
        "workspace_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=32), nullable=False),
        sa.Column("actor_type", sa.String(length=32), nullable=False),
        sa.Column("text_payload", sa.Text(), nullable=False),
        sa.Column("canvas_snapshot_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("media_artifact_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["media_artifact_id"], ["media_artifacts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["workspace_session_id"],
            ["workspace_sessions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_workspace_events_session_created",
        "workspace_events",
        ["workspace_session_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_workspace_events_session_created", table_name="workspace_events")
    op.drop_table("workspace_events")
    op.drop_index("ix_workspace_sessions_user_status", table_name="workspace_sessions")
    op.drop_table("workspace_sessions")
