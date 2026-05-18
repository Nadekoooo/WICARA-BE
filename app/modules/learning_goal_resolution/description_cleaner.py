from __future__ import annotations

import re

_LEVEL_DESCRIPTION_PATTERNS = (
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


def course_description_only(value: str | None) -> str:
    description = " ".join(str(value or "").split()).strip()
    if not description:
        return ""
    for pattern in _LEVEL_DESCRIPTION_PATTERNS:
        description = pattern.sub("", description).strip()
    if description and description[-1] not in ".!?":
        description = f"{description}."
    return description
