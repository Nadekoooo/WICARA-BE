from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.curriculum.kurikulum_merdeka import canonical_subject_code
from app.modules.curriculum.models import KnowledgeConcept, Subject
from app.modules.learning_goal_resolution.level_context import (
    concept_grade_bounds,
    grade_relation_for_concept,
    requested_grade_for_context,
)

try:  # rapidfuzz is declared as a dependency, but keep local dev resilient.
    from rapidfuzz import fuzz
except Exception:  # pragma: no cover - exercised only when dependency is absent.
    fuzz = None


ALIASES: dict[str, tuple[str, ...]] = {
    "multiplication": (
        "kali",
        "kali-kalian",
        "perkalian",
        "dikali",
        "times",
        "multiply",
        "multiplication",
        "repeated addition",
        "penjumlahan berulang",
    ),
    "addition": (
        "tambah",
        "penjumlahan",
        "plus",
        "add",
        "addition",
        "sum",
    ),
    "subtraction": (
        "kurang",
        "pengurangan",
        "minus",
        "subtract",
        "subtraction",
        "difference",
    ),
    "division": (
        "bagi",
        "pembagian",
        "dibagi",
        "divide",
        "division",
        "quotient",
    ),
    "fraction": (
        "pecahan",
        "fraction",
        "fractions",
        "per",
        "pembilang",
        "penyebut",
        "rasional",
        "decimal",
        "desimal",
    ),
    "derivative": (
        "turunan",
        "diferensial",
        "differentiation",
        "derivative",
        "derivatives",
        "gradien fungsi",
        "kemiringan grafik",
        "kemiringan kurva",
        "laju perubahan",
        "rate of change",
        "slope",
        "tangent",
    ),
    "limit": (
        "limit",
        "limits",
        "mendekati",
        "approaches",
        "continuity",
        "kontinuitas",
    ),
    "function": (
        "fungsi",
        "function",
        "functions",
        "domain",
        "range",
        "grafik fungsi",
    ),
    "linear_equation": (
        "persamaan",
        "persamaan linear",
        "linear equation",
        "equation",
        "solve x",
        "mencari x",
    ),
    "quadratic": (
        "kuadrat",
        "persamaan kuadrat",
        "quadratic",
        "parabola",
        "polynomial",
    ),
    "trigonometry": (
        "trigonometri",
        "trigonometry",
        "sin",
        "cos",
        "tan",
        "trig",
    ),
}


INTENT_BOOSTS: tuple[dict[str, tuple[str, ...]], ...] = (
    {
        "name": ("multiplication",),
        "triggers": ("kali", "kali-kalian", "dikali", "perkalian"),
        "boost_terms": ("perkalian", "multiplication", "multiply", "repeated addition"),
    },
    {
        "name": ("derivative",),
        "triggers": ("turunan", "kemiringan grafik", "gradien fungsi", "laju perubahan"),
        "boost_terms": ("turunan", "derivative", "differentiation", "rate of change", "slope"),
    },
    {
        "name": ("fraction",),
        "triggers": ("pecahan", "per", "pembilang", "penyebut"),
        "boost_terms": ("pecahan", "fraction", "rational", "decimal"),
    },
    {
        "name": ("limit",),
        "triggers": ("limit", "mendekati", "kontinuitas"),
        "boost_terms": ("limit", "limits", "continuity", "kontinuitas"),
    },
    {
        "name": ("function",),
        "triggers": ("fungsi", "grafik fungsi", "domain", "range"),
        "boost_terms": ("fungsi", "function", "graph"),
    },
)


@dataclass(frozen=True)
class ConceptCandidate:
    concept: KnowledgeConcept
    score: float
    matched_signals: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()

    def snapshot(self) -> dict[str, object]:
        subject = self.concept.subject
        return {
            "concept_id": str(self.concept.id),
            "concept_code": self.concept.code,
            "title": self.concept.title,
            "description": self.concept.id_desc or self.concept.description,
            "id_desc": self.concept.id_desc or self.concept.description,
            "en_desc": self.concept.en_desc,
            "subject_code": subject.code if subject else "",
            "subject": subject.name if subject else "",
            "grade_band": self.concept.grade_band,
            "aliases": list(self.aliases),
            "score": round(self.score, 3),
            "confidence": score_to_confidence(self.score),
            "matched_signals": list(self.matched_signals),
        }


class CandidateConceptRetriever:
    def search(
        self,
        session: Session,
        *,
        query: str,
        subject_code: str | None = None,
        education_level: str | None = None,
        grade_level: str | None = None,
        grade_scope: str = "all",
        include_context_fallback: bool = False,
        limit: int = 30,
    ) -> list[ConceptCandidate]:
        normalized_query = _normalize_text(query)
        raw_terms = _raw_query_terms(query)
        expanded_terms = _expanded_terms(query)
        all_terms = raw_terms | expanded_terms
        expanded_query = _normalize_text(" ".join(sorted(expanded_terms)))

        concepts = self._load_concepts(session, subject_code=subject_code)
        concepts = [
            concept
            for concept in concepts
            if _concept_matches_grade_scope(
                concept,
                grade_scope=grade_scope,
                education_level=education_level,
                grade_level=grade_level,
            )
        ]

        scored: list[ConceptCandidate] = []
        for concept in concepts:
            score, signals, aliases = _score_concept(
                concept,
                raw_terms=raw_terms,
                all_terms=all_terms,
                normalized_query=normalized_query,
                expanded_query=expanded_query,
                education_level=education_level,
                grade_level=grade_level,
            )
            if score > 0:
                scored.append(
                    ConceptCandidate(
                        concept=concept,
                        score=score,
                        matched_signals=tuple(dict.fromkeys(signals)),
                        aliases=tuple(dict.fromkeys(aliases)),
                    )
                )
        scored.sort(key=lambda item: (-item.score, item.concept.display_order, item.concept.title))
        if include_context_fallback and len(scored) < limit:
            scored_ids = {candidate.concept.id for candidate in scored}
            for concept in concepts:
                if concept.id in scored_ids:
                    continue
                scored.append(
                    ConceptCandidate(
                        concept=concept,
                        score=0.05,
                        matched_signals=(f"context:{grade_scope}",),
                    )
                )
                if len(scored) >= limit:
                    break
        return scored[:limit]

    def _load_concepts(
        self,
        session: Session,
        *,
        subject_code: str | None,
    ) -> list[KnowledgeConcept]:
        statement = (
            select(KnowledgeConcept)
            .join(KnowledgeConcept.subject)
            .where(Subject.is_active.is_(True))
            .options(selectinload(KnowledgeConcept.subject))
            .order_by(KnowledgeConcept.display_order, KnowledgeConcept.title)
        )
        if subject_code:
            statement = statement.where(Subject.code == canonical_subject_code(subject_code))
        return list(session.scalars(statement))


def score_to_confidence(score: float) -> float:
    return round(max(0.0, min(0.99, float(score) / 18.0)), 3)


def _raw_query_terms(query: str) -> set[str]:
    normalized = _normalize_text(query)
    return {term for term in re.split(r"[^a-z0-9_]+", normalized) if len(term) >= 2}


def _expanded_terms(query: str) -> set[str]:
    normalized = _normalize_text(query)
    terms = set(_raw_query_terms(normalized))
    for group, aliases in ALIASES.items():
        if _matches_any_phrase(normalized, aliases):
            terms.add(group)
            for alias in aliases:
                terms.update(_raw_query_terms(alias))
    return terms


def _score_concept(
    concept: KnowledgeConcept,
    *,
    raw_terms: set[str],
    all_terms: set[str],
    normalized_query: str,
    expanded_query: str,
    education_level: str | None,
    grade_level: str | None,
) -> tuple[float, list[str], list[str]]:
    title = _normalize_text(concept.title)
    code = _normalize_text(concept.code)
    description = _normalize_text(concept.description or "")
    id_desc = _normalize_text(concept.id_desc or "")
    en_desc = _normalize_text(concept.en_desc or "")
    metadata = concept.metadata_json or {}
    metadata_haystack = _metadata_search_text(metadata)
    haystack = f"{code} {title} {description} {id_desc} {en_desc} {metadata_haystack}".replace("-", " ")
    title_terms = _raw_query_terms(title)
    code_terms = _raw_query_terms(code)
    description_terms = _raw_query_terms(f"{description} {id_desc} {en_desc}")
    metadata_terms = _raw_query_terms(metadata_haystack)

    score = 0.0
    signals: list[str] = []
    matched_aliases: list[str] = []

    if normalized_query:
        if normalized_query in title:
            score += 8.0
            signals.append("phrase:title")
        if normalized_query in code:
            score += 6.0
            signals.append("phrase:code")
        if normalized_query in description:
            score += 3.0
            signals.append("phrase:description")

    title_overlap = len(raw_terms & title_terms)
    code_overlap = len(raw_terms & code_terms)
    description_overlap = len(raw_terms & description_terms)
    expanded_overlap = len(all_terms & (title_terms | code_terms | description_terms))
    metadata_overlap = len(all_terms & metadata_terms)
    if title_overlap:
        score += title_overlap * 4.0
        signals.append(f"token:title:{title_overlap}")
    if code_overlap:
        score += code_overlap * 3.0
        signals.append(f"token:code:{code_overlap}")
    if description_overlap:
        score += description_overlap * 2.0
        signals.append(f"token:description:{description_overlap}")
    if expanded_overlap:
        score += expanded_overlap * 1.4
        signals.append(f"token:expanded:{expanded_overlap}")
    if metadata_overlap:
        score += metadata_overlap * 1.2
        signals.append(f"token:semantic_metadata:{metadata_overlap}")

    if normalized_query and normalized_query in metadata_haystack:
        score += 2.4
        signals.append("phrase:semantic_metadata")

    for group, aliases in ALIASES.items():
        query_matches_group = group in all_terms or _matches_any_phrase(normalized_query, aliases)
        if not query_matches_group:
            continue
        concept_matches_group = group in haystack or _matches_any_phrase(haystack, aliases)
        if concept_matches_group:
            score += 5.0
            signals.append(f"alias:{group}")
            matched_aliases.extend(alias for alias in aliases if _phrase_in(alias, haystack))

    for intent in INTENT_BOOSTS:
        triggers = intent["triggers"]
        boost_terms = intent["boost_terms"]
        if not _matches_any_phrase(normalized_query, triggers):
            continue
        if _matches_any_phrase(haystack, boost_terms):
            name = intent["name"][0]
            score += 6.0
            signals.append(f"intent:{name}")

    fuzzy_score, fuzzy_signals = _fuzzy_score(normalized_query, title=title, haystack=haystack, prefix="raw")
    score += fuzzy_score
    signals.extend(fuzzy_signals)
    if expanded_query and expanded_query != normalized_query:
        expanded_fuzzy_score, expanded_fuzzy_signals = _fuzzy_score(
            expanded_query,
            title=title,
            haystack=haystack,
            prefix="expanded",
        )
        score += expanded_fuzzy_score * 0.65
        signals.extend(expanded_fuzzy_signals)

    relation = grade_relation_for_concept(
        concept,
        education_level=education_level,
        grade_level=grade_level,
    )
    if relation == "at_current_level":
        score += 1.0
        signals.append("grade:current")
    elif relation == "below_current_level":
        score += 0.4
        signals.append("grade:below")
    elif relation == "above_current_level":
        score -= 0.2
        signals.append("grade:above")
    elif education_level:
        requested = _education_level_alias(education_level)
        grade_band = (concept.grade_band or "").lower()
        school_level = str(metadata.get("school_level", "")).lower()
        if requested and (requested in grade_band or requested in school_level):
            score += 0.2
            signals.append("grade:school_level")

    return max(0.0, score), signals, matched_aliases


def _fuzzy_score(
    query: str,
    *,
    title: str,
    haystack: str,
    prefix: str,
) -> tuple[float, list[str]]:
    if not query or fuzz is None:
        return 0.0, []
    partial = float(fuzz.partial_ratio(query, title))
    token_set = float(fuzz.token_set_ratio(query, haystack))
    weighted = float(fuzz.WRatio(query, haystack))
    score = (partial * 0.04) + (token_set * 0.03) + (weighted * 0.02)
    signals = []
    if partial >= 75:
        signals.append(f"fuzzy:{prefix}:title")
    if token_set >= 75:
        signals.append(f"fuzzy:{prefix}:token_set")
    if weighted >= 75:
        signals.append(f"fuzzy:{prefix}:weighted")
    return score, signals


def _normalize_text(value: str) -> str:
    return value.lower().replace("-", " ")


def _metadata_search_text(metadata: dict[str, object]) -> str:
    search_fields = [
        "label_id",
        "label_en",
        "description_id",
        "description_en",
        "domain",
        "element",
        "subject_label",
        "concept_family",
        "concept_family_label_id",
        "concept_type",
        "concept_type_label_id",
        "concept_subtype",
        "concept_subtype_label_id",
        "concept_visual_pattern",
        "default_template_id",
        "media_engine_family",
        "recommended_visual_engine",
        "tags",
    ]
    parts: list[str] = []
    for field in search_fields:
        value = metadata.get(field)
        if isinstance(value, str):
            parts.append(value)
    anchors = metadata.get("real_world_anchor_examples")
    if isinstance(anchors, list):
        parts.extend(str(anchor) for anchor in anchors if str(anchor).strip())
    return _normalize_text(" ".join(parts))


def _matches_any_phrase(value: str, phrases: Iterable[str]) -> bool:
    return any(_phrase_in(phrase, value) for phrase in phrases)


def _phrase_in(phrase: str, value: str) -> bool:
    normalized = _normalize_text(phrase)
    if " " in normalized:
        return normalized in value
    return normalized in _raw_query_terms(value)


def _education_level_alias(value: str) -> str:
    normalized = value.lower()
    if any(marker in normalized for marker in ("elementary", "primary", "sd")):
        return "sd"
    if any(marker in normalized for marker in ("junior", "middle", "smp")):
        return "smp"
    if any(marker in normalized for marker in ("senior", "high", "sma")):
        return "sma"
    return normalized


def _concept_matches_grade_scope(
    concept: KnowledgeConcept,
    *,
    grade_scope: str,
    education_level: str | None,
    grade_level: str | None,
) -> bool:
    if grade_scope == "all":
        return True
    requested_grade = requested_grade_for_context(
        education_level=education_level,
        grade_level=grade_level,
    )
    bounds = concept_grade_bounds(concept)
    if requested_grade is None or bounds is None:
        return grade_scope in {"nearby_grade", "all"}
    min_grade, max_grade = bounds
    if grade_scope == "current_grade":
        return min_grade <= requested_grade <= max_grade
    if grade_scope == "nearby_grade":
        return min_grade <= requested_grade + 2 and max_grade >= requested_grade - 2
    return True
