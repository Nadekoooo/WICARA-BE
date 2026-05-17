from __future__ import annotations

from app.modules.learning_goal_resolution.candidate_retriever import ConceptCandidate


PROMPT_VERSION = "goal_resolver_v3_scope_relevance"


def build_goal_resolution_prompt(*, raw_query: str, candidates: list[ConceptCandidate]) -> str:
    candidate_lines = "\n".join(
        (
            f"- concept_code={candidate.concept.code}; title={candidate.concept.title}; "
            f"subject={candidate.concept.subject.code if candidate.concept.subject else ''}; "
            f"grade_band={candidate.concept.grade_band or ''}; "
            f"score={candidate.score:.2f}; "
            f"aliases={', '.join(candidate.aliases[:6])}; "
            f"signals={', '.join(candidate.matched_signals[:8])}; "
            f"description_id={_compact(candidate.concept.id_desc or candidate.concept.description or '')}; "
            f"description_en={_compact(candidate.concept.en_desc or '')}"
        )
        for candidate in candidates
    )
    return f"""
You resolve a learner's free-text learning goal to an existing knowledge_concepts node.

Rules:
- Choose only from the provided candidates.
- Do not invent concept_code values.
- Return status="exact_match" only when one candidate directly teaches the requested learning goal.
- Return status="ambiguous" when multiple candidates are plausible, the query is too broad, or the query could mean different curriculum concepts.
- Return status="no_match" when no candidate directly represents the goal in this candidate list.
- Never pick a weakly related node just because it is the closest available.
- confidence must be a number from 0 to 1.
- If status="exact_match", selected_concept_code must be from the candidate list.
- If status is "ambiguous" or "no_match", selected_concept_code must be null.
- alternatives must contain only concept_code values from the candidate list.
- Return compact JSON only with:
  status, selected_concept_code, confidence, alternatives, reason, should_expand_scope, clarification_question.

User query:
{raw_query}

Candidates:
{candidate_lines}
""".strip()


def _compact(value: str, *, max_length: int = 180) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= max_length:
        return normalized
    return normalized[: max_length - 1].rstrip() + "..."
