from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select

from app.modules.accounts.models import LearnerProfile, UserAccount
from app.modules.curriculum.models import KnowledgeConcept, Subject
from app.modules.curriculum.seed import seed_curriculum
from app.modules.learning.models import LearnerConceptState, LearningGoal, LearningTrack, TrackModule
from app.modules.question_bank.models import QuestionBankImportRun, QuestionBankItem
from app.modules.question_bank.service import (
    default_seeds_dir,
    ensure_question_bank_seeded,
    import_seed_file,
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


def test_daily_selector_resolves_latest_non_completed_track(db_session):
    seed_curriculum(db_session)
    import_seed_directory(db_session)
    user = _create_user_with_profile(db_session)
    subject, concept = _math_subject_and_concept(db_session)
    older_track = _create_track_for_concept(
        db_session,
        user=user,
        subject=subject,
        concept=concept,
        raw_topic="older rational number track",
        updated_at=datetime.now(UTC) - timedelta(days=1),
    )
    latest_track = _create_track_for_concept(
        db_session,
        user=user,
        subject=subject,
        concept=concept,
        raw_topic="latest rational number track",
        updated_at=datetime.now(UTC),
    )
    older_track.status = "completed"
    db_session.commit()
    db_session.refresh(user)

    learner_step, selected = select_daily_questions(db_session, user=user)

    assert learner_step.active_track_id == latest_track.id
    assert learner_step.active_module_id is not None
    assert learner_step.active_concept_id == concept.id
    assert selected
    assert selected[0].slot == "active_module"
    assert selected[0].item.concept_id == concept.id


def test_question_bank_seeded_backfills_missing_preferred_language(db_session):
    seed_curriculum(db_session)
    for seed_path in default_seeds_dir().glob("mathematics.*.v1.json"):
        if ".id." not in seed_path.name:
            import_seed_file(db_session, path=seed_path, strict=False)
    db_session.commit()

    id_item_count = db_session.scalar(
        select(func.count())
        .select_from(QuestionBankItem)
        .where(QuestionBankItem.language == "id")
    )
    assert id_item_count == 0

    ensure_question_bank_seeded(db_session, preferred_language="id")

    id_item_count = db_session.scalar(
        select(func.count())
        .select_from(QuestionBankItem)
        .where(QuestionBankItem.language == "id")
    )
    assert id_item_count > 0


def test_daily_selector_uses_indonesian_bank_items_for_indonesian_profile(db_session):
    seed_curriculum(db_session)
    import_seed_directory(db_session)
    user = _create_user_with_profile(db_session, preferred_language="id")

    learner_step, selected = select_daily_questions(db_session, user=user)

    assert learner_step.preferred_language == "id"
    assert selected
    assert {choice.item.language for choice in selected} == {"id"}
    assert not selected[0].item.prompt.startswith(("A quick review", "Which topic"))


def test_daily_selector_does_not_import_question_bank_on_read_path(db_session):
    seed_curriculum(db_session)
    user = _create_user_with_profile(db_session)

    _learner_step, selected = select_daily_questions(db_session, user=user)
    item_count = db_session.scalar(select(func.count()).select_from(QuestionBankItem))

    assert selected == []
    assert item_count == 0


def _create_user_with_profile(db_session, *, preferred_language: str = "en") -> UserAccount:
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
            preferred_language=preferred_language,
            selected_subjects=["mathematics"],
            onboarding_completed=True,
        )
    )
    db_session.commit()
    db_session.refresh(user)
    return user


def _math_subject_and_concept(db_session):
    subject = db_session.scalar(select(Subject).where(Subject.code == "matematika"))
    assert subject is not None
    concept = db_session.scalar(
        select(KnowledgeConcept).where(KnowledgeConcept.code == "km_d_matematika_bilangan_rasional")
    )
    assert concept is not None
    return subject, concept


def _create_track_for_concept(
    db_session,
    *,
    user: UserAccount,
    subject,
    concept: KnowledgeConcept,
    raw_topic: str,
    updated_at: datetime,
) -> LearningTrack:
    goal = LearningGoal(
        user_id=user.id,
        subject_id=subject.id,
        raw_topic=raw_topic,
        normalized_topic=raw_topic,
        status="pretest_ready",
    )
    db_session.add(goal)
    db_session.flush()
    track = LearningTrack(
        user_id=user.id,
        learning_goal_id=goal.id,
        title=raw_topic,
        subtitle="test track",
        status="in_progress",
        progress_percent=0,
        created_at=updated_at,
        updated_at=updated_at,
    )
    db_session.add(track)
    db_session.flush()
    db_session.add(
        TrackModule(
            track_id=track.id,
            concept_id=concept.id,
            title="Active module",
            description="",
            estimated_minutes=10,
            difficulty_label="Medium",
            sort_order=1,
            status="ready",
        )
    )
    db_session.commit()
    return track
