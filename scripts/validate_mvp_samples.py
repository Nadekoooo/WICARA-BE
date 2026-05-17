from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.modules.learning.template_quality import evaluate_template_quality
from app.modules.learning.template_validation import (
    TemplateValidationError,
    validate_template_spec,
)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    sample_root = root / "wicara_mvp_10_manim_templates" / "specs" / "samples"
    if not sample_root.exists():
        print(f"Sample directory missing: {sample_root}")
        return 1

    total = 0
    passed = 0
    failed = 0
    warned = 0
    for entry in sorted(sample_root.iterdir()):
        if not entry.is_dir():
            continue
        sample_path = entry / "sample_01.json"
        if not sample_path.exists():
            print(f"[MISS] {entry.name}: sample_01.json not found")
            failed += 1
            total += 1
            continue

        payload = json.loads(sample_path.read_text(encoding="utf-8"))
        template_id = str(payload.get("template_id") or entry.name).strip().lower()
        total += 1
        try:
            normalized = validate_template_spec(template_id=template_id, spec_json=payload)
            quality_result = evaluate_template_quality(
                template_id=template_id,
                spec_json=normalized.normalized_spec,
            )
            if not quality_result.passed:
                failed += 1
                print(f"[FAIL] {template_id}: quality lint errors detected")
                for detail in quality_result.to_feedback_details():
                    if detail.get("severity") != "error":
                        continue
                    path = detail.get("path", "spec_json")
                    msg = detail.get("message", "Quality issue.")
                    print(f"       - {path}: {msg}")
                continue

            if quality_result.warnings:
                warned += 1
                print(f"[WARN] {template_id}: quality warnings={len(quality_result.warnings)}")
                for detail in quality_result.to_feedback_details():
                    if detail.get("severity") != "warning":
                        continue
                    path = detail.get("path", "spec_json")
                    msg = detail.get("message", "Quality warning.")
                    print(f"       - {path}: {msg}")
            else:
                print(f"[PASS] {template_id}")
            passed += 1
        except TemplateValidationError as exc:
            failed += 1
            print(f"[FAIL] {template_id}: {exc.message}")
            for detail in exc.details[:6]:
                path = detail.get("path", "spec_json")
                msg = detail.get("message", "Invalid value.")
                print(f"       - {path}: {msg}")

    print("---")
    print(f"Total : {total}")
    print(f"Passed: {passed}")
    print(f"Warned: {warned}")
    print(f"Failed: {failed}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
