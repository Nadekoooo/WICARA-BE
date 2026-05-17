"""create question bank tables

Revision ID: 20260516_0010
Revises: 20260514_0008
Create Date: 2026-05-16 20:30:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260516_0010"
down_revision: str | None = "20260516_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "question_bank_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.String(length=160), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("concept_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("subject_code", sa.String(length=64), nullable=False),
        sa.Column("concept_code", sa.String(length=160), nullable=False),
        sa.Column("concept_title", sa.String(length=255), nullable=False),
        sa.Column("education_level", sa.String(length=64), nullable=False),
        sa.Column("grade_band", sa.String(length=64), nullable=False),
        sa.Column("language", sa.String(length=16), nullable=False),
        sa.Column("assessment_types", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("question_type", sa.String(length=64), nullable=False),
        sa.Column("difficulty", sa.String(length=32), nullable=False),
        sa.Column("cognitive_level", sa.String(length=64), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("helper_text", sa.Text(), nullable=False),
        sa.Column("answer_key", sa.String(length=16), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("rubric", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("source_file", sa.String(length=255), nullable=False),
        sa.Column("source_version", sa.String(length=64), nullable=False),
        sa.Column("source_hash", sa.String(length=64), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["concept_id"], ["knowledge_concepts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_id", name="uq_question_bank_items_external_id"),
    )
    op.create_index("ix_question_bank_items_external_id", "question_bank_items", ["external_id"])
    op.create_index("ix_question_bank_items_subject_code", "question_bank_items", ["subject_code"])
    op.create_index("ix_question_bank_items_concept_code", "question_bank_items", ["concept_code"])
    op.create_index("ix_question_bank_items_education_level", "question_bank_items", ["education_level"])
    op.create_index("ix_question_bank_items_language", "question_bank_items", ["language"])
    op.create_index("ix_question_bank_items_status", "question_bank_items", ["status"])

    op.create_table(
        "question_bank_options",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question_bank_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("option_key", sa.String(length=16), nullable=False),
        sa.Column("label", sa.String(length=16), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["question_bank_item_id"],
            ["question_bank_items.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "question_bank_item_id",
            "option_key",
            name="uq_question_bank_options_key",
        ),
    )

    op.create_table(
        "question_bank_import_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_path", sa.Text(), nullable=False),
        sa.Column("source_hash", sa.String(length=64), nullable=False),
        sa.Column("imported_count", sa.Integer(), nullable=False),
        sa.Column("skipped_count", sa.Integer(), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False),
        sa.Column("strict_mode", sa.Boolean(), nullable=False),
        sa.Column("errors", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("question_bank_import_runs")
    op.drop_table("question_bank_options")
    op.drop_index("ix_question_bank_items_status", table_name="question_bank_items")
    op.drop_index("ix_question_bank_items_language", table_name="question_bank_items")
    op.drop_index("ix_question_bank_items_education_level", table_name="question_bank_items")
    op.drop_index("ix_question_bank_items_concept_code", table_name="question_bank_items")
    op.drop_index("ix_question_bank_items_subject_code", table_name="question_bank_items")
    op.drop_index("ix_question_bank_items_external_id", table_name="question_bank_items")
    op.drop_table("question_bank_items")
