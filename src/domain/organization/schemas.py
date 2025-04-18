from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class OrganizationBase(BaseModel):
    id: Optional[str] = None
    name: str
    long_name: str
    description: str
    placeholder1: Optional[str] = None
    placeholder2: Optional[str] = None
    placeholder3: Optional[str] = None
    created_at: Optional[datetime] = datetime.now()
    created_by: Optional[str] = "54be662c-eab6-4e60-8c43-40cd744d1fbd"

class OrganizationUpdate(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    long_name: Optional[str] = None
    description: Optional[str] = None
    placeholder1: Optional[str] = None
    placeholder2: Optional[str] = None
    placeholder3: Optional[str] = None
    last_updated_at: Optional[datetime] = datetime.now()
    last_updated_by: Optional[str] = None

class OrganizationResponse(BaseModel):
    id: Optional[str] = None
    name: str = None
    long_name: str = None
    description: str = None
    placeholder1: Optional[str] = None
    placeholder2: Optional[str] = None
    placeholder3: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    last_updated_by: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: str

    class Config:
        orm_mode = True


