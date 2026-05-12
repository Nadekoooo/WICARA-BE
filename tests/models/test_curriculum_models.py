from sqlalchemy import select

from app.modules.curriculum.models import ConceptEdge, KnowledgeConcept, Subject


def test_curriculum_models_persist_subject_owned_prerequisite_graph(db_session):
    subject = Subject(code="math", name="Mathematics", display_order=1)
    prerequisite = KnowledgeConcept(
        subject=subject,
        code="limits",
        title="Limits",
        display_order=1,
        metadata_json={"default_status": "ready"},
    )
    target = KnowledgeConcept(
        subject=subject,
        code="derivatives",
        title="Derivatives",
        display_order=2,
        metadata_json={"default_status": "locked"},
    )
    edge = ConceptEdge(
        from_concept=prerequisite,
        to_concept=target,
        edge_type="prerequisite",
        weight=1.0,
    )

    db_session.add_all([subject, prerequisite, target, edge])
    db_session.commit()

    loaded = db_session.scalar(select(Subject).where(Subject.code == "math"))
    assert loaded is not None
    assert {concept.code for concept in loaded.concepts} == {"limits", "derivatives"}

    loaded_edge = db_session.scalar(select(ConceptEdge))
    assert loaded_edge is not None
    assert loaded_edge.edge_type == "prerequisite"
    assert loaded_edge.from_concept.code == "limits"
    assert loaded_edge.to_concept.code == "derivatives"
