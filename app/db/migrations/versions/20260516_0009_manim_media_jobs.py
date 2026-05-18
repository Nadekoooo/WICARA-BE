"""add manim queue columns and media jobs table

Revision ID: 20260516_0009
Revises: 20260514_0008
Create Date: 2026-05-16 18:10:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260516_0009"
down_revision: str | None = "20260514_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "media_artifacts",
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "media_artifacts",
        sa.Column("template_id", sa.String(length=120), server_default=sa.text("''"), nullable=False),
    )
    op.add_column(
        "media_artifacts",
        sa.Column(
            "spec_json",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "media_artifacts",
        sa.Column("language", sa.String(length=16), server_default=sa.text("'id'"), nullable=False),
    )
    op.add_column(
        "media_artifacts",
        sa.Column(
            "quality_profile",
            sa.String(length=32),
            server_default=sa.text("'standard'"),
            nullable=False,
        ),
    )
    op.add_column(
        "media_artifacts",
        sa.Column("video_url", sa.Text(), server_default=sa.text("''"), nullable=False),
    )
    op.add_column(
        "media_artifacts",
        sa.Column(
            "render_meta_json",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )
    op.create_foreign_key(
        "fk_media_artifacts_workspace_id",
        "media_artifacts",
        "workspace_sessions",
        ["workspace_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "media_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=32), server_default=sa.text("'queued'"), nullable=False),
        sa.Column("progress", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("message", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column("attempt", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["artifact_id"], ["media_artifacts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_media_jobs_artifact_id",
        "media_jobs",
        ["artifact_id"],
        unique=False,
    )
    op.create_index(
        "ix_media_jobs_status_created",
        "media_jobs",
        ["status", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_media_jobs_status_created", table_name="media_jobs")
    op.drop_index("ix_media_jobs_artifact_id", table_name="media_jobs")
    op.drop_table("media_jobs")

    op.drop_constraint(
        "fk_media_artifacts_workspace_id",
        "media_artifacts",
        type_="foreignkey",
    )
    op.drop_column("media_artifacts", "render_meta_json")
    op.drop_column("media_artifacts", "video_url")
    op.drop_column("media_artifacts", "quality_profile")
    op.drop_column("media_artifacts", "language")
    op.drop_column("media_artifacts", "spec_json")
    op.drop_column("media_artifacts", "template_id")
    op.drop_column("media_artifacts", "workspace_id")
