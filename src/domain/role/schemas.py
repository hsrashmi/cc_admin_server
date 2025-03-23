from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from uuid import UUID

class AccessTypeEnum(str, Enum):
    read = "read"
    female = "write"

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
    name: Optional[bool] = None
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

class UserRoleBase(BaseModel):
    id: Optional[str] = None
    user_id: str
    role_id: str
    access_type: AccessTypeEnum = Field(..., description="Access type must be 'read' or 'write'")
    level: Optional[str] = None
    level_id: Optional[str] = None    
    created_at: Optional[datetime] = datetime.now()
    created_by: Optional[str] = "54be662c-eab6-4e60-8c43-40cd744d1fbd"
    
class UserRoleUpdate(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    role_id: Optional[str] = None
    access_type: Optional[AccessTypeEnum] = Field(None, description="Access type must be 'read' or 'write'")
    level: Optional[str] = None
    level_id: Optional[str] = None    
    last_updated_at: Optional[datetime] = datetime.now()
    last_updated_by: Optional[str] = None
     
class UserRoleResponse(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    role_id: Optional[str] = None
    access_type: Optional[str] = None    
    level: Optional[str] = None
    level_id: Optional[str] = None    
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    last_updated_by: Optional[str] = None

class UserRoleCreate(UserRoleBase):
 pass

class UserRole(UserRoleBase):
    id: str
    class Config:
        orm_mode = True