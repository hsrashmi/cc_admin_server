from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ZoneBase(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    state_id: Optional[str] = None
    created_at: Optional[datetime] = datetime.now()
    created_by: Optional[str] = "54be662c-eab6-4e60-8c43-40cd744d1fbd"

class ZoneUpdate(BaseModel):
    id: str = None
    name: Optional[str] = None
    description: Optional[str] = None
    state_id: Optional[str] = None
    last_updated_at: Optional[datetime] = datetime.now()
    last_updated_by: Optional[str] = None

class ZoneResponse(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    state_id: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    last_updated_by: Optional[str] = None

class ZoneCreate(ZoneBase):
    pass

class Zone(ZoneBase):
    id: str

    class Config:
        orm_mode = True


