from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class BlockBase(BaseModel):
    id: Optional[str] = None
    name: str
    district_id: str
    description = Optional[str] = None
    created_at: Optional[datetime] = datetime.now()
    created_by: Optional[str] = "root@ilp.com"

class BlockUpdate(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    district_id: Optional[str] = None
    description = Optional[str] = None
    last_updated_at: Optional[datetime] = datetime.now()
    last_updated_by: Optional[str] = None

class BlockResponse(BaseModel):
    id: Optional[str] = None
    name: str = None
    district_id: Optional[str] = None
    description = Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    last_updated_by: Optional[str] = None

class BlockCreate(BlockBase):
    pass

class Block(BlockBase):
    id: str

    class Config:
        orm_mode = True


