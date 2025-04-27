from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class SchoolBase(BaseModel):
    id: Optional[str] = None
    name: str
    long_name: str
    block_id: str
    dise_code: int = Field(..., ge=10**10, le=10**11 - 1, description="Invalid Dise Code")
    address: str
    city: str
    pincode: int
    organization_id: str
    created_at: Optional[datetime] = datetime.now()
    created_by: Optional[str] = "54be662c-eab6-4e60-8c43-40cd744d1fbd"

class SchoolUpdate(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    long_name: Optional[str] = None    
    block_id: Optional[str] = None
    dise_code: Optional[int] = Field(None, ge=10**10, le=10**11 - 1, description="Invalid Dise Code")
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[int] = None
    organization_id: Optional[str] = None
    last_updated_at: Optional[datetime] = datetime.now()
    last_updated_by: Optional[str] = None

class SchoolResponse(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    long_name: Optional[str] = None
    block_id: Optional[str] = None
    dise_code: Optional[int] = None
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[int] = None
    organization_id: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    last_updated_by: Optional[str] = None

class SchoolCreate(SchoolBase):
 pass

class School(SchoolBase):
    id: str
    class Config:
        orm_mode = True

class SchoolDetailsResponse(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    block_id: Optional[str] = None
    block_name: Optional[str] = None
    district_id: Optional[str]  = None
    district_name: Optional[str] = None
    zone_id: Optional[str] = None
    zone_name: Optional[str]  = None
    state_id: Optional[str] = None
    state_name: Optional[str] = None

    # All fields from School table (example)
    long_name: Optional[str] = None
    dise_code: Optional[int] = None
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[int] = None
    organization_id: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    last_updated_by: Optional[str] = None

    class Config:
        orm_mode = True

class ClassBase(BaseModel):
    id: Optional[str] = None
    school_id: str
    grade: str
    section: str
    created_at: Optional[datetime] = datetime.now()
    created_by: Optional[str] = "54be662c-eab6-4e60-8c43-40cd744d1fbd"

class ClassUpdate(BaseModel):
    id: Optional[str] = None
    school_id: Optional[str] = None
    grade: Optional[str] = None
    section: Optional[str] = None
    last_updated_at: Optional[datetime] = datetime.now()
    last_updated_by: Optional[str] = None

class ClassResponse(BaseModel):
    id: Optional[str] = None
    school_id: Optional[str] = None
    grade: Optional[str] = None
    section: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    last_updated_by: Optional[str] = None
class ClassDetailsBase(BaseModel):
    class_id: Optional[str] = None    
    grade: Optional[str] = None
    section: Optional[str] = None
    class_teacher_id: Optional[str] = None
    class_teacher_name: Optional[str] = None
    teacher_assignment_id: Optional[str] = None
    student_count: Optional[int] = 0
    created_at: Optional[datetime] = datetime.now()
    created_by: Optional[str] = "54be662c-eab6-4e60-8c43-40cd744d1fbd"

class ClassCreate(ClassBase):
 pass

class Class(ClassBase):
    id: str
    class Config:
        orm_mode = True