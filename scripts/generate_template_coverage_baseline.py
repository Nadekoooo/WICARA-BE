from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ConceptTypeRow:
    concept_type: str
    concept_type_label_id: str
    default_template_id: str
    media_engine_family: str
    count: int
    covered: bool


def _resolve_paths() -> tuple[Path, Path, Path, Path]:
    root = Path(__file__).resolve().parents[1]
    registry = root / "app" / "modules" / "learning" / "template_registry.json"
    mapping = root.parent / "wicara_kurikulum_merdeka_graph_complete" / "node_concept_type_mapping.csv"
    baseline_out = root / "template_coverage_baseline.md"
    priority_out = root / "concept_type_priority.csv"
    return registry, mapping, baseline_out, priority_out


def _load_registry_template_ids(path: Path) -> set[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("templates", [])
    result: set[str] = set()
    for row in rows:
        template_id = str(row.get("template_id", "")).strip().lower()
        if template_id:
            result.add(template_id)
    if not result:
        raise ValueError(f"No template ids found in registry: {path}")
    return result


def _load_concept_rows(path: Path, template_ids: set[str]) -> tuple[list[ConceptTypeRow], int]:
    with path.open(encoding="utf-8", newline="") as fp:
        rows = list(csv.DictReader(fp))
    if not rows:
        raise ValueError(f"Concept mapping CSV is empty: {path}")

    by_type_count = Counter(str(row.get("concept_type", "")).strip() for row in rows)
    by_type_label = defaultdict(str)
    by_type_template = defaultdict(str)
    by_type_engine = defaultdict(str)

    for row in rows:
        key = str(row.get("concept_type", "")).strip()
        if not key:
            continue
        if not by_type_label[key]:
            by_type_label[key] = str(row.get("concept_type_label_id", "")).strip()
        if not by_type_template[key]:
            by_type_template[key] = str(row.get("default_template_id", "")).strip().lower()
        if not by_type_engine[key]:
            by_type_engine[key] = str(row.get("media_engine_family", "")).strip().lower()

    result: list[ConceptTypeRow] = []
    for concept_type, count in by_type_count.most_common():
        default_template_id = by_type_template.get(concept_type, "")
        covered = bool(default_template_id and default_template_id in template_ids)
        result.append(
            ConceptTypeRow(
                concept_type=concept_type,
                concept_type_label_id=by_type_label.get(concept_type, ""),
                default_template_id=default_template_id,
                media_engine_family=by_type_engine.get(concept_type, ""),
                count=count,
                covered=covered,
            )
        )
    return result, len(rows)


def _priority_tier(rank_uncovered: int) -> str:
    if rank_uncovered <= 0:
        return "covered_mvp"
    if rank_uncovered <= 10:
        return "top10_uncovered"
    if rank_uncovered <= 30:
        return "top30_uncovered"
    if rank_uncovered <= 60:
        return "top60_uncovered"
    return "long_tail"


def _write_priority_csv(path: Path, rows: list[ConceptTypeRow]) -> None:
    uncovered = [row for row in rows if not row.covered]
    covered = [row for row in rows if row.covered]
    uncovered_rank = {row.concept_type: i + 1 for i, row in enumerate(uncovered)}

    with path.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "concept_type",
                "concept_type_label_id",
                "frequency",
                "priority",
                "status",
                "suggested_template_id",
                "media_engine_family",
            ],
        )
        writer.writeheader()
        for row in rows:
            rank = uncovered_rank.get(row.concept_type, 0)
            priority = _priority_tier(rank)
            status = "covered_mvp" if row.covered else "uncovered"
            writer.writerow(
                {
                    "concept_type": row.concept_type,
                    "concept_type_label_id": row.concept_type_label_id,
                    "frequency": row.count,
                    "priority": priority,
                    "status": status,
                    "suggested_template_id": row.default_template_id,
                    "media_engine_family": row.media_engine_family,
                }
            )


def _bullet(lines: list[str]) -> str:
    return "\n".join(f"- {line}" for line in lines)


def _write_baseline_md(
    path: Path,
    rows: list[ConceptTypeRow],
    total_mapping_rows: int,
    template_ids: set[str],
) -> None:
    manim_rows = sum(row.count for row in rows if row.media_engine_family.startswith("manim"))
    remotion_rows = sum(row.count for row in rows if row.media_engine_family.startswith("remotion"))
    covered_rows = sum(row.count for row in rows if row.covered)
    uncovered_rows = total_mapping_rows - covered_rows
    covered_types = [row for row in rows if row.covered]
    uncovered_types = [row for row in rows if not row.covered]

    top_covered = [f"`{row.concept_type}` ({row.count}) -> `{row.default_template_id}`" for row in covered_types[:12]]
    top_uncovered = [
        f"`{row.concept_type}` ({row.count}) -> suggested `{row.default_template_id or 'TBD'}`"
        for row in uncovered_types[:20]
    ]
    existing_templates = [f"`{tid}`" for tid in sorted(template_ids)]

    md = f"""# Template Coverage Baseline

Generated from:
- `wicara_kurikulum_merdeka_graph_complete/node_concept_type_mapping.csv`
- `app/modules/learning/template_registry.json`

## Snapshot
- Total curriculum rows: **{total_mapping_rows}**
- Unique `concept_type`: **{len(rows)}**
- Registered MVP templates: **{len(template_ids)}**
- Rows mapped to `media_engine_family=manim`: **{manim_rows} ({manim_rows / total_mapping_rows:.1%})**
- Rows mapped to `media_engine_family=remotion*`: **{remotion_rows} ({remotion_rows / total_mapping_rows:.1%})**
- Covered rows (default template already in MVP registry): **{covered_rows} ({covered_rows / total_mapping_rows:.1%})**
- Uncovered rows: **{uncovered_rows} ({uncovered_rows / total_mapping_rows:.1%})**
- Covered concept types: **{len(covered_types)} / {len(rows)}**

## Existing MVP Templates
{_bullet(existing_templates)}

## Covered Concept Types (Top by Frequency)
{_bullet(top_covered)}

## Uncovered Concept Types (Top by Frequency)
{_bullet(top_uncovered)}

## Rollout Buckets
- `top10_uncovered`: highest frequency uncovered concept types.
- `top30_uncovered`: next band after top 10.
- `top60_uncovered`: next band after top 30.
- `long_tail`: remaining uncovered concept types.
- `covered_mvp`: already handled by current MVP 10 template registry.

## Output Files
- `concept_type_priority.csv`: machine-readable backlog with `priority` and `status`.
- `template_coverage_baseline.md`: this summary.
"""
    path.write_text(md, encoding="utf-8")


def main() -> None:
    registry_path, mapping_path, baseline_out, priority_out = _resolve_paths()
    template_ids = _load_registry_template_ids(registry_path)
    rows, total_rows = _load_concept_rows(mapping_path, template_ids)
    _write_priority_csv(priority_out, rows)
    _write_baseline_md(baseline_out, rows, total_rows, template_ids)
    print(f"Wrote {priority_out}")
    print(f"Wrote {baseline_out}")


if __name__ == "__main__":
    main()
