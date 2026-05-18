from __future__ import annotations

import re

from app.modules.curriculum.models import KnowledgeConcept


def grade_relation_for_concept(
    concept: KnowledgeConcept,
    *,
    education_level: str | None,
    grade_level: str | None,
) -> str:
    requested_grade = _requested_grade(education_level=education_level, grade_level=grade_level)
    concept_bounds = concept_grade_bounds(concept)
    if requested_grade is None or concept_bounds is None:
        return "unknown"

    min_grade, max_grade = concept_bounds
    if requested_grade < min_grade:
        return "above_current_level"
    if requested_grade > max_grade:
        return "below_current_level"
    return "at_current_level"


def level_note_for_relation(relation: str, *, language: str) -> str | None:
    is_id = _is_indonesian(language)
    if relation == "below_current_level":
        return (
            "Ini materi fondasi di bawah level kelasmu. Tetap cocok untuk refresh atau memperkuat prasyarat."
            if is_id
            else "This is a foundational concept below your current grade. It is still useful for review or prerequisite repair."
        )
    if relation == "above_current_level":
        return (
            "Node ini biasanya di atas level kelasmu. Lanjutkan kalau memang itu tujuanmu."
            if is_id
            else "This concept is usually above your current grade. Continue if this is the goal you meant."
        )
    if relation == "at_current_level":
        return (
            "Node ini cocok dengan level kelasmu."
            if is_id
            else "This concept matches your current grade level."
        )
    return None


def concept_grade_bounds(concept: KnowledgeConcept) -> tuple[int, int] | None:
    metadata = concept.metadata_json or {}
    grade_range = str(metadata.get("grade_range") or concept.grade_band or "").lower()
    parsed = _parse_grade_range(grade_range)
    if parsed is not None:
        return parsed

    grade_band = (concept.grade_band or "").lower()
    if any(marker in grade_band for marker in ("primary", "elementary", "sd")):
        return (1, 6)
    if any(marker in grade_band for marker in ("lower_secondary", "junior", "smp")):
        return (7, 9)
    if "algebra" in grade_band:
        return (7, 10)
    if "precalculus" in grade_band:
        return (10, 11)
    if any(marker in grade_band for marker in ("limits", "continuity", "calculus_1")):
        return (11, 12)
    if any(marker in grade_band for marker in ("calculus_2", "calculus_3")):
        return (12, 12)
    return None


def requested_grade_for_context(*, education_level: str | None, grade_level: str | None) -> int | None:
    return _requested_grade(education_level=education_level, grade_level=grade_level)


def _requested_grade(*, education_level: str | None, grade_level: str | None) -> int | None:
    grade = _first_int(grade_level or "")
    if grade is not None:
        return grade

    normalized = (education_level or "").strip().lower()
    if any(marker in normalized for marker in ("elementary", "primary", "sd", "sekolah dasar")):
        return 4
    if any(marker in normalized for marker in ("junior", "middle", "smp")):
        return 8
    if any(marker in normalized for marker in ("senior", "high", "sma")):
        return 11
    return None


def _parse_grade_range(value: str) -> tuple[int, int] | None:
    numbers = [int(number) for number in re.findall(r"\d+", value)]
    if not numbers:
        return None
    return (min(numbers), max(numbers))


def _first_int(value: str) -> int | None:
    match = re.search(r"\d+", value)
    return int(match.group(0)) if match else None


def _is_indonesian(language: str) -> bool:
    normalized = (language or "").strip().lower()
    return normalized in {"id", "indonesian", "bahasa indonesia"} or "indo" in normalized
