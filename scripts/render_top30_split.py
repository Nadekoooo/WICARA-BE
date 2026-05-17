from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "app" / "modules" / "learning" / "template_registry.json"
SAMPLE_ROOT = ROOT / "wicara_mvp_10_manim_templates" / "specs" / "samples"
RENDER_HELPER = ROOT / "wicara_mvp_10_manim_templates" / "scripts" / "render_sample.py"
MEDIA_SCENE_DIR = ROOT / "media" / "videos" / "render_scene" / "480p15"


def _load_registry() -> list[dict]:
    payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    rows = payload.get("templates", [])
    if not isinstance(rows, list):
        raise ValueError("template registry format invalid: templates must be a list")
    return [row for row in rows if isinstance(row, dict)]


def _template_slug(template_id: str) -> str:
    suffix = template_id.strip().lower().replace("manim.", "")
    if suffix.endswith(".v1"):
        suffix = suffix[:-3]
    return suffix


def _resolve_paths(template_id: str) -> tuple[Path, Path]:
    slug = _template_slug(template_id)
    template_path = ROOT / "wicara_mvp_10_manim_templates" / "templates" / "manim" / f"{slug}_v1.py"
    sample_path = SAMPLE_ROOT / template_id / "sample_01.json"
    return template_path, sample_path


def _copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", default=str(ROOT / ".venv" / "Scripts" / "python.exe"))
    parser.add_argument("--quality", default="-ql")
    parser.add_argument(
        "--output-root",
        default=str(ROOT / "tmp" / f"batch_render_outputs_top30_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
    )
    args = parser.parse_args()

    py_exec = Path(args.python)
    if not py_exec.exists():
        raise FileNotFoundError(f"Python executable not found: {py_exec}")

    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    rows = _load_registry()
    top30_ids = sorted({str(row.get("template_id", "")).strip().lower() for row in rows if row.get("template_id")})
    mvp10_ids = {
        str(row.get("template_id", "")).strip().lower()
        for row in rows
        if str(row.get("phase", "")).strip().lower() != "phase4_expansion"
    }

    success = 0
    failed = 0
    report_rows: list[dict] = []

    for index, template_id in enumerate(top30_ids, start=1):
        bucket = "mvp10" if template_id in mvp10_ids else "phase4_additional20"
        out_dir = output_root / bucket / template_id
        out_dir.mkdir(parents=True, exist_ok=True)
        log_path = out_dir / "render.log"

        template_path, sample_path = _resolve_paths(template_id)
        if not template_path.exists() or not sample_path.exists():
            failed += 1
            msg = f"Template or sample not found. template={template_path.exists()} sample={sample_path.exists()}"
            log_path.write_text(msg + "\n", encoding="utf-8")
            report_rows.append(
                {
                    "template_id": template_id,
                    "bucket": bucket,
                    "status": "failed",
                    "error": msg,
                }
            )
            print(f"[{index}/{len(top30_ids)}] FAIL {template_id}: missing inputs")
            continue

        cmd = [
            str(py_exec),
            str(RENDER_HELPER),
            "--template",
            str(template_path),
            "--spec",
            str(sample_path),
            f"--quality={args.quality}",
        ]
        print(f"[{index}/{len(top30_ids)}] RENDER {template_id}")
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        log_path.write_text(proc.stdout or "", encoding="utf-8")

        if proc.returncode != 0:
            failed += 1
            report_rows.append(
                {
                    "template_id": template_id,
                    "bucket": bucket,
                    "status": "failed",
                    "error": f"render command exit code {proc.returncode}",
                }
            )
            print(f"[{index}/{len(top30_ids)}] FAIL {template_id} (exit={proc.returncode})")
            continue

        copied_mp4 = _copy_if_exists(MEDIA_SCENE_DIR / "RenderScene.mp4", out_dir / "RenderScene.mp4")
        copied_srt = _copy_if_exists(MEDIA_SCENE_DIR / "RenderScene.srt", out_dir / "RenderScene.srt")

        if not copied_mp4:
            failed += 1
            report_rows.append(
                {
                    "template_id": template_id,
                    "bucket": bucket,
                    "status": "failed",
                    "error": "Render succeeded but RenderScene.mp4 was not found in media output.",
                }
            )
            print(f"[{index}/{len(top30_ids)}] FAIL {template_id} (missing mp4)")
            continue

        success += 1
        report_rows.append(
            {
                "template_id": template_id,
                "bucket": bucket,
                "status": "ok",
                "has_srt": copied_srt,
                "output_dir": str(out_dir),
            }
        )
        print(f"[{index}/{len(top30_ids)}] OK   {template_id}")

    summary = {
        "generated_at": datetime.now().isoformat(),
        "output_root": str(output_root),
        "total": len(top30_ids),
        "success": success,
        "failed": failed,
        "mvp10_count": len(mvp10_ids),
        "phase4_additional20_count": len(top30_ids) - len(mvp10_ids),
        "results": report_rows,
    }
    summary_path = output_root / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("---")
    print(f"Output root : {output_root}")
    print(f"Summary file: {summary_path}")
    print(f"Success     : {success}")
    print(f"Failed      : {failed}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
