from typing import Optional
from .models import LevelEnum
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from uuid import UUID
from typing import List

class UserRoleBase(BaseModel):
    id: Optional[str] = None
    user_id: str
    role_id: str
    access_type: str = "READ"
    level: Optional[str] = None
    level_id: Optional[str] = None    
    created_at: Optional[datetime] = datetime.now()
    created_by: Optional[str] = "54be662c-eab6-4e60-8c43-40cd744d1fbd"
    
class UserRoleUpdate(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    role_id: Optional[str] = None
    access_type: Optional[str] = None
    level: Optional[str] = None
    level_id: Optional[str] = None    
    last_updated_at: Optional[datetime] = datetime.now()
    last_updated_by: Optional[str] = None
     
class UserRoleResponse(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    role_id: Optional[str] = None
    role_name: Optional[str] = None
    access_type: Optional[str] = None    
    level: Optional[str] = None
    level_id: Optional[str] = None    
    level_name: Optional[str] = None    
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    last_updated_by: Optional[str] = None

class UserRoleResponseSchema(BaseModel):
    id: str
    user_id: str
    user_name: Optional[str]
    role_id: str
    role_name: Optional[str]
    access_type: str
    level: str
    level_id: Optional[str]

    class Config:
        orm_mode = True


class FieldFilter(BaseModel):
    field_name: LevelEnum
    field_value: str

class FilterRequest(BaseModel):
    fields: List[FieldFilter]

class TeacherCreate(BaseModel):    
    id: Optional[str] = None
    role_id: Optional[str] = None
    user_id: str
    class_id: str

class TeacherUpdate(BaseModel):    
    user_id: Optional[str] = None
    class_id: Optional[str] = None

class StudentUpdateRequest(BaseModel):
    student_ids: list[str]
    
class UserRoleCreate(UserRoleBase):
 pass

class UserRole(UserRoleBase):
    id: str
    class Config:
        orm_mode = True

