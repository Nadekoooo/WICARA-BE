from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.modules.accounts.dependencies import get_current_account
from app.modules.accounts.models import UserAccount
from app.modules.workspaces import schemas, service

router = APIRouter(prefix="/workspaces")


@router.post("", response_model=schemas.WorkspaceRead)
def create_workspace(
    payload: schemas.WorkspaceCreateRequest,
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.WorkspaceRead:
    try:
        return service.create_or_resume_workspace(
            session,
            user=account,
            track_id=payload.track_id,
            module_id=payload.module_id,
            content_mode=payload.content_mode,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{workspace_id}", response_model=schemas.WorkspaceRead)
def read_workspace(
    workspace_id: UUID,
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.WorkspaceRead:
    workspace = service.read_workspace(session, user=account, workspace_id=workspace_id)
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace was not found.")
    return workspace


@router.post("/{workspace_id}/events", response_model=schemas.WorkspaceEventCreateResponse)
def append_workspace_event(
    workspace_id: UUID,
    payload: schemas.WorkspaceEventCreateRequest,
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.WorkspaceEventCreateResponse:
    try:
        response = service.append_workspace_event(
            session,
            user=account,
            workspace_id=workspace_id,
            event_type=payload.event_type,
            actor_type=payload.actor_type,
            text_payload=payload.text_payload,
            canvas_snapshot_id=payload.canvas_snapshot_id,
            media_artifact_id=payload.media_artifact_id,
            metadata=payload.metadata,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace was not found.")
    return response
