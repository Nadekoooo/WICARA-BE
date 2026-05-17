from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class ImageAssetCreateRequest(BaseModel):
    storage_path: str = Field(..., min_length=1)
    mime_type: str = Field(default="image/png", min_length=3, max_length=64)
    width: int | None = Field(default=None, ge=1)
    height: int | None = Field(default=None, ge=1)
    checksum: str | None = Field(default=None, max_length=128)


class ImageAssetRead(BaseModel):
    id: UUID
    storage_path: str
    mime_type: str
    width: int | None = None
    height: int | None = None
    checksum: str | None = None
