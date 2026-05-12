"""create curriculum graph tables

Revision ID: 20260513_0001
Revises:
Create Date: 2026-05-13 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260513_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "subjects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_subjects_code", "subjects", ["code"], unique=False)

    op.create_table(
        "knowledge_concepts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("grade_band", sa.String(length=64), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("layout_x", sa.Float(), nullable=True),
        sa.Column("layout_y", sa.Float(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "subject_id",
            "code",
            name="uq_knowledge_concepts_subject_code",
        ),
    )
    op.create_index(
        "ix_knowledge_concepts_subject_display_order",
        "knowledge_concepts",
        ["subject_id", "display_order"],
        unique=False,
    )

    op.create_table(
        "concept_edges",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("from_concept_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("to_concept_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("edge_type", sa.String(length=32), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "from_concept_id <> to_concept_id",
            name="ck_concept_edges_no_self_loop",
        ),
        sa.ForeignKeyConstraint(
            ["from_concept_id"],
            ["knowledge_concepts.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["to_concept_id"],
            ["knowledge_concepts.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "from_concept_id",
            "to_concept_id",
            "edge_type",
            name="uq_concept_edges_from_to_type",
        ),
    )
    op.create_index(
        "ix_concept_edges_from_type",
        "concept_edges",
        ["from_concept_id", "edge_type"],
        unique=False,
    )
    op.create_index(
        "ix_concept_edges_to_type",
        "concept_edges",
        ["to_concept_id", "edge_type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_concept_edges_to_type", table_name="concept_edges")
    op.drop_index("ix_concept_edges_from_type", table_name="concept_edges")
    op.drop_table("concept_edges")
    op.drop_index(
        "ix_knowledge_concepts_subject_display_order",
        table_name="knowledge_concepts",
    )
    op.drop_table("knowledge_concepts")
    op.drop_index("ix_subjects_code", table_name="subjects")
    op.drop_table("subjects")
