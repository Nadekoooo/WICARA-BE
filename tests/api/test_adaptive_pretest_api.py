from __future__ import annotations

from contextlib import contextmanager
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.modules.accounts.dependencies import get_current_account
from app.modules.accounts.models import UserAccount
from app.modules.curriculum.models import ConceptEdge, KnowledgeConcept, Subject
from app.modules.learning.models import (
    AssessmentAttempt,
    AssessmentQuestionPack,
    AssessmentSession,
    LearningGoal,
    TrackModule,
)
from app.modules.learning_goal_resolution.models import LearningGoalResolution

ACCOUNT_ID = UUID("33333333-3333-4333-8333-333333333333")


def test_resolve_does_not_create_goal_and_confirm_enforces_active_lock(client):
    _override_account(client)

    resolve_response = client.post(
        "/api/v1/learning-goals/resolve",
        json={
            "raw_query": "aku mau belajar kali-kalian",
            "subject_code": "math",
            "education_level": "sd",
            "grade_level": "3",
            "language": "id",
        },
    )

    assert resolve_response.status_code == 200
    resolved = resolve_response.json()
    assert resolved["status"] == "needs_confirmation"
    assert resolved["suggested_concept"]["concept_code"] == "math.multiplication"

    with _session_for_client(client) as session:
        assert session.scalar(select(LearningGoal).where(LearningGoal.user_id == ACCOUNT_ID)) is None

    confirm_response = client.post(
        f"/api/v1/learning-goals/resolve/{resolved['resolution_id']}/confirm"
    )
    assert confirm_response.status_code == 200
    goal = confirm_response.json()
    assert goal["status"] == "confirmed"

    second = client.post(
        "/api/v1/learning-goals/resolve",
        json={"raw_query": "belajar penjumlahan", "subject_code": "math"},
    )
    assert second.status_code == 200
    conflict = client.post(
        f"/api/v1/learning-goals/resolve/{second.json()['resolution_id']}/confirm"
    )
    assert conflict.status_code == 409
    assert conflict.json()["detail"]["error"] == "ACTIVE_LEARNING_GOAL_EXISTS"


def test_resolve_tolerates_null_llm_confidence(client, monkeypatch):
    _override_account(client)

    async def fake_resolve_with_ai(*, raw_query, candidates):
        return {
            "status": "needs_confirmation",
            "concept_code": candidates[0].concept.code,
            "confidence": None,
            "provider": "test",
            "model": "test",
        }

    from app.modules.learning_goal_resolution.router import service

    monkeypatch.setattr(service, "_resolve_with_ai", fake_resolve_with_ai)
    response = client.post(
        "/api/v1/learning-goals/resolve",
        json={"raw_query": "aku mau belajar kali-kalian", "subject_code": "math"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "needs_confirmation"
    assert payload["confidence"] > 0


def test_resolve_needs_clarification_when_query_has_no_candidate_signal(client):
    _override_account(client)

    response = client.post(
        "/api/v1/learning-goals/resolve",
        json={
            "raw_query": "zzzzzz topik tidak ada",
            "subject_code": "math",
            "language": "en",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "needs_clarification"
    assert payload["suggested_concept"] is None
    assert "more specific" in payload["clarification_question"]


def test_resolve_allows_foundational_node_for_higher_grade_user(client):
    _override_account(client)

    response = client.post(
        "/api/v1/learning-goals/resolve",
        json={
            "raw_query": "aku mau refresh perkalian dasar",
            "subject_code": "math",
            "education_level": "senior_high",
            "grade_level": "11",
            "language": "id",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "needs_confirmation"
    assert payload["search_scope"] == "subject_all_grades"
    assert payload["suggested_concept"]["concept_code"] == "math.multiplication"
    assert payload["suggested_concept"]["grade_relation"] == "below_current_level"
    assert "fondasi" in payload["suggested_concept"]["level_note"]


def test_pretest_start_is_idempotent_and_generates_target_pack(client):
    _override_account(client)
    learning_goal_id = _confirmed_goal_id(client)

    first = client.post(
        "/api/v1/pretests/start",
        json={"learning_goal_id": learning_goal_id, "depth": 2},
    )
    second = client.post(
        "/api/v1/pretests/start",
        json={"learning_goal_id": learning_goal_id, "depth": 2},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["session_id"] == second.json()["session_id"]
    assert first.json()["current_question"]["difficulty"] == "medium"

    with _session_for_client(client) as session:
        packs = list(session.scalars(select(AssessmentQuestionPack)))
        assert len(packs) == 1
        questions = first.json()["decision_state"]["generated_packs"]
        target_code = first.json()["target_concept"]["concept_code"]
        assert set(questions[target_code]["questions"]) == {"easy", "medium", "hard"}


def test_answers_select_from_pack_generate_prereq_pack_and_reject_duplicate(client):
    _override_account(client)
    learning_goal_id = _confirmed_goal_id(client)
    start = client.post("/api/v1/pretests/start", json={"learning_goal_id": learning_goal_id})
    payload = start.json()
    question = payload["current_question"]
    wrong_option = next(option for option in question["options"] if option["label"] != "B")

    answer = client.post(
        f"/api/v1/pretests/{payload['session_id']}/answers",
        json={
            "question_id": question["id"],
            "selected_option_id": wrong_option["id"],
            "typed_reasoning": "",
        },
    )
    duplicate = client.post(
        f"/api/v1/pretests/{payload['session_id']}/answers",
        json={
            "question_id": question["id"],
            "selected_option_id": wrong_option["id"],
        },
    )

    assert answer.status_code == 200
    assert answer.json()["next_question"]["difficulty"] == "easy"
    assert answer.json()["next_question"]["pack_id"] == question["pack_id"]
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"]["error"] == "QUESTION_ALREADY_ANSWERED"

    easy_question = answer.json()["next_question"]
    easy_wrong = next(option for option in easy_question["options"] if option["label"] != "B")
    prereq_answer = client.post(
        f"/api/v1/pretests/{payload['session_id']}/answers",
        json={
            "question_id": easy_question["id"],
            "selected_option_id": easy_wrong["id"],
        },
    )

    assert prereq_answer.status_code == 200
    next_question = prereq_answer.json()["next_question"]
    assert next_question["difficulty"] == "medium"
    assert next_question["concept_code"] != question["concept_code"]

    with _session_for_client(client) as session:
        assert session.scalar(select(func.count()).select_from(AssessmentQuestionPack)) == 2


def test_finalize_and_path_selection_create_track(client):
    _override_account(client)
    learning_goal_id = _confirmed_goal_id(client)
    start = client.post("/api/v1/pretests/start", json={"learning_goal_id": learning_goal_id})
    session_id = start.json()["session_id"]
    question = start.json()["current_question"]
    correct = next(option for option in question["options"] if option["label"] == "B")

    first = client.post(
        f"/api/v1/pretests/{session_id}/answers",
        json={"question_id": question["id"], "selected_option_id": correct["id"]},
    )
    hard_question = first.json()["next_question"]
    hard_correct = next(option for option in hard_question["options"] if option["label"] == "B")
    done = client.post(
        f"/api/v1/pretests/{session_id}/answers",
        json={"question_id": hard_question["id"], "selected_option_id": hard_correct["id"]},
    )

    assert done.status_code == 200
    assert done.json()["next_action"]["type"] == "finalize"
    assert done.json()["diagnosis"]["recommended_path"] == "review_only"

    path = client.post(
        f"/api/v1/learning-goals/{learning_goal_id}/path-selection",
        json={"path_option": "review_only"},
    )

    assert path.status_code == 200
    assert path.json()["goal_status"] == "in_progress"
    assert path.json()["modules"]

    with _session_for_client(client) as session:
        goal = session.get(LearningGoal, UUID(learning_goal_id))
        assert goal.status == "in_progress"
        assert session.scalar(select(TrackModule).where(TrackModule.track_id == goal.track.id)) is not None


def test_cancel_abandons_active_pretest_and_releases_lock(client):
    _override_account(client)
    learning_goal_id = _confirmed_goal_id(client)
    start = client.post("/api/v1/pretests/start", json={"learning_goal_id": learning_goal_id})

    cancel = client.post(f"/api/v1/learning-goals/{learning_goal_id}/cancel")
    assert cancel.status_code == 200
    assert cancel.json()["status"] == "cancelled"

    with _session_for_client(client) as session:
        assessment = session.get(AssessmentSession, UUID(start.json()["session_id"]))
        assert assessment.status == "cancelled"

    resolve = client.post(
        "/api/v1/learning-goals/resolve",
        json={"raw_query": "belajar penjumlahan", "subject_code": "math"},
    )
    confirm = client.post(f"/api/v1/learning-goals/resolve/{resolve.json()['resolution_id']}/confirm")
    assert confirm.status_code == 200


def _confirmed_goal_id(client) -> str:
    response = client.post(
        "/api/v1/learning-goals/resolve",
        json={"raw_query": "aku mau belajar kali-kalian", "subject_code": "math"},
    )
    assert response.status_code == 200
    confirm = client.post(
        f"/api/v1/learning-goals/resolve/{response.json()['resolution_id']}/confirm"
    )
    assert confirm.status_code == 200
    return confirm.json()["learning_goal_id"]


def _override_account(client) -> None:
    def override_current_account(
        session: Session = Depends(get_session),
    ) -> UserAccount:
        account = session.get(UserAccount, ACCOUNT_ID)
        if account is None:
            account = UserAccount(
                id=ACCOUNT_ID,
                supabase_user_id="supabase-user-adaptive",
                email="learner-adaptive@example.com",
                display_name="Adaptive User",
                provider_subject="supabase-user-adaptive",
            )
            session.add(account)
            _seed_math_graph(session)
            session.commit()
        return account

    client.app.dependency_overrides[get_current_account] = override_current_account


def _seed_math_graph(session: Session) -> None:
    subject = session.scalar(select(Subject).where(Subject.code == "math"))
    if subject is None:
        subject = Subject(code="math", name="Matematika", description="", is_active=True)
        session.add(subject)
        session.flush()
    concepts = {}
    for index, (code, title) in enumerate(
        [
            ("math.addition", "Penjumlahan"),
            ("math.subtraction", "Pengurangan"),
            ("math.multiplication", "Perkalian"),
        ],
        start=1,
    ):
        concept = session.scalar(
            select(KnowledgeConcept).where(
                KnowledgeConcept.subject_id == subject.id,
                KnowledgeConcept.code == code,
            )
        )
        if concept is None:
            concept = KnowledgeConcept(
                subject_id=subject.id,
                code=code,
                title=title,
                description=title,
                grade_band="primary",
                display_order=index,
            )
            session.add(concept)
            session.flush()
        else:
            concept.grade_band = "primary"
        concepts[code] = concept
    for from_code, to_code in [
        ("math.addition", "math.subtraction"),
        ("math.subtraction", "math.multiplication"),
    ]:
        if session.scalar(
            select(ConceptEdge).where(
                ConceptEdge.from_concept_id == concepts[from_code].id,
                ConceptEdge.to_concept_id == concepts[to_code].id,
            )
        ) is None:
            session.add(
                ConceptEdge(
                    from_concept_id=concepts[from_code].id,
                    to_concept_id=concepts[to_code].id,
                    edge_type="prerequisite",
                    weight=0.9,
                )
            )


@contextmanager
def _session_for_client(client):
    override = client.app.dependency_overrides[get_session]
    generator = override()
    session = next(generator)
    try:
        yield session
    finally:
        generator.close()
