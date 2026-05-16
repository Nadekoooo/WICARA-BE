from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select

from app.modules.accounts.models import LearnerProfile, UserAccount
from app.modules.curriculum.models import KnowledgeConcept
from app.modules.curriculum.seed import seed_curriculum
from app.modules.learning.models import LearnerConceptState
from app.modules.question_bank.models import QuestionBankImportRun, QuestionBankItem
from app.modules.question_bank.service import (
    import_seed_directory,
    select_daily_questions,
)


ACCOUNT_ID = UUID("33333333-3333-4333-8333-333333333333")


def test_question_bank_seed_import_is_idempotent(db_session):
    seed_curriculum(db_session)

    first = import_seed_directory(db_session)
    item_count = db_session.scalar(select(func.count()).select_from(QuestionBankItem))

    second = import_seed_directory(db_session)

    assert first.files_processed >= 1
    assert first.imported_count > 0
    assert first.failed_count == 0
    assert item_count == first.imported_count
    assert second.imported_count == 0
    assert second.skipped_count == item_count


def test_question_bank_seed_import_can_run_without_commit(db_session):
    seed_curriculum(db_session, commit=False)

    summary = import_seed_directory(db_session, commit=False)
    in_transaction_count = db_session.scalar(select(func.count()).select_from(QuestionBankItem))

    db_session.rollback()
    persisted_item_count = db_session.scalar(select(func.count()).select_from(QuestionBankItem))
    persisted_run_count = db_session.scalar(select(func.count()).select_from(QuestionBankImportRun))

    assert summary.imported_count > 0
    assert in_transaction_count > 0
    assert persisted_item_count == 0
    assert persisted_run_count == 0


def test_daily_selector_prioritizes_due_learner_concept(db_session):
    seed_curriculum(db_session)
    import_seed_directory(db_session)
    user = _create_user_with_profile(db_session)
    concept = db_session.scalar(
        select(KnowledgeConcept).where(KnowledgeConcept.code == "km_d_matematika_bilangan_rasional")
    )
    assert concept is not None
    db_session.add(
        LearnerConceptState(
            user_id=user.id,
            concept_id=concept.id,
            status="review_due",
            mastery_score=0.21,
            confidence_score=0.28,
            evidence_count=2,
            last_evaluated_at=datetime.now(UTC) - timedelta(days=2),
            next_review_at=datetime.now(UTC) - timedelta(hours=1),
        )
    )
    db_session.commit()
    db_session.refresh(user)

    learner_step, selected = select_daily_questions(db_session, user=user)

    assert learner_step.subject.code == "matematika"
    assert learner_step.education_level == "junior_high"
    assert selected
    assert selected[0].slot == "due_review"
    assert selected[0].item.concept_code == "bilangan_rasional"
    assert "daily_quiz" in selected[0].item.assessment_types_json


def test_daily_selector_uses_fallback_slot_when_no_personalized_state_exists(db_session):
    seed_curriculum(db_session)
    import_seed_directory(db_session)
    user = _create_user_with_profile(db_session)

    _learner_step, selected = select_daily_questions(db_session, user=user)

    assert selected
    assert {item.slot for item in selected} == {"fallback"}


def test_daily_selector_does_not_import_question_bank_on_read_path(db_session):
    seed_curriculum(db_session)
    user = _create_user_with_profile(db_session)

    _learner_step, selected = select_daily_questions(db_session, user=user)
    item_count = db_session.scalar(select(func.count()).select_from(QuestionBankItem))

    assert selected == []
    assert item_count == 0


def _create_user_with_profile(db_session) -> UserAccount:
    user = UserAccount(
        id=ACCOUNT_ID,
        supabase_user_id="supabase-question-bank",
        email="learner-question-bank@example.com",
        display_name="Question Bank User",
        provider_subject="supabase-question-bank",
    )
    db_session.add(user)
    db_session.flush()
    db_session.add(
        LearnerProfile(
            user_id=user.id,
            full_name="Question Bank User",
            education_level="SMP",
            grade_level="Kelas 7",
            preferred_language="en",
            selected_subjects=["mathematics"],
            onboarding_completed=True,
        )
    )
    db_session.commit()
    db_session.refresh(user)
    return user
