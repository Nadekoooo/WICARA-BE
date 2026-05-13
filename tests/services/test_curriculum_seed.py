from sqlalchemy import func, select

from app.modules.curriculum.models import ConceptEdge, KnowledgeConcept, Subject
from app.modules.curriculum.seed import seed_curriculum
from app.modules.curriculum.kurikulum_merdeka import load_kurikulum_merdeka_seed_data


def test_curriculum_seed_is_idempotent_and_creates_kurikulum_graph(db_session):
    seed_data = load_kurikulum_merdeka_seed_data()

    first = seed_curriculum(db_session)
    second = seed_curriculum(db_session)

    assert first.subjects_created == len(seed_data.subjects)
    assert first.concepts_created == len(seed_data.concepts)
    assert first.edges_created == len(seed_data.edges)
    assert second.subjects_created == 0
    assert second.concepts_created == 0
    assert second.edges_created == 0

    subject_count = db_session.scalar(select(func.count()).select_from(Subject))
    concept_count = db_session.scalar(select(func.count()).select_from(KnowledgeConcept))
    edge_count = db_session.scalar(select(func.count()).select_from(ConceptEdge))
    assert subject_count == 6
    assert concept_count == len(seed_data.concepts)
    assert edge_count == len(seed_data.edges)


def test_curriculum_seed_creates_required_prerequisite_edge(db_session):
    seed_curriculum(db_session)

    bilangan_bulat = db_session.scalar(
        select(KnowledgeConcept).where(
            KnowledgeConcept.code == "km_d_matematika_bilangan_bulat"
        )
    )
    bilangan_rasional = db_session.scalar(
        select(KnowledgeConcept).where(
            KnowledgeConcept.code == "km_d_matematika_bilangan_rasional"
        )
    )
    edge = db_session.scalar(
        select(ConceptEdge).where(
            ConceptEdge.from_concept_id == bilangan_bulat.id,
            ConceptEdge.to_concept_id == bilangan_rasional.id,
            ConceptEdge.edge_type == "prerequisite",
        )
    )

    assert bilangan_bulat.subject.code == "matematika"
    assert edge is not None
    assert edge.weight == 0.85
