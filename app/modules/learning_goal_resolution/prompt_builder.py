from __future__ import annotations

import json

from app.modules.learning_goal_resolution.candidate_retriever import ConceptCandidate


PROMPT_VERSION = "goal_resolver_v4_llm_scope_nodes"


def build_goal_resolution_prompt(
    *,
    raw_query: str,
    candidates: list[ConceptCandidate],
    language: str,
    search_scope: str,
) -> str:
    node_payload = [
        {
            "concept_code": candidate.concept.code,
            "title": candidate.concept.title,
            "subject_code": candidate.concept.subject.code if candidate.concept.subject else "",
            "grade_band": candidate.concept.grade_band or "",
            "description_id": _compact(candidate.concept.id_desc or candidate.concept.description or ""),
            "description_en": _compact(candidate.concept.en_desc or ""),
            "domain": _metadata_text(candidate, "domain"),
            "element": _metadata_text(candidate, "element"),
            "concept_family": _metadata_text(candidate, "concept_family"),
            "concept_type": _metadata_text(candidate, "concept_type"),
        }
        for candidate in candidates
    ]
    return f"""
You resolve a learner's free-text learning goal to an existing knowledge_concepts node.

Rules:
- Choose only from the provided nodes.
- Do not invent concept_code values.
- Return status="exact_match" only when one node directly teaches the requested learning goal.
- Return status="ambiguous" when multiple nodes are plausible, the query is too broad, or the query could mean different curriculum concepts.
- Return status="no_match" when no node directly represents the goal in this node list.
- Never pick a weakly related node just because it is the closest available.
- confidence must be a number from 0 to 1.
- If status="exact_match", selected_concept_code must be from the node list.
- If status is "ambiguous" or "no_match", selected_concept_code must be null.
- alternatives must contain only concept_code values from the node list.
- Write clarification_question in the learner response language.
- Return compact JSON only with:
  status, selected_concept_code, confidence, alternatives, reason, should_expand_scope, clarification_question.

User query:
{raw_query}

Learner response language:
{language or "en"}

Search scope:
{search_scope}

Available nodes:
{json.dumps(node_payload, ensure_ascii=False)}
""".strip()


def _compact(value: str, *, max_length: int = 180) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= max_length:
        return normalized
    return normalized[: max_length - 1].rstrip() + "..."


def _metadata_text(candidate: ConceptCandidate, key: str) -> str:
    value = (candidate.concept.metadata_json or {}).get(key)
    return str(value).strip() if value is not None else ""
