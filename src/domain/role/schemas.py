from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from uuid import UUID

class RoleBase(BaseModel):    
    id: Optional[str] = None
    username: str
    description: str    
    created_at: Optional[datetime] = datetime.now()
    created_by: Optional[str] = "54be662c-eab6-4e60-8c43-40cd744d1fbd"
    
class RoleUpdate(BaseModel):
    id: Optional[str] = None
    name: Optional[bool] = None
    description: Optional[str] = None
    last_updated_at: Optional[datetime] = datetime.now()
    last_updated_by: Optional[str] = None
    
class RoleResponse(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    last_updated_by: Optional[str] = None

class RoleCreate(RoleBase):
 pass

class Role(RoleBase):
    user_id: str
    class Config:
        orm_mode = True