from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.session import SessionLocal
from app.modules.workspaces.models import WorkspaceSession
from app.modules.workspaces.service import _ensure_phase_metadata


def main() -> int:
    updated = 0
    with SessionLocal() as session:
        workspaces = session.scalars(
            select(WorkspaceSession).where(WorkspaceSession.status == "active")
        ).all()
        total = len(workspaces)
        for workspace in workspaces:
            before = dict(workspace.metadata_json or {})
            after = _ensure_phase_metadata(before, created_at=workspace.created_at)
            if after == before:
                continue
            workspace.metadata_json = after
            updated += 1
        session.commit()

    print(f"Workspace scanned : {total}")
    print(f"Workspace updated : {updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
