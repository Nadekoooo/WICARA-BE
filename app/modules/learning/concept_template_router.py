from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


_ROUTING_MAP_PATH = Path(__file__).with_name("concept_type_template_map_phase4.json")


def resolve_primary_template_id(concept_type: str | None) -> str | None:
    normalized = _normalize_key(concept_type)
    if not normalized:
        return None
    row = resolve_route_entry(concept_type)
    if row is None:
        return None
    template_id = _normalize_key(row.get("primary_template_id"))
    return template_id or None


def resolve_template_candidates(concept_type: str | None) -> list[str]:
    row = resolve_route_entry(concept_type)
    if row is None:
        return []
    candidates = row.get("template_candidates", [])
    if not isinstance(candidates, list):
        return []
    normalized_candidates: list[str] = []
    for item in candidates:
        token = _normalize_key(item)
        if token and token not in normalized_candidates:
            normalized_candidates.append(token)
    return normalized_candidates


def resolve_route_entry(concept_type: str | None) -> dict | None:
    normalized = _normalize_key(concept_type)
    if not normalized:
        return None
    routes = _routing_map()
    return routes.get(normalized)


@lru_cache
def _routing_map() -> dict[str, dict]:
    if not _ROUTING_MAP_PATH.exists():
        return {}
    payload = json.loads(_ROUTING_MAP_PATH.read_text(encoding="utf-8"))
    rows = payload.get("routes", [])
    if not isinstance(rows, list):
        return {}

    result: dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        key = _normalize_key(row.get("concept_type"))
        if not key:
            continue
        result[key] = row
    return result


def _normalize_key(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()
