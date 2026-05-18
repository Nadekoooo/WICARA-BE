from __future__ import annotations

import json

from app.modules.curriculum.models import KnowledgeConcept, Subject
from app.modules.learning_goal_resolution.candidate_retriever import ConceptCandidate
from app.modules.learning_goal_resolution.prompt_builder import build_goal_resolution_prompt


def test_goal_resolution_prompt_uses_english_node_payload_only():
    prompt = build_goal_resolution_prompt(
        raw_query="I want to learn fractions",
        candidates=[_candidate()],
        language="en",
        search_scope="same_subject_all_grades",
    )

    payload = _available_nodes(prompt)

    assert payload == [
        {
            "concept_code": "math_fraction",
            "title": "Fractions",
            "grade_band": "7",
            "description": "English description for fractions.",
        }
    ]
    assert "description_id" not in prompt
    assert "description_en" not in prompt
    assert "Deskripsi Indonesia untuk pecahan." not in prompt
    assert "Phase D" not in prompt
    assert "Kurikulum Merdeka" not in prompt


def test_goal_resolution_prompt_uses_indonesian_node_payload_only():
    prompt = build_goal_resolution_prompt(
        raw_query="Aku mau belajar pecahan",
        candidates=[_candidate()],
        language="id",
        search_scope="same_subject_all_grades",
    )

    payload = _available_nodes(prompt)

    assert payload == [
        {
            "concept_code": "math_fraction",
            "title": "Pecahan",
            "grade_band": "7",
            "description": "Deskripsi Indonesia untuk pecahan.",
        }
    ]
    assert "description_id" not in prompt
    assert "description_en" not in prompt
    assert "English description for fractions." not in prompt
    assert "Fase D" not in prompt
    assert "Kurikulum Merdeka" not in prompt


def _candidate() -> ConceptCandidate:
    subject = Subject(
        code="math",
        name="Matematika",
        metadata_json={"name_id": "Matematika", "name_en": "Math"},
    )
    concept = KnowledgeConcept(
        code="math_fraction",
        title="Pecahan",
        description="Deskripsi umum pecahan.",
        id_desc=(
            "Deskripsi Indonesia untuk pecahan sesuai Capaian Pembelajaran "
            "Kurikulum Merdeka Fase D."
        ),
        en_desc=(
            "English description for fractions aligned with Kurikulum Merdeka "
            "Phase D learning outcomes."
        ),
        grade_band="7",
        display_order=1,
        metadata_json={
            "label_id": "Pecahan",
            "label_en": "Fractions",
            "description_id": "Deskripsi metadata Indonesia.",
            "description_en": "Metadata English description.",
        },
    )
    concept.subject = subject
    return ConceptCandidate(concept=concept, score=1.0)


def _available_nodes(prompt: str) -> list[dict[str, str]]:
    payload = prompt.split("Available nodes:\n", 1)[1]
    return json.loads(payload)
