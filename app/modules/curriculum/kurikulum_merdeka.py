from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

GRAPH_FILE_NAME = "wicara_kurikulum_merdeka_graph_complete.json"

SUBJECT_ALIASES = {
    "math": "matematika",
    "mathematics": "matematika",
    "physics": "fisika",
    "chemistry": "kimia",
    "biology": "biologi",
    "science": "ipa",
}

SUBJECT_DISPLAY_ORDER = {
    "matematika": 1,
    "ipas": 2,
    "ipa": 3,
    "fisika": 4,
    "kimia": 5,
    "biologi": 6,
}

PHASE_ORDER = {
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4,
    "E": 5,
    "F": 6,
}

GROUP_X_START = 28.0
GROUP_X_GAP = 302.0
NODE_Y_START = 82.0
NODE_Y_GAP = 70.0


@dataclass(frozen=True)
class SubjectSeed:
    code: str
    name: str
    description: str
    display_order: int
    metadata: dict[str, Any]


@dataclass(frozen=True)
class ConceptSeed:
    subject_code: str
    code: str
    title: str
    description: str | None
    grade_band: str | None
    display_order: int
    layout_x: float
    layout_y: float
    metadata: dict[str, Any]


@dataclass(frozen=True)
class EdgeSeed:
    from_code: str
    to_code: str
    edge_type: str
    weight: float
    metadata: dict[str, Any]


@dataclass(frozen=True)
class CurriculumSeedData:
    subjects: list[SubjectSeed]
    concepts: list[ConceptSeed]
    edges: list[EdgeSeed]


def canonical_subject_code(value: str) -> str:
    normalized = _slug(value)
    return SUBJECT_ALIASES.get(normalized, normalized)


def load_kurikulum_merdeka_seed_data(
    graph_path: str | Path | None = None,
) -> CurriculumSeedData:
    if graph_path is None:
        try:
            path = find_default_graph_path()
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            payload = _fallback_kurikulum_merdeka_payload()
    else:
        path = Path(graph_path)
        payload = json.loads(path.read_text(encoding="utf-8"))

    metadata = payload.get("metadata", {})
    nodes = [node for node in payload.get("nodes", []) if isinstance(node, dict)]
    edges = [edge for edge in payload.get("edges", []) if isinstance(edge, dict)]

    return _build_seed_data(metadata=metadata, nodes=nodes, edges=edges)


def find_default_graph_path() -> Path:
    module_data_path = Path(__file__).resolve().parent / "data" / GRAPH_FILE_NAME
    if module_data_path.exists():
        return module_data_path

    for parent in Path(__file__).resolve().parents:
        candidate = parent / GRAPH_FILE_NAME
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        f"Could not find {GRAPH_FILE_NAME}. Set graph_path when seeding curriculum."
    )


def _build_seed_data(
    *,
    metadata: dict[str, Any],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> CurriculumSeedData:
    nodes_by_subject: dict[str, list[dict[str, Any]]] = {}
    for node in nodes:
        subject_code = canonical_subject_code(_string(node, "subject"))
        if not subject_code:
            continue
        nodes_by_subject.setdefault(subject_code, []).append(node)

    subjects = [
        _subject_seed(subject_code, subject_nodes, metadata)
        for subject_code, subject_nodes in sorted(
            nodes_by_subject.items(),
            key=lambda item: (SUBJECT_DISPLAY_ORDER.get(item[0], 999), item[0]),
        )
    ]

    concepts: list[ConceptSeed] = []
    groups_by_subject = {
        subject_code: _subject_groups(subject_nodes)
        for subject_code, subject_nodes in nodes_by_subject.items()
    }
    concept_order = 1
    for subject_code, subject_nodes in sorted(
        nodes_by_subject.items(),
        key=lambda item: (SUBJECT_DISPLAY_ORDER.get(item[0], 999), item[0]),
    ):
        groups = groups_by_subject[subject_code]
        local_counts_by_group: dict[tuple[str, str], int] = {}
        for node in _sorted_nodes(subject_nodes):
            group_key = _group_key(node)
            group = groups[group_key]
            local_index = local_counts_by_group.get(group_key, 0)
            local_counts_by_group[group_key] = local_index + 1

            concepts.append(
                _concept_seed(
                    subject_code=subject_code,
                    node=node,
                    display_order=concept_order,
                    layout_x=group["x"],
                    layout_y=NODE_Y_START + (local_index * NODE_Y_GAP),
                    local_group_order=local_index + 1,
                )
            )
            concept_order += 1

    known_node_ids = {concept.code for concept in concepts}
    edge_seeds = [
        _edge_seed(edge)
        for edge in edges
        if _string(edge, "from_node_id") in known_node_ids
        and _string(edge, "to_node_id") in known_node_ids
    ]

    return CurriculumSeedData(subjects=subjects, concepts=concepts, edges=edge_seeds)


def _fallback_kurikulum_merdeka_payload() -> dict[str, Any]:
    return {
        "metadata": {
            "curriculum": "kurikulum_merdeka",
            "version": "fallback-dev",
            "generated_at": None,
        },
        "nodes": [
            _fallback_node(
                node_id="km_a_matematika_pola",
                subject="matematika",
                subject_label="Matematika",
                phase="A",
                school_level="SD",
                grade_range="1-2",
                domain="Aljabar",
                difficulty_order=1,
                label="Pola Sederhana",
            ),
            _fallback_node(
                node_id="km_d_matematika_bilangan_bulat",
                subject="matematika",
                subject_label="Matematika",
                phase="D",
                school_level="SMP",
                grade_range="7-9",
                domain="Bilangan",
                difficulty_order=1,
                label="Bilangan Bulat",
            ),
            _fallback_node(
                node_id="km_d_matematika_bilangan_rasional",
                subject="matematika",
                subject_label="Matematika",
                phase="D",
                school_level="SMP",
                grade_range="7-9",
                domain="Bilangan",
                difficulty_order=3,
                label="Bilangan Rasional",
            ),
            _fallback_node(
                node_id="km_d_matematika_bilangan_irasional",
                subject="matematika",
                subject_label="Matematika",
                phase="D",
                school_level="SMP",
                grade_range="7-9",
                domain="Bilangan",
                difficulty_order=4,
                label="Bilangan Irasional",
            ),
            _fallback_node(
                node_id="km_b_ipas_makhluk_hidup",
                subject="ipas",
                subject_label="IPAS",
                phase="B",
                school_level="SD",
                grade_range="3-4",
                domain="Makhluk Hidup",
                difficulty_order=1,
                label="Makhluk Hidup dan Lingkungan",
            ),
            _fallback_node(
                node_id="km_d_ipa_pengukuran",
                subject="ipa",
                subject_label="IPA",
                phase="D",
                school_level="SMP",
                grade_range="7-9",
                domain="Sains",
                difficulty_order=1,
                label="Pengukuran dalam Sains",
            ),
            _fallback_node(
                node_id="km_e_fisika_gerak",
                subject="fisika",
                subject_label="Fisika",
                phase="E",
                school_level="SMA",
                grade_range="10",
                domain="Mekanika",
                difficulty_order=1,
                label="Gerak Lurus",
            ),
            _fallback_node(
                node_id="km_e_kimia_atom",
                subject="kimia",
                subject_label="Kimia",
                phase="E",
                school_level="SMA",
                grade_range="10",
                domain="Struktur Materi",
                difficulty_order=1,
                label="Struktur Atom",
            ),
            _fallback_node(
                node_id="km_e_biologi_sel",
                subject="biologi",
                subject_label="Biologi",
                phase="E",
                school_level="SMA",
                grade_range="10",
                domain="Sel",
                difficulty_order=1,
                label="Struktur Sel",
            ),
        ],
        "edges": [
            _fallback_edge(
                edge_id="edge_km_d_matematika_bilangan_bulat_rasional",
                from_node_id="km_d_matematika_bilangan_bulat",
                to_node_id="km_d_matematika_bilangan_rasional",
                strength=0.85,
            ),
            _fallback_edge(
                edge_id="edge_km_d_matematika_bilangan_rasional_irasional",
                from_node_id="km_d_matematika_bilangan_rasional",
                to_node_id="km_d_matematika_bilangan_irasional",
                strength=0.8,
            ),
        ],
    }


def _fallback_node(
    *,
    node_id: str,
    subject: str,
    subject_label: str,
    phase: str,
    school_level: str,
    grade_range: str,
    domain: str,
    difficulty_order: int,
    label: str,
) -> dict[str, Any]:
    return {
        "id": node_id,
        "subject": subject,
        "subject_label": subject_label,
        "phase": phase,
        "school_level": school_level,
        "grade_range": grade_range,
        "domain": domain,
        "difficulty_order": difficulty_order,
        "label_id": label,
        "label_en": label,
        "description_id": f"Fallback seed untuk {label}.",
    }


def _fallback_edge(
    *,
    edge_id: str,
    from_node_id: str,
    to_node_id: str,
    strength: float,
) -> dict[str, Any]:
    return {
        "id": edge_id,
        "from_node_id": from_node_id,
        "to_node_id": to_node_id,
        "edge_type": "prerequisite",
        "strength": strength,
    }


def _subject_seed(
    subject_code: str,
    nodes: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> SubjectSeed:
    first_node = _sorted_nodes(nodes)[0]
    label = _string(first_node, "subject_label", fallback=subject_code.title())
    phases = sorted({_string(node, "phase") for node in nodes}, key=_phase_sort_key)
    school_levels = sorted({_string(node, "school_level") for node in nodes if _string(node, "school_level")})
    groups = list(_subject_groups(nodes).values())
    graph_metadata = {
        "title": f"Kurikulum Merdeka {label} Knowledge Map",
        "width": (groups[-1]["x"] + 260.0) if groups else 1200.0,
        "height": _graph_height(nodes),
        "top_down": True,
        "groups": groups,
    }

    return SubjectSeed(
        code=subject_code,
        name=label,
        description=(
            f"Kurikulum Merdeka {label} graph covering phases "
            f"{', '.join(phases)} across {len(nodes)} concepts."
        ),
        display_order=SUBJECT_DISPLAY_ORDER.get(subject_code, 999),
        metadata={
            "curriculum": metadata.get("curriculum", "kurikulum_merdeka"),
            "version": metadata.get("version"),
            "generated_at": metadata.get("generated_at"),
            "source_subject_code": _string(first_node, "subject"),
            "phases": phases,
            "school_levels": school_levels,
            "node_count": len(nodes),
            "graph": graph_metadata,
        },
    )


def _concept_seed(
    *,
    subject_code: str,
    node: dict[str, Any],
    display_order: int,
    layout_x: float,
    layout_y: float,
    local_group_order: int,
) -> ConceptSeed:
    title = _string(node, "label_id", fallback=_string(node, "label_en"))
    metadata = dict(node)
    metadata.update(
        {
            "default_status": _preview_status(
                node,
                local_group_order=local_group_order,
            ),
            "local_group_order": local_group_order,
            "preview_status_only": True,
            "source_node_id": _string(node, "id"),
            "source_curriculum_graph": GRAPH_FILE_NAME,
        }
    )

    return ConceptSeed(
        subject_code=subject_code,
        code=_string(node, "id"),
        title=title,
        description=_optional_string(node, "description_id"),
        grade_band=_grade_band(node),
        display_order=display_order,
        layout_x=layout_x,
        layout_y=layout_y,
        metadata=metadata,
    )


def _edge_seed(edge: dict[str, Any]) -> EdgeSeed:
    metadata = dict(edge)
    metadata.update(
        {
            "source_edge_id": _string(edge, "id"),
            "source_curriculum_graph": GRAPH_FILE_NAME,
        }
    )
    return EdgeSeed(
        from_code=_string(edge, "from_node_id"),
        to_code=_string(edge, "to_node_id"),
        edge_type=_string(edge, "edge_type", fallback="prerequisite"),
        weight=_float(edge.get("strength"), fallback=1.0),
        metadata=metadata,
    )


def _subject_groups(nodes: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    for index, group_key in enumerate(
        sorted({_group_key(node) for node in nodes}, key=_group_sort_key)
    ):
        phase, domain = group_key
        groups[group_key] = {
            "label": f"Fase {phase} / {domain}" if phase else domain,
            "x": GROUP_X_START + (index * GROUP_X_GAP),
            "phase": phase,
            "domain": domain,
        }
    return groups


def _sorted_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        nodes,
        key=lambda node: (
            _phase_sort_key(_string(node, "phase")),
            _string(node, "domain"),
            _int(node.get("difficulty_order"), fallback=9999),
            _string(node, "label_id"),
            _string(node, "id"),
        ),
    )


def _group_key(node: dict[str, Any]) -> tuple[str, str]:
    return (
        _string(node, "phase", fallback="?"),
        _string(node, "domain", fallback="General"),
    )


def _group_sort_key(group_key: tuple[str, str]) -> tuple[int, str]:
    phase, domain = group_key
    return (_phase_sort_key(phase), domain)


def _grade_band(node: dict[str, Any]) -> str | None:
    phase = _string(node, "phase")
    school_level = _string(node, "school_level")
    grade_range = _string(node, "grade_range")
    if not phase and not school_level and not grade_range:
        return None
    return f"Fase {phase} ({school_level} {grade_range})".strip()


def _preview_status(node: dict[str, Any], *, local_group_order: int) -> str:
    phase = _string(node, "phase")
    difficulty = local_group_order

    if phase in {"A", "B"}:
        return "mastered"
    if phase == "C":
        return "review" if difficulty % 5 == 0 else "ready"
    if phase == "D":
        if difficulty <= 2:
            return "active"
        if difficulty % 7 == 0:
            return "gap"
        if difficulty % 4 == 0:
            return "review"
        return "ready"
    if phase == "E":
        if difficulty <= 2:
            return "active"
        return "gap" if difficulty % 6 == 0 else "locked"
    if phase == "F":
        return "ready" if difficulty == 1 else "locked"
    return "ready"


def _graph_height(nodes: list[dict[str, Any]]) -> float:
    group_counts: dict[tuple[str, str], int] = {}
    for node in nodes:
        key = _group_key(node)
        group_counts[key] = group_counts.get(key, 0) + 1
    max_group_count = max(group_counts.values(), default=6)
    return max(600.0, NODE_Y_START + (max_group_count * NODE_Y_GAP) + 80.0)


def _phase_sort_key(phase: str) -> int:
    return PHASE_ORDER.get(phase, 999)


def _slug(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def _string(
    payload: dict[str, Any],
    key: str,
    *,
    fallback: str = "",
) -> str:
    value = payload.get(key)
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def _optional_string(payload: dict[str, Any], key: str) -> str | None:
    value = _string(payload, key)
    return value or None


def _int(value: Any, *, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _float(value: Any, *, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback
