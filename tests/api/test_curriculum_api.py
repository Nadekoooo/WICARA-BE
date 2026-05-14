from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.modules.accounts.dependencies import get_optional_current_account
from app.modules.accounts.models import UserAccount
from app.modules.curriculum.models import KnowledgeConcept
from app.modules.learning.models import LearnerConceptState


ACCOUNT_ID = UUID("33333333-3333-4333-8333-333333333333")
TARGET_CONCEPT = "km_d_matematika_bilangan_rasional"


def test_get_subjects_returns_seeded_subject_catalog(client, seeded_curriculum):
    response = client.get("/api/v1/subjects")

    assert response.status_code == 200
    payload = response.json()
    assert [subject["code"] for subject in payload["items"]] == [
        "matematika",
        "ipas",
        "ipa",
        "fisika",
        "kimia",
        "biologi",
    ]
    assert payload["items"][0]["name"] == "Matematika"
    assert payload["items"][0]["metadata"]["curriculum"] == "kurikulum_merdeka"


def test_get_knowledge_map_returns_mobile_ready_kurikulum_graph(client, seeded_curriculum):
    response = client.get("/api/v1/knowledge-map?subject=matematika")

    assert response.status_code == 200
    payload = response.json()

    assert payload["subject"]["code"] == "matematika"
    assert payload["graph"]["title"] == "Kurikulum Merdeka Matematika Knowledge Map"
    assert payload["graph"]["top_down"] is True
    assert payload["groups"][0] == {"label": "Fase A / Aljabar", "x": 28.0}

    nodes_by_id = {node["id"]: node for node in payload["nodes"]}
    assert nodes_by_id["km_d_matematika_bilangan_bulat"]["status"] == "active"
    assert nodes_by_id["km_d_matematika_bilangan_bulat"]["status_label"] == "IN PROGRESS"
    assert nodes_by_id["km_d_matematika_bilangan_bulat"]["metadata"]["preview_status_only"] is True
    assert nodes_by_id["km_d_matematika_bilangan_bulat"]["group"] == "Fase D / Bilangan"

    edges = {(edge["from"], edge["to"], edge["edge_type"]) for edge in payload["edges"]}
    assert (
        "km_d_matematika_bilangan_bulat",
        "km_d_matematika_bilangan_rasional",
        "prerequisite",
    ) in edges


def test_get_knowledge_map_supports_math_alias(client, seeded_curriculum):
    response = client.get("/api/v1/knowledge-map?subject=math")

    assert response.status_code == 200
    assert response.json()["subject"]["code"] == "matematika"


def test_get_knowledge_map_returns_science_subject_graph(client, seeded_curriculum):
    response = client.get("/api/v1/knowledge-map?subject=kimia")

    assert response.status_code == 200
    payload = response.json()
    assert payload["subject"]["code"] == "kimia"
    assert payload["nodes"]
    assert payload["groups"]


def test_get_concept_detail_returns_mock_mastery_and_relations(
    client,
    seeded_curriculum,
):
    response = client.get(
        "/api/v1/knowledge-map/concepts/km_d_matematika_bilangan_rasional"
        "?subject=matematika"
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["concept"]["id"] == "km_d_matematika_bilangan_rasional"
    assert payload["subject"]["code"] == "matematika"
    assert payload["metadata"]["mock_mastery"] is True
    assert isinstance(payload["mastery_confidence"], float)

    prerequisite_ids = {item["id"] for item in payload["prerequisites"]}
    related_ids = {item["id"] for item in payload["related_concepts"]}
    assert "km_d_matematika_bilangan_bulat" in prerequisite_ids
    assert "km_d_matematika_bilangan_irasional" in related_ids


def test_authenticated_knowledge_map_uses_low_learner_mastery_as_gap(
    client,
    seeded_curriculum,
):
    _override_optional_account(
        client,
        concept_code=TARGET_CONCEPT,
        mastery_score=0.25,
        confidence_score=0.2,
        evidence_count=2,
        status="review_due",
    )

    response = client.get("/api/v1/knowledge-map?subject=matematika")

    assert response.status_code == 200
    node = _node_by_id(response.json(), TARGET_CONCEPT)
    assert node["status"] == "gap"
    assert node["status_label"] == "GAP"
    assert node["metadata"]["personalization_source"] == "learner_concept_state"
    assert node["metadata"]["learner_state_present"] is True
    assert node["metadata"]["mock_mastery"] is False
    assert node["metadata"]["mastery_score"] == 0.25
    assert node["metadata"]["status_reason"] == "low_mastery_score"


def test_authenticated_concept_detail_uses_real_mastery_confidence(
    client,
    seeded_curriculum,
):
    _override_optional_account(
        client,
        concept_code=TARGET_CONCEPT,
        mastery_score=0.82,
        confidence_score=0.74,
        evidence_count=4,
        status="mastered",
    )

    response = client.get(
        f"/api/v1/knowledge-map/concepts/{TARGET_CONCEPT}?subject=matematika"
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["concept"]["status"] == "mastered"
    assert payload["concept"]["status_label"] == "MASTERED"
    assert payload["mastery_confidence"] == 0.74
    assert payload["metadata"]["mock_mastery"] is False
    assert payload["metadata"]["source"] == "learner_concept_state"
    assert payload["metadata"]["evidence_count"] == 4


def test_authenticated_knowledge_map_marks_due_review_from_next_review_at(
    client,
    seeded_curriculum,
):
    _override_optional_account(
        client,
        concept_code=TARGET_CONCEPT,
        mastery_score=0.81,
        confidence_score=0.75,
        evidence_count=3,
        status="mastered",
        next_review_at=datetime.now(UTC) - timedelta(days=1),
    )

    response = client.get("/api/v1/knowledge-map?subject=matematika")

    assert response.status_code == 200
    node = _node_by_id(response.json(), TARGET_CONCEPT)
    assert node["status"] == "review"
    assert node["status_label"] == "REVIEW"
    assert node["metadata"]["status_reason"] == "review_due"


def test_authenticated_knowledge_map_distinguishes_unmeasured_from_gap(
    client,
    seeded_curriculum,
):
    _override_optional_account(client)

    response = client.get("/api/v1/knowledge-map?subject=matematika")

    assert response.status_code == 200
    node = _node_by_id(response.json(), TARGET_CONCEPT)
    assert node["status"] == "locked"
    assert node["metadata"]["personalization_source"] == "no_learner_state"
    assert node["metadata"]["learner_state_present"] is False
    assert node["metadata"]["evidence_count"] == 0


def test_get_concept_detail_unknown_concept_returns_404(client, seeded_curriculum):
    response = client.get("/api/v1/knowledge-map/concepts/unknown")

    assert response.status_code == 404


def test_get_knowledge_map_unknown_subject_returns_404(client, seeded_curriculum):
    response = client.get("/api/v1/knowledge-map?subject=history")

    assert response.status_code == 404


def _node_by_id(payload: dict, node_id: str) -> dict:
    return next(node for node in payload["nodes"] if node["id"] == node_id)


def _override_optional_account(
    client,
    *,
    concept_code: str | None = None,
    mastery_score: float = 0.0,
    confidence_score: float = 0.0,
    evidence_count: int = 0,
    status: str = "ready",
    next_review_at: datetime | None = None,
) -> None:
    def override_optional_current_account(
        session: Session = Depends(get_session),
    ) -> UserAccount:
        account = session.get(UserAccount, ACCOUNT_ID)
        if account is None:
            account = UserAccount(
                id=ACCOUNT_ID,
                supabase_user_id="supabase-user-curriculum",
                email="learner-curriculum@example.com",
                display_name="Curriculum User",
                provider_subject="supabase-user-curriculum",
            )
            session.add(account)
            session.flush()

        if concept_code is not None:
            concept = session.scalar(
                select(KnowledgeConcept).where(KnowledgeConcept.code == concept_code)
            )
            assert concept is not None
            learner_state = session.scalar(
                select(LearnerConceptState).where(
                    LearnerConceptState.user_id == account.id,
                    LearnerConceptState.concept_id == concept.id,
                )
            )
            if learner_state is None:
                learner_state = LearnerConceptState(
                    user_id=account.id,
                    concept_id=concept.id,
                )
                session.add(learner_state)
            learner_state.status = status
            learner_state.mastery_score = mastery_score
            learner_state.confidence_score = confidence_score
            learner_state.evidence_count = evidence_count
            learner_state.last_evaluated_at = datetime.now(UTC)
            learner_state.next_review_at = next_review_at

        session.commit()
        session.refresh(account)
        return account

    client.app.dependency_overrides[get_optional_current_account] = (
        override_optional_current_account
    )
