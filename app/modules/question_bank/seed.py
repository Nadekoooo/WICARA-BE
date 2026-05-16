from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from app.db.session import SessionLocal
from app.modules.curriculum.seed import seed_curriculum
from app.modules.question_bank.service import import_seed_directory


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed WICARA question bank data.")
    parser.add_argument(
        "--seeds-dir",
        default=None,
        help="Path to a directory containing question-bank JSON seed files.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail when a seed item cannot map to a curriculum concept.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and summarize seed changes, then roll back instead of writing to the database.",
    )
    args = parser.parse_args()

    seeds_dir = Path(args.seeds_dir) if args.seeds_dir else None
    with SessionLocal() as session:
        try:
            seed_curriculum(session, commit=not args.dry_run)
            summary = import_seed_directory(
                session,
                seeds_dir=seeds_dir,
                strict=args.strict,
                commit=not args.dry_run,
            )
        finally:
            if args.dry_run:
                session.rollback()

    print(json.dumps(asdict(summary), sort_keys=True))
    if summary.failed_count:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
