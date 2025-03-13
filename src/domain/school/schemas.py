from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class SchoolBase(BaseModel):
    id: Optional[str] = None
    name: str
    long_name: str
    dise_code: int = Field(..., ge=10**10, le=10**11 - 1, description="Phone number must be a 10-digit integer")
    city: str
    state: str
    pincode: int
    owner_id: int
    organization_id: int
    created_at: Optional[datetime] = datetime.now()
    created_by: Optional[str] = "root@ilp.com"

class SchoolUpdate(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    long_name: Optional[str] = None
    last_name: Optional[str] = None
    dise_code: Optional[int] = Field(None, ge=10**10, le=10**11 - 1, description="Phone number must be a 10-digit integer")
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[int] = None
    owner_id: Optional[int] = None
    organization_id: Optional[int] = None
    last_updated_at: Optional[datetime] = datetime.now()
    last_updated_by: Optional[str] = None

class SchoolCreate(SchoolBase):
 pass

class School(SchoolBase):
    id: str
    class Config:
        orm_mode = True

class ClassBase(BaseModel):
    id: Optional[str] = None
    school_id: str
    grade: str
    section: str
    created_at: Optional[datetime] = datetime.now()
    created_by: Optional[str] = "root@ilp.com"

class ClassUpdate(BaseModel):
    id: Optional[str] = None
    school_id: Optional[str] = None
    grade: Optional[str] = None
    section: Optional[str] = None
    last_updated_at: Optional[datetime] = datetime.now()
    last_updated_by: Optional[str] = None

class ClassCreate(ClassBase):
 pass

class Class(ClassBase):
    id: str
    class Config:
        orm_mode = True