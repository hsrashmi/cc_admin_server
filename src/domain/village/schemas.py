from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class VillageBase(BaseModel):
    id: Optional[str] = None
    name: str
    block_id: str
    description: str
    created_at: Optional[datetime] = datetime.now()
    created_by: Optional[str] = "root@ilp.com"

class VillageUpdate(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    block_id: Optional[str] = None
    description: Optional[str] = None
    last_updated_at: Optional[datetime] = datetime.now()
    last_updated_by: Optional[str] = None

class VillageResponse(BaseModel):
    id: Optional[str] = None
    name: str = None
    block_id: str = None
    description: str = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    last_updated_by: Optional[str] = None

class VillageCreate(VillageBase):
    pass

class Village(VillageBase):
    id: str

    class Config:
        orm_mode = True


