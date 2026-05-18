from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.modules.accounts.dependencies import get_current_account
from app.modules.accounts.models import UserAccount
from app.modules.evidence.canvas_upload_service import CanvasUploadService
from app.modules.evidence.schemas import ImageAssetCreateRequest

router = APIRouter()
service = CanvasUploadService()


@router.post("/evidence/image-assets")
def create_image_asset(
    payload: ImageAssetCreateRequest,
    session: Session = Depends(get_session),
    user: UserAccount = Depends(get_current_account),
):
    return service.create_image_asset(session, user=user, payload=payload)
