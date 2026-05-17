import json

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


def test_curriculum_seed_marks_removed_concepts_as_stale(db_session, tmp_path):
    legacy_graph_path = tmp_path / "legacy_graph.json"
    legacy_graph_path.write_text(
        json.dumps(
            {
                "metadata": {
                    "curriculum": "kurikulum_merdeka",
                    "version": "legacy-test",
                },
                "nodes": [
                    {
                        "id": "legacy_ipas_node",
                        "subject": "ipas",
                        "subject_label": "IPAS",
                        "phase": "A",
                        "school_level": "SD",
                        "grade_range": "1-2",
                        "domain": "Legacy",
                        "difficulty_order": 1,
                        "label_id": "Legacy IPAS Node",
                    }
                ],
                "edges": [],
            }
        ),
        encoding="utf-8",
    )

    seed_curriculum(db_session, graph_path=legacy_graph_path)
    legacy_concept = db_session.scalar(
        select(KnowledgeConcept).where(KnowledgeConcept.code == "legacy_ipas_node")
    )

    assert legacy_concept is not None
    assert legacy_concept.metadata_json.get("stale_seed") is not True

    seed_curriculum(db_session)
    db_session.refresh(legacy_concept)

    assert legacy_concept.metadata_json["stale_seed"] is True
    assert (
        legacy_concept.metadata_json["stale_reason"]
        == "not_present_in_current_curriculum_seed"
    )


def test_curriculum_seed_persists_bilingual_node_descriptions(db_session, tmp_path):
    graph_path = tmp_path / "bilingual_graph.json"
    graph_path.write_text(
        json.dumps(
            {
                "metadata": {
                    "curriculum": "kurikulum_merdeka",
                    "version": "bilingual-test",
                },
                "nodes": [
                    {
                        "id": "km_d_ipa_bilingual_node",
                        "subject": "ipa",
                        "subject_label": "IPA",
                        "phase": "D",
                        "school_level": "SMP/MTs",
                        "grade_range": "7-9",
                        "domain": "Sains",
                        "difficulty_order": 1,
                        "label_id": "Node bilingual",
                        "label_en": "Bilingual node",
                        "description_id": "Deskripsi Indonesia untuk node.",
                        "description_en": "English description for the node.",
                    }
                ],
                "edges": [],
            }
        ),
        encoding="utf-8",
    )

    seed_curriculum(db_session, graph_path=graph_path)

    concept = db_session.scalar(
        select(KnowledgeConcept).where(KnowledgeConcept.code == "km_d_ipa_bilingual_node")
    )
    assert concept is not None
    assert concept.description == "Deskripsi Indonesia untuk node."
    assert concept.id_desc == "Deskripsi Indonesia untuk node."
    assert concept.en_desc == "English description for the node."
