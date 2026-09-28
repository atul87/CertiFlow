from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AssetResponse(BaseModel):
    id: str
    organization_id: str
    template_id: Optional[str] = None
    filename: str
    mime_type: str
    size: int
    asset_type: str  # background, logo, signature, seal, watermark
    width: int
    height: int
    url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FontResponse(BaseModel):
    id: str
    name: str
    family: str
    source: str  # system, custom
    organization_id: Optional[str] = None

    class Config:
        from_attributes = True
