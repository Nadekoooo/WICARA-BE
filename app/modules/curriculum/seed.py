from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.modules.curriculum.models import ConceptEdge, KnowledgeConcept, Subject
from app.modules.curriculum.seed_data import MATH_CONCEPTS, MATH_EDGES, SUBJECTS


@dataclass(frozen=True)
class CurriculumSeedResult:
    subjects_created: int = 0
    subjects_updated: int = 0
    concepts_created: int = 0
    concepts_updated: int = 0
    edges_created: int = 0
    edges_updated: int = 0


def seed_curriculum(session: Session, *, commit: bool = True) -> CurriculumSeedResult:
    counts = {
        "subjects_created": 0,
        "subjects_updated": 0,
        "concepts_created": 0,
        "concepts_updated": 0,
        "edges_created": 0,
        "edges_updated": 0,
    }

    subjects_by_code: dict[str, Subject] = {}
    for subject_data in SUBJECTS:
        subject = session.scalar(
            select(Subject).where(Subject.code == subject_data["code"])
        )
        if subject is None:
            subject = Subject(code=subject_data["code"])
            session.add(subject)
            counts["subjects_created"] += 1
        else:
            counts["subjects_updated"] += 1

        subject.name = subject_data["name"]
        subject.description = subject_data["description"]
        subject.display_order = subject_data["display_order"]
        subject.is_active = True
        subject.metadata_json = subject_data["metadata"]
        subjects_by_code[subject.code] = subject

    session.flush()

    math_subject = subjects_by_code["math"]
    concepts_by_code: dict[str, KnowledgeConcept] = {}
    for index, concept_data in enumerate(MATH_CONCEPTS, start=1):
        concept = session.scalar(
            select(KnowledgeConcept).where(
                KnowledgeConcept.subject_id == math_subject.id,
                KnowledgeConcept.code == concept_data["code"],
            )
        )
        if concept is None:
            concept = KnowledgeConcept(
                subject_id=math_subject.id,
                code=concept_data["code"],
            )
            session.add(concept)
            counts["concepts_created"] += 1
        else:
            counts["concepts_updated"] += 1

        concept.title = concept_data["title"]
        concept.description = f"Seeded Math concept for {concept_data['title']}."
        concept.grade_band = concept_data["grade_band"]
        concept.display_order = index
        concept.layout_x = float(concept_data["x"])
        concept.layout_y = float(concept_data["y"])
        concept.metadata_json = {
            "default_status": concept_data["status"],
            "mobile_seed": True,
        }
        concepts_by_code[concept.code] = concept

    session.flush()

    for from_code, to_code in MATH_EDGES:
        from_concept = concepts_by_code[from_code]
        to_concept = concepts_by_code[to_code]
        edge = session.scalar(
            select(ConceptEdge).where(
                ConceptEdge.from_concept_id == from_concept.id,
                ConceptEdge.to_concept_id == to_concept.id,
                ConceptEdge.edge_type == "prerequisite",
            )
        )
        if edge is None:
            edge = ConceptEdge(
                from_concept_id=from_concept.id,
                to_concept_id=to_concept.id,
                edge_type="prerequisite",
            )
            session.add(edge)
            counts["edges_created"] += 1
        else:
            counts["edges_updated"] += 1

        edge.weight = 1.0
        edge.metadata_json = {"mobile_seed": True}

    if commit:
        session.commit()

    return CurriculumSeedResult(**counts)


def main() -> None:
    with SessionLocal() as session:
        result = seed_curriculum(session)
    print(json.dumps(asdict(result), sort_keys=True))


if __name__ == "__main__":
    main()
