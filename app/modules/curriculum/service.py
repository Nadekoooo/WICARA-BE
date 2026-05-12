from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.curriculum.models import ConceptEdge, KnowledgeConcept, Subject
from app.modules.curriculum.schemas import (
    KnowledgeMapEdge,
    KnowledgeMapGraph,
    KnowledgeMapGroup,
    KnowledgeMapNode,
    KnowledgeMapResponse,
    SubjectRead,
)

STATUS_LABELS = {
    "mastered": "MASTERED",
    "active": "IN PROGRESS",
    "review": "REVIEW",
    "ready": "READY",
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
) -> KnowledgeMapResponse | None:
    normalized_code = subject_code.strip().lower()
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
        nodes=[_concept_to_node(concept, groups) for concept in concepts],
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


def _concept_to_node(
    concept: KnowledgeConcept,
    groups: list[KnowledgeMapGroup],
) -> KnowledgeMapNode:
    metadata: dict[str, Any] = concept.metadata_json or {}
    status = str(metadata.get("default_status", "ready"))
    return KnowledgeMapNode(
        id=concept.code,
        concept_id=concept.id,
        code=concept.code,
        label=concept.title,
        title=concept.title,
        description=concept.description,
        grade_band=concept.grade_band,
        status=status,
        status_label=STATUS_LABELS.get(status, status.upper()),
        x=concept.layout_x,
        y=concept.layout_y,
        group=_nearest_group_label(concept.layout_x, groups),
        metadata=metadata,
    )


def _nearest_group_label(
    x: float | None,
    groups: list[KnowledgeMapGroup],
) -> str | None:
    if x is None or not groups:
        return None
    return min(groups, key=lambda group: abs(group.x - x)).label
