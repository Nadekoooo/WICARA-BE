from sqlalchemy import func, select

from app.modules.curriculum.models import ConceptEdge, KnowledgeConcept, Subject
from app.modules.curriculum.seed import seed_curriculum
from app.modules.curriculum.seed_data import MATH_CONCEPTS, MATH_EDGES


def test_curriculum_seed_is_idempotent_and_creates_math_graph(db_session):
    first = seed_curriculum(db_session)
    second = seed_curriculum(db_session)

    assert first.subjects_created == 4
    assert first.concepts_created == len(MATH_CONCEPTS)
    assert first.edges_created == len(MATH_EDGES)
    assert second.subjects_created == 0
    assert second.concepts_created == 0
    assert second.edges_created == 0

    subject_count = db_session.scalar(select(func.count()).select_from(Subject))
    concept_count = db_session.scalar(select(func.count()).select_from(KnowledgeConcept))
    edge_count = db_session.scalar(select(func.count()).select_from(ConceptEdge))
    assert subject_count == 4
    assert concept_count == len(MATH_CONCEPTS)
    assert edge_count == len(MATH_EDGES)


def test_curriculum_seed_creates_required_prerequisite_edge(db_session):
    seed_curriculum(db_session)

    derivative_definition = db_session.scalar(
        select(KnowledgeConcept).where(KnowledgeConcept.code == "derivative_definition")
    )
    derivative_rules = db_session.scalar(
        select(KnowledgeConcept).where(KnowledgeConcept.code == "derivative_rules")
    )
    edge = db_session.scalar(
        select(ConceptEdge).where(
            ConceptEdge.from_concept_id == derivative_definition.id,
            ConceptEdge.to_concept_id == derivative_rules.id,
            ConceptEdge.edge_type == "prerequisite",
        )
    )

    assert derivative_definition.subject.code == "math"
    assert edge is not None
    assert edge.weight == 1.0
