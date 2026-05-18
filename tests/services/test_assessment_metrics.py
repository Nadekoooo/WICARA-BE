from app.modules.assessments.metrics import calculate_evidence_score
from app.modules.accounts.models import UserAccount
from app.modules.curriculum.models import KnowledgeConcept, Subject
from app.modules.curriculum.service import _latest_posttest_pass_by_concept
from app.modules.learning.models import (
    AssessmentAttempt,
    AssessmentOption,
    AssessmentQuestion,
    AssessmentSession,
)


def test_evidence_score_uses_answer_only_when_no_extra_evidence():
    assert calculate_evidence_score(answer_score=1.0, reasoning_score=None, canvas_score=None) == 1.0
    assert calculate_evidence_score(answer_score=0.0, reasoning_score=None, canvas_score=None) == 0.0


def test_evidence_score_weights_reasoning_and_canvas():
    assert calculate_evidence_score(answer_score=1.0, reasoning_score=0.8, canvas_score=None) == 0.94
    assert calculate_evidence_score(answer_score=1.0, reasoning_score=None, canvas_score=0.5) == 0.85
    assert calculate_evidence_score(answer_score=1.0, reasoning_score=0.8, canvas_score=0.5) == 0.875


def test_wrong_answer_remains_bounded_even_with_strong_reasoning():
    assert calculate_evidence_score(answer_score=0.0, reasoning_score=0.8, canvas_score=None) == 0.24


def test_curriculum_posttest_gate_does_not_round_two_of_three_to_pass(db_session):
    user = UserAccount(
        supabase_user_id="metric-user",
        email="metric-user@example.com",
        display_name="Metric User",
        provider_subject="metric-user",
    )
    subject = Subject(code="metric", name="Metric", description="", is_active=True)
    db_session.add_all([user, subject])
    db_session.flush()
    concept = KnowledgeConcept(
        subject_id=subject.id,
        code="metric.posttest",
        title="Metric Posttest",
        description="Metric Posttest",
        display_order=1,
    )
    db_session.add(concept)
    db_session.flush()

    assessment = AssessmentSession(
        user_id=user.id,
        session_type="posttest",
        title="Posttest",
        status="completed",
        metadata_json={},
    )
    db_session.add(assessment)
    db_session.flush()

    for index, is_correct in enumerate([True, True, False], start=1):
        question = AssessmentQuestion(
            session_id=assessment.id,
            concept_id=concept.id,
            step_label="Posttest",
            topic="Metric Posttest",
            prompt=f"Question {index}",
            helper_text="",
            difficulty_label="Medium",
            sort_order=index,
        )
        db_session.add(question)
        db_session.flush()
        option = AssessmentOption(
            question_id=question.id,
            option_key="A",
            label="A",
            text="A",
            is_correct=is_correct,
            sort_order=1,
        )
        db_session.add(option)
        db_session.flush()
        score = 1.0 if is_correct else 0.0
        db_session.add(
            AssessmentAttempt(
                session_id=assessment.id,
                question_id=question.id,
                selected_option_id=option.id,
                confidence=8,
                score=score,
                is_correct=is_correct,
                answer_score=score,
                evidence_score=score,
            )
        )
    db_session.commit()

    assert _latest_posttest_pass_by_concept(db_session, user=user, concept_ids=[concept.id]) == {
        concept.id: False
    }
