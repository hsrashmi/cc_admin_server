from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from uuid import UUID

class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"

class ILPUserBase(BaseModel):
    user_id: Optional[str] = None
    is_active: Optional[bool] = True
    username: str
    first_name: str
    last_name: str
    profile_pic_url: Optional[str] = None
    phone1: str = Field(..., description="Phone number must be a 10-digit integer")
    phone2: Optional[str] = Field(None, description="Phone number must be a 10-digit integer")
    email: EmailStr = Field(default=None)
    password: str
    address: str
    city: str
    state: str
    country: str
    gender: GenderEnum = Field(..., description="Gender must be 'male', 'female', or 'other'")
    created_at: Optional[datetime] = datetime.now()
    created_by: Optional[str] = "root@ilp.com"
    
    @field_validator("phone1", "phone2")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not value:
            return value
        if not value.isdigit():
            raise ValueError("Phone number must contain only digits")
        if len(value) != 10:
            raise ValueError("Phone number must be exactly 10 digits")
        return value

class ILPUserUpdate(BaseModel):
    user_id: Optional[str] = None
    is_active: Optional[bool] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_pic_url: Optional[str] = None
    phone1: Optional[str] = Field(None, description="Phone number must be a 10-digit string")
    phone2: Optional[str] = Field(None, description="Phone number must be a 10-digit string")
    email: Optional[EmailStr] = Field(default=None)
    password: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    gender: Optional[GenderEnum] = Field(None, description="Gender must be 'male', 'female', or 'other'")
    last_updated_at: Optional[datetime] = datetime.now()
    last_updated_by: Optional[str] = None

    @field_validator("phone1", "phone2")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("Phone number must contain only digits")
        if len(value) != 10:
            raise ValueError("Phone number must be exactly 10 digits")
        return value
        
class ILPUserResponse(BaseModel):
    user_id: Optional[str] = None
    is_active: Optional[bool] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_pic_url: Optional[str] = None
    phone1: Optional[int] = None
    phone2: Optional[int] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    gender: Optional[GenderEnum] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    last_updated_by: Optional[str] = None

class ILPUserCreate(ILPUserBase):
 pass

class ILPUser(ILPUserBase):
    user_id: str
    class Config:
        orm_mode = True
