"""add goal resolver and adaptive pretest pack schema

Revision ID: 20260517_0011
Revises: 20260516_0010
Create Date: 2026-05-17 09:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260517_0011"
down_revision: str | None = "20260516_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "learning_goal_resolutions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("raw_query", sa.Text(), nullable=False),
        sa.Column("subject_code", sa.String(length=64), nullable=False),
        sa.Column("education_level", sa.String(length=64), nullable=False),
        sa.Column("grade_level", sa.String(length=64), nullable=False),
        sa.Column("language", sa.String(length=16), nullable=False),
        sa.Column("suggested_concept_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("alternatives_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("candidate_snapshot_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("llm_response_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("llm_provider", sa.String(length=64), nullable=False),
        sa.Column("llm_model", sa.String(length=128), nullable=False),
        sa.Column("prompt_version", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["suggested_concept_id"], ["knowledge_concepts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "image_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("mime_type", sa.String(length=64), nullable=False),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("checksum", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column("learning_goals", sa.Column("resolution_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("learning_goals", sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("learning_goals", sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("learning_goals", sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key(
        "fk_learning_goals_resolution_id_learning_goal_resolutions",
        "learning_goals",
        "learning_goal_resolutions",
        ["resolution_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "uq_learning_goals_active_user",
        "learning_goals",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("status in ('confirmed', 'pretest_in_progress', 'diagnosed', 'in_progress')"),
        sqlite_where=sa.text("status in ('confirmed', 'pretest_in_progress', 'diagnosed', 'in_progress')"),
    )

    op.add_column("assessment_sessions", sa.Column("target_concept_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column(
        "assessment_sessions",
        sa.Column("source", sa.String(length=64), nullable=False, server_default="adaptive_generated"),
    )
    op.add_column(
        "assessment_sessions",
        sa.Column(
            "graph_scope_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.add_column(
        "assessment_sessions",
        sa.Column(
            "decision_state_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.add_column("assessment_sessions", sa.Column("max_depth", sa.Integer(), nullable=False, server_default="2"))
    op.add_column("assessment_sessions", sa.Column("max_questions", sa.Integer(), nullable=False, server_default="10"))
    op.add_column("assessment_sessions", sa.Column("max_nodes_visited", sa.Integer(), nullable=False, server_default="5"))
    op.create_foreign_key(
        "fk_assessment_sessions_target_concept_id_knowledge_concepts",
        "assessment_sessions",
        "knowledge_concepts",
        ["target_concept_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "assessment_question_packs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("concept_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("generation_source", sa.String(length=64), nullable=False),
        sa.Column("llm_provider", sa.String(length=64), nullable=False),
        sa.Column("llm_model", sa.String(length=128), nullable=False),
        sa.Column("prompt_version", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["concept_id"], ["knowledge_concepts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["session_id"], ["assessment_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "concept_id", name="uq_assessment_question_packs_session_concept"),
    )

    op.add_column("assessment_questions", sa.Column("pack_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("assessment_questions", sa.Column("generation_source", sa.String(length=64), nullable=False, server_default=""))
    op.add_column("assessment_questions", sa.Column("generation_prompt_version", sa.String(length=64), nullable=False, server_default=""))
    op.add_column(
        "assessment_questions",
        sa.Column(
            "llm_metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.add_column("assessment_questions", sa.Column("expected_reasoning", sa.Text(), nullable=False, server_default=""))
    op.add_column(
        "assessment_questions",
        sa.Column(
            "rubric_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.create_foreign_key(
        "fk_assessment_questions_pack_id_assessment_question_packs",
        "assessment_questions",
        "assessment_question_packs",
        ["pack_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("assessment_attempts", sa.Column("canvas_asset_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("assessment_attempts", sa.Column("typed_reasoning", sa.Text(), nullable=False, server_default=""))
    op.add_column("assessment_attempts", sa.Column("is_correct", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("assessment_attempts", sa.Column("answer_score", sa.Float(), nullable=False, server_default="0"))
    op.add_column("assessment_attempts", sa.Column("reasoning_score", sa.Float(), nullable=True))
    op.add_column("assessment_attempts", sa.Column("canvas_score", sa.Float(), nullable=True))
    op.add_column("assessment_attempts", sa.Column("evidence_score", sa.Float(), nullable=False, server_default="0"))
    op.add_column("assessment_attempts", sa.Column("diagnostic_signal", sa.String(length=64), nullable=False, server_default=""))
    op.add_column(
        "assessment_attempts",
        sa.Column(
            "evaluation_metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.create_foreign_key(
        "fk_assessment_attempts_canvas_asset_id_image_assets",
        "assessment_attempts",
        "image_assets",
        ["canvas_asset_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_assessment_attempts_canvas_asset_id_image_assets", "assessment_attempts", type_="foreignkey")
    op.drop_column("assessment_attempts", "evaluation_metadata_json")
    op.drop_column("assessment_attempts", "diagnostic_signal")
    op.drop_column("assessment_attempts", "evidence_score")
    op.drop_column("assessment_attempts", "canvas_score")
    op.drop_column("assessment_attempts", "reasoning_score")
    op.drop_column("assessment_attempts", "answer_score")
    op.drop_column("assessment_attempts", "is_correct")
    op.drop_column("assessment_attempts", "typed_reasoning")
    op.drop_column("assessment_attempts", "canvas_asset_id")

    op.drop_constraint("fk_assessment_questions_pack_id_assessment_question_packs", "assessment_questions", type_="foreignkey")
    op.drop_column("assessment_questions", "rubric_json")
    op.drop_column("assessment_questions", "expected_reasoning")
    op.drop_column("assessment_questions", "llm_metadata_json")
    op.drop_column("assessment_questions", "generation_prompt_version")
    op.drop_column("assessment_questions", "generation_source")
    op.drop_column("assessment_questions", "pack_id")

    op.drop_table("assessment_question_packs")

    op.drop_constraint("fk_assessment_sessions_target_concept_id_knowledge_concepts", "assessment_sessions", type_="foreignkey")
    op.drop_column("assessment_sessions", "max_nodes_visited")
    op.drop_column("assessment_sessions", "max_questions")
    op.drop_column("assessment_sessions", "max_depth")
    op.drop_column("assessment_sessions", "decision_state_json")
    op.drop_column("assessment_sessions", "graph_scope_json")
    op.drop_column("assessment_sessions", "source")
    op.drop_column("assessment_sessions", "target_concept_id")

    op.drop_index("uq_learning_goals_active_user", table_name="learning_goals")
    op.drop_constraint("fk_learning_goals_resolution_id_learning_goal_resolutions", "learning_goals", type_="foreignkey")
    op.drop_column("learning_goals", "completed_at")
    op.drop_column("learning_goals", "archived_at")
    op.drop_column("learning_goals", "cancelled_at")
    op.drop_column("learning_goals", "resolution_id")

    op.drop_table("image_assets")
    op.drop_table("learning_goal_resolutions")
