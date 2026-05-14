from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.accounts.models import UserAccount
from app.modules.curriculum.models import ConceptEdge, KnowledgeConcept, Subject
from app.modules.curriculum.schemas import (
    ConceptDetailResponse,
    ConceptRelation,
    KnowledgeMapEdge,
    KnowledgeMapGraph,
    KnowledgeMapGroup,
    KnowledgeMapNode,
    KnowledgeMapResponse,
    SubjectRead,
)
from app.modules.curriculum.kurikulum_merdeka import canonical_subject_code
from app.modules.learning.models import LearnerConceptState

STATUS_LABELS = {
    "mastered": "MASTERED",
    "active": "IN PROGRESS",
    "review": "REVIEW",
    "review_due": "REVIEW",
    "ready": "READY",
    "gap": "GAP",
    "locked": "LOCKED",
}


def list_active_subjects(session: Session) -> list[Subject]:
    return list(
        session.scalars(
            select(Subject)
            .where(Subject.is_active.is_(True))
            .order_by(Subject.display_order, Subject.name)
        )
    )


def subject_to_schema(subject: Subject) -> SubjectRead:
    return SubjectRead(
        id=subject.id,
        code=subject.code,
        name=subject.name,
        description=subject.description,
        is_active=subject.is_active,
        display_order=subject.display_order,
        metadata=subject.metadata_json or {},
    )


def get_knowledge_map(
    session: Session,
    *,
    subject_code: str,
    user: UserAccount | None = None,
) -> KnowledgeMapResponse | None:
    normalized_code = canonical_subject_code(subject_code)
    subject = session.scalar(
        select(Subject).where(
            Subject.code == normalized_code,
            Subject.is_active.is_(True),
        )
    )
    if subject is None:
        return None

    concepts = list(
        session.scalars(
            select(KnowledgeConcept)
            .where(KnowledgeConcept.subject_id == subject.id)
            .options(selectinload(KnowledgeConcept.outgoing_edges))
            .order_by(KnowledgeConcept.display_order, KnowledgeConcept.title)
        )
    )
    if not concepts:
        return None

    concept_by_id = {concept.id: concept for concept in concepts}
    concept_by_code = {concept.code: concept for concept in concepts}
    edges = list(
        session.scalars(
            select(ConceptEdge)
            .where(
                ConceptEdge.from_concept_id.in_(concept_by_id),
                ConceptEdge.to_concept_id.in_(concept_by_id),
            )
            .order_by(ConceptEdge.edge_type, ConceptEdge.created_at)
        )
    )
    state_by_concept = _learner_states_for_concepts(
        session,
        user=user,
        concept_ids=list(concept_by_id),
    )
    concepts_with_prerequisites = {
        edge.to_concept_id
        for edge in edges
        if edge.edge_type == "prerequisite"
    }

    graph_metadata = subject.metadata_json.get("graph", {}) if subject.metadata_json else {}
    groups_payload = graph_metadata.get("groups", [])
    groups = [
        KnowledgeMapGroup(label=str(group["label"]), x=float(group["x"]))
        for group in groups_payload
    ]

    return KnowledgeMapResponse(
        subject=subject_to_schema(subject),
        graph=KnowledgeMapGraph(
            title=str(graph_metadata.get("title", f"{subject.name} Knowledge Map")),
            width=float(graph_metadata.get("width", 1200)),
            height=float(graph_metadata.get("height", 600)),
            top_down=bool(graph_metadata.get("top_down", True)),
        ),
        groups=groups,
        nodes=[
            _concept_to_node(
                concept,
                groups,
                state=state_by_concept.get(concept.id),
                is_personalized=user is not None,
                has_prerequisites=concept.id in concepts_with_prerequisites,
            )
            for concept in concepts
        ],
        edges=[
            KnowledgeMapEdge(
                id=edge.id,
                from_node=concept_by_code[concept_by_id[edge.from_concept_id].code].code,
                to=concept_by_code[concept_by_id[edge.to_concept_id].code].code,
                edge_type=edge.edge_type,
                weight=edge.weight,
                metadata=edge.metadata_json or {},
            )
            for edge in edges
        ],
    )


def get_concept_detail(
    session: Session,
    *,
    concept_code: str,
    subject_code: str | None = None,
    user: UserAccount | None = None,
) -> ConceptDetailResponse | None:
    statement = (
        select(KnowledgeConcept)
        .join(KnowledgeConcept.subject)
        .options(selectinload(KnowledgeConcept.subject))
        .where(KnowledgeConcept.code == concept_code)
    )
    if subject_code:
        statement = statement.where(Subject.code == canonical_subject_code(subject_code))

    concept = session.scalar(statement)
    if concept is None:
        return None

    incoming_edges = list(
        session.scalars(
            select(ConceptEdge)
            .where(ConceptEdge.to_concept_id == concept.id)
            .options(
                selectinload(ConceptEdge.from_concept).selectinload(
                    KnowledgeConcept.subject
                )
            )
            .order_by(ConceptEdge.edge_type, ConceptEdge.weight.desc())
        )
    )
    outgoing_edges = list(
        session.scalars(
            select(ConceptEdge)
            .where(ConceptEdge.from_concept_id == concept.id)
            .options(
                selectinload(ConceptEdge.to_concept).selectinload(
                    KnowledgeConcept.subject
                )
            )
            .order_by(ConceptEdge.edge_type, ConceptEdge.weight.desc())
        )
    )

    prerequisite_concepts = [
        edge.from_concept
        for edge in incoming_edges
        if edge.from_concept.subject_id == concept.subject_id
    ]
    related_concept_models = [
        edge.to_concept
        for edge in outgoing_edges
        if edge.to_concept.subject_id == concept.subject_id
    ]
    cross_subject_concepts = [
        *[
            edge.from_concept
            for edge in incoming_edges
            if edge.from_concept.subject_id != concept.subject_id
        ],
        *[
            edge.to_concept
            for edge in outgoing_edges
            if edge.to_concept.subject_id != concept.subject_id
        ],
    ]
    state_by_concept = _learner_states_for_concepts(
        session,
        user=user,
        concept_ids=[
            concept.id,
            *[item.id for item in prerequisite_concepts],
            *[item.id for item in related_concept_models],
            *[item.id for item in cross_subject_concepts],
        ],
    )
    concept_state = state_by_concept.get(concept.id)

    prerequisites = [
        _concept_relation(
            item,
            state=state_by_concept.get(item.id),
            is_personalized=user is not None,
            has_prerequisites=False,
        )
        for item in prerequisite_concepts
    ]
    related_concepts = [
        _concept_relation(
            item,
            state=state_by_concept.get(item.id),
            is_personalized=user is not None,
            has_prerequisites=True,
        )
        for item in related_concept_models
    ]
    cross_subject_connections = [
        _concept_relation(
            item,
            state=state_by_concept.get(item.id),
            is_personalized=user is not None,
            has_prerequisites=True,
        )
        for item in cross_subject_concepts
    ]

    return ConceptDetailResponse(
        concept=_concept_to_node(
            concept,
            _groups_for_subject(concept.subject),
            state=concept_state,
            is_personalized=user is not None,
            has_prerequisites=bool(prerequisite_concepts),
        ),
        subject=subject_to_schema(concept.subject),
        mastery_confidence=_mastery_confidence_for_detail(
            concept,
            state=concept_state,
            is_personalized=user is not None,
        ),
        prerequisites=prerequisites[:5],
        related_concepts=related_concepts[:5],
        cross_subject_connections=cross_subject_connections[:5],
        metadata=_concept_detail_metadata(
            concept,
            state=concept_state,
            is_personalized=user is not None,
            has_prerequisites=bool(prerequisite_concepts),
        ),
    )


def _concept_to_node(
    concept: KnowledgeConcept,
    groups: list[KnowledgeMapGroup],
    *,
    state: LearnerConceptState | None = None,
    is_personalized: bool = False,
    has_prerequisites: bool = False,
) -> KnowledgeMapNode:
    metadata: dict[str, Any] = concept.metadata_json or {}
    status, reason = _status_for_concept(
        concept,
        state=state,
        is_personalized=is_personalized,
        has_prerequisites=has_prerequisites,
    )
    response_metadata = _node_metadata(
        concept,
        state=state,
        is_personalized=is_personalized,
        status_reason=reason,
        has_prerequisites=has_prerequisites,
    )
    return KnowledgeMapNode(
        id=concept.code,
        concept_id=concept.id,
        code=concept.code,
        label=concept.title,
        title=concept.title,
        description=concept.description,
        grade_band=concept.grade_band,
        status=status,
        status_label=(
            _personalized_status_label(status)
            if is_personalized
            else _concept_status_label(metadata, status)
        ),
        x=concept.layout_x,
        y=concept.layout_y,
        group=_nearest_group_label(concept.layout_x, groups),
        metadata=response_metadata,
    )


def _concept_relation(
    concept: KnowledgeConcept,
    *,
    state: LearnerConceptState | None = None,
    is_personalized: bool = False,
    has_prerequisites: bool = False,
) -> ConceptRelation:
    metadata: dict[str, Any] = concept.metadata_json or {}
    status, _reason = _status_for_concept(
        concept,
        state=state,
        is_personalized=is_personalized,
        has_prerequisites=has_prerequisites,
    )
    return ConceptRelation(
        id=concept.code,
        code=concept.code,
        label=concept.title,
        subject_code=concept.subject.code,
        subject_name=concept.subject.name,
        status=status,
        status_label=(
            _personalized_status_label(status)
            if is_personalized
            else _concept_status_label(metadata, status)
        ),
    )


def _groups_for_subject(subject: Subject) -> list[KnowledgeMapGroup]:
    graph_metadata = subject.metadata_json.get("graph", {}) if subject.metadata_json else {}
    groups_payload = graph_metadata.get("groups", [])
    return [
        KnowledgeMapGroup(label=str(group["label"]), x=float(group["x"]))
        for group in groups_payload
    ]


def _learner_states_for_concepts(
    session: Session,
    *,
    user: UserAccount | None,
    concept_ids: list[UUID],
) -> dict[UUID, LearnerConceptState]:
    if user is None or not concept_ids:
        return {}

    return {
        state.concept_id: state
        for state in session.scalars(
            select(LearnerConceptState).where(
                LearnerConceptState.user_id == user.id,
                LearnerConceptState.concept_id.in_(concept_ids),
            )
        )
    }


def _status_for_concept(
    concept: KnowledgeConcept,
    *,
    state: LearnerConceptState | None,
    is_personalized: bool,
    has_prerequisites: bool,
) -> tuple[str, str]:
    metadata: dict[str, Any] = concept.metadata_json or {}
    curriculum_status = str(metadata.get("default_status", "ready"))
    if not is_personalized:
        return _normalize_status(curriculum_status), "curriculum_default"

    if state is None:
        if has_prerequisites:
            return "locked", "no_learner_evidence_prerequisites_unknown"
        return "ready", "no_learner_evidence_root_concept"

    evidence_count = state.evidence_count or 0
    mastery_score = _clamp_score(state.mastery_score)
    stored_status = _normalize_status(state.status)
    if evidence_count <= 0:
        return "ready", "learner_state_without_evidence"
    if mastery_score < 0.4:
        return "gap", "low_mastery_score"
    if _is_review_due(state.next_review_at):
        return "review", "review_due"
    if stored_status in {"review", "review_due"}:
        return "review", "stored_review_status"
    if stored_status == "active":
        return "active", "stored_active_status"
    if stored_status == "mastered" or mastery_score >= 0.7:
        return "mastered", "strong_mastery_score"
    if mastery_score < 0.55:
        return "review", "moderate_low_mastery_score"
    return "ready", "developing_mastery_score"


def _node_metadata(
    concept: KnowledgeConcept,
    *,
    state: LearnerConceptState | None,
    is_personalized: bool,
    status_reason: str,
    has_prerequisites: bool,
) -> dict[str, Any]:
    metadata: dict[str, Any] = dict(concept.metadata_json or {})
    if not is_personalized:
        return metadata

    metadata.update(
        {
            "personalization_source": (
                "learner_concept_state" if state is not None else "no_learner_state"
            ),
            "learner_state_present": state is not None,
            "status_reason": status_reason,
            "has_prerequisites": has_prerequisites,
            "curriculum_default_status": str(metadata.get("default_status", "ready")),
            "mock_mastery": False,
        }
    )
    if state is None:
        metadata.update(
            {
                "mastery_score": None,
                "confidence_score": None,
                "evidence_count": 0,
                "last_evaluated_at": None,
                "next_review_at": None,
            }
        )
        return metadata

    metadata.update(
        {
            "stored_status": state.status,
            "mastery_score": round(_clamp_score(state.mastery_score), 4),
            "confidence_score": round(_clamp_score(state.confidence_score), 4),
            "evidence_count": state.evidence_count or 0,
            "last_evaluated_at": _datetime_to_iso(state.last_evaluated_at),
            "next_review_at": _datetime_to_iso(state.next_review_at),
        }
    )
    return metadata


def _concept_detail_metadata(
    concept: KnowledgeConcept,
    *,
    state: LearnerConceptState | None,
    is_personalized: bool,
    has_prerequisites: bool,
) -> dict[str, Any]:
    if not is_personalized:
        return {
            "mock_mastery": True,
            "source": "curriculum_graph",
        }

    _status, reason = _status_for_concept(
        concept,
        state=state,
        is_personalized=True,
        has_prerequisites=has_prerequisites,
    )
    return {
        "mock_mastery": False,
        "source": "learner_concept_state" if state is not None else "no_learner_state",
        "learner_state_present": state is not None,
        "status_reason": reason,
        "mastery_score": round(_clamp_score(state.mastery_score), 4) if state else None,
        "confidence_score": round(_clamp_score(state.confidence_score), 4) if state else None,
        "evidence_count": (state.evidence_count or 0) if state else 0,
        "last_evaluated_at": _datetime_to_iso(state.last_evaluated_at) if state else None,
        "next_review_at": _datetime_to_iso(state.next_review_at) if state else None,
    }


def _mastery_confidence_for_detail(
    concept: KnowledgeConcept,
    *,
    state: LearnerConceptState | None,
    is_personalized: bool,
) -> float:
    if not is_personalized:
        return _mock_mastery_confidence(concept)
    if state is None:
        return 0.0
    confidence = _clamp_score(state.confidence_score)
    return round(confidence if confidence > 0 else _clamp_score(state.mastery_score), 4)


def _mock_mastery_confidence(concept: KnowledgeConcept) -> float:
    metadata: dict[str, Any] = concept.metadata_json or {}
    status = str(metadata.get("default_status", "ready"))
    return {
        "mastered": 0.92,
        "active": 0.62,
        "review": 0.48,
        "ready": 0.34,
        "gap": 0.18,
        "locked": 0.08,
    }.get(status, 0.34)


def _nearest_group_label(
    x: float | None,
    groups: list[KnowledgeMapGroup],
) -> str | None:
    if x is None or not groups:
        return None
    return min(groups, key=lambda group: abs(group.x - x)).label


def _concept_status_label(metadata: dict[str, Any], status: str) -> str:
    if metadata.get("preview_status_only"):
        return STATUS_LABELS.get(status, status.upper())

    if metadata.get("source_curriculum_graph"):
        phase = str(metadata.get("phase") or "").strip()
        grade_range = str(metadata.get("grade_range") or "").strip()
        if phase and grade_range:
            return f"Fase {phase} / {grade_range}"
        if phase:
            return f"Fase {phase}"

    return STATUS_LABELS.get(status, status.upper())


def _personalized_status_label(status: str) -> str:
    return STATUS_LABELS.get(status, status.upper())


def _normalize_status(status: str) -> str:
    normalized = status.strip().lower().replace("-", "_").replace(" ", "_")
    return {
        "review_due": "review_due",
        "in_progress": "active",
        "unknown": "locked",
    }.get(normalized, normalized if normalized in STATUS_LABELS else "ready")


def _clamp_score(value: float | None) -> float:
    if value is None:
        return 0.0
    return max(0.0, min(1.0, float(value)))


def _is_review_due(value: datetime | None) -> bool:
    if value is None:
        return False
    candidate = value if value.tzinfo else value.replace(tzinfo=UTC)
    return candidate <= datetime.now(UTC)


def _datetime_to_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    candidate = value if value.tzinfo else value.replace(tzinfo=UTC)
    return candidate.isoformat()
