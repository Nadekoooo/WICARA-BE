from __future__ import annotations

import re

_LEVEL_DESCRIPTION_PATTERNS = (
    re.compile(
        r"\s+within\s+.+?\s+for\s+Phase\s+[A-F](?:/[A-F])?" r"(?:\s*/\s*[^.]+)*\.?",
        re.IGNORECASE,
    ),
    re.compile(
        r"\s+aligned with Kurikulum Merdeka(?:\s+[A-Z]+)?\s+Phase\s+[A-F]"
        r"(?:/[A-F])?(?:\s+[A-Z]+)?\s+learning outcomes\.?",
        re.IGNORECASE,
    ),
    re.compile(
        r"\s+sesuai Capaian Pembelajaran Kurikulum Merdeka(?:\s+SD)?"
        r"\s+Fase\s+[A-F](?:/[A-F])?(?:\s+[A-Z]+)?\.?",
        re.IGNORECASE,
    ),
)

_GENERATED_DESCRIPTION_PATTERNS = (
    re.compile(r"^(?:build|building) understanding of .+\.?$", re.IGNORECASE),
)


def course_description_only(value: str | None) -> str:
    description = " ".join(str(value or "").split()).strip()
    if not description:
        return ""
    for pattern in _LEVEL_DESCRIPTION_PATTERNS:
        description = pattern.sub("", description).strip()
    if any(
        pattern.fullmatch(description) for pattern in _GENERATED_DESCRIPTION_PATTERNS
    ):
        return ""
    if description and description[-1] not in ".!?":
        description = f"{description}."
    return description


def first_course_description(*values: str | None) -> str:
    for value in values:
        description = course_description_only(value)
        if description:
            return description
    return ""
