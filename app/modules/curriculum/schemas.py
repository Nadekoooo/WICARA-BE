from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class SubjectRead(BaseModel):
    id: UUID
    code: str
    name: str
    description: str | None = None
    is_active: bool
    display_order: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class SubjectListResponse(BaseModel):
    items: list[SubjectRead]


class KnowledgeMapGroup(BaseModel):
    label: str
    x: float


class KnowledgeMapGraph(BaseModel):
    title: str
    width: float
    height: float
    top_down: bool = True


class KnowledgeMapNode(BaseModel):
    id: str
    concept_id: UUID
    code: str
    label: str
    title: str
    description: str | None = None
    grade_band: str | None = None
    status: str
    status_label: str
    x: float | None = None
    y: float | None = None
    group: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeMapEdge(BaseModel):
    id: UUID
    from_node: str = Field(serialization_alias="from")
    to: str
    edge_type: str
    weight: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeMapResponse(BaseModel):
    subject: SubjectRead
    graph: KnowledgeMapGraph
    groups: list[KnowledgeMapGroup]
    nodes: list[KnowledgeMapNode]
    edges: list[KnowledgeMapEdge]


class ConceptRelation(BaseModel):
    id: str
    code: str
    label: str
    subject_code: str
    subject_name: str
    status: str
    status_label: str


class ConceptDetailResponse(BaseModel):
    concept: KnowledgeMapNode
    subject: SubjectRead
    mastery_confidence: float
    prerequisites: list[ConceptRelation]
    related_concepts: list[ConceptRelation]
    cross_subject_connections: list[ConceptRelation]
    metadata: dict[str, Any] = Field(default_factory=dict)
