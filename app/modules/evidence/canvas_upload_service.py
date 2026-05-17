from __future__ import annotations

from sqlalchemy.orm import Session

from app.modules.accounts.models import UserAccount
from app.modules.evidence.models import ImageAsset
from app.modules.evidence.schemas import ImageAssetCreateRequest, ImageAssetRead


class CanvasUploadService:
    def create_image_asset(
        self,
        session: Session,
        *,
        user: UserAccount,
        payload: ImageAssetCreateRequest,
    ) -> ImageAssetRead:
        asset = ImageAsset(
            user_id=user.id,
            storage_path=payload.storage_path,
            mime_type=payload.mime_type,
            width=payload.width,
            height=payload.height,
            checksum=payload.checksum,
        )
        session.add(asset)
        session.commit()
        return ImageAssetRead(
            id=asset.id,
            storage_path=asset.storage_path,
            mime_type=asset.mime_type,
            width=asset.width,
            height=asset.height,
            checksum=asset.checksum,
        )
