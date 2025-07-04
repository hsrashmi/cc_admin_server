from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class AssetBase(BaseModel):
    id: Optional[str] = None
    name: str = None
    type: str = None
    description: str = None
    url: Optional[str] = None
    size: Optional[int] = None
    mime_type: str = None
    created_at: Optional[datetime] = datetime.now()
    created_by: Optional[str] = "54be662c-eab6-4e60-8c43-40cd744d1fbd"

class AssetUpdate(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None 
    url: Optional[str] = None
    size: Optional[int] = None
    mime_type: Optional[str]  = None
    last_updated_at: Optional[datetime] = datetime.now()
    last_updated_by: Optional[str] = None

class AssetResponse(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None 
    url: Optional[str] = None
    size: Optional[int] = None
    mime_type: Optional[str]  = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    last_updated_by: Optional[str] = None

class AssetCreate(AssetBase):
    pass

class Asset(AssetBase):
    id: str

    class Config:
        orm_mode = True

class ActivityAssetBase(BaseModel):
    id: Optional[str] = None
    activity_id: str = None
    asset_id: str = None
    created_at: Optional[datetime] = datetime.now()
    created_by: Optional[str] = "54be662c-eab6-4e60-8c43-40cd744d1fbd"

class AssetUpdate(BaseModel):
    id: Optional[str] = None
    activity_id: Optional[str] = None
    asset_id: Optional[str] = None
    last_updated_at: Optional[datetime] = datetime.now()
    last_updated_by: Optional[str] = None

class ActivityAssetResponse(BaseModel):
    id: Optional[str] = None
    activity_id: Optional[str] = None
    activity_name: Optional[str] = None 
    asset_id: Optional[str] = None
    asset_description: Optional[str] = None 
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    last_updated_by: Optional[str] = None

class ActivityAssetBaseCreate(ActivityAssetBase):
    pass

class ActivityAsset(AssetBase):
    id: str

    class Config:
        orm_mode = True