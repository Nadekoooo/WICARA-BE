#!/usr/bin/env python3
"""
Dump full curriculum graph JSON for mobile offline bundle.

Default source:
  app/modules/curriculum/data/wicara_kurikulum_merdeka_graph_complete.json

Default output:
  ../wicara-mobile-brian/assets/offline_graph/full_curriculum_dump.json
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def _resolve_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid JSON object in {path}")
    return payload


def _build_output(payload: dict) -> dict:
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    version = str(metadata.get("version", "v0")).strip() or "v0"
    notes = metadata.get("notes")
    if not isinstance(notes, list):
        notes = []

    return {
        "metadata": {
            "curriculum_version": version,
            "source": "wicara_be_graph_complete",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "notes": notes,
        },
        "nodes": payload.get("nodes", []),
        "edges": payload.get("edges", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Dump curriculum JSON for mobile")
    parser.add_argument(
        "--source",
        default="app/modules/curriculum/data/wicara_kurikulum_merdeka_graph_complete.json",
        help="Path to source JSON (relative to WICARA-BE root).",
    )
    parser.add_argument(
        "--output",
        default="../wicara-mobile-brian/assets/offline_graph/full_curriculum_dump.json",
        help="Path to output JSON (relative to WICARA-BE root).",
    )
    args = parser.parse_args()

    root = _resolve_root()
    source = (root / args.source).resolve()
    output = (root / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    payload = _load_json(source)
    result = _build_output(payload)

    with output.open("w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"[dump_curriculum] source={source}")
    print(f"[dump_curriculum] output={output}")
    print(f"[dump_curriculum] nodes={len(result.get('nodes', []))}")
    print(f"[dump_curriculum] edges={len(result.get('edges', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

