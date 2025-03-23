from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime

class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"

class ILPUserBase(BaseModel):
    id: Optional[str] = None
    is_active: Optional[bool] = True
    username: str
    first_name: str
    last_name: str
    profile_pic_url: Optional[str] = None
    phone1: str = Field(..., description="Phone number must be a 10-digit integer")
    phone2: Optional[str] = Field(None, description="Phone number must be a 10-digit integer")
    email: EmailStr
    password: str
    address: str
    city: str
    state: str
    country: str
    gender: GenderEnum
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    created_by: Optional[str] = "54be662c-eab6-4e60-8c43-40cd744d1fbd"
    
    @field_validator("phone1", "phone2")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not value.isdigit():
            raise ValueError("Phone number must contain only digits")
        if len(value) != 10:
            raise ValueError("Phone number must be exactly 10 digits")
        return value

class ILPUserUpdate(BaseModel):
    id: Optional[str] = None
    is_active: Optional[bool] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_pic_url: Optional[str] = None
    phone1: Optional[str] = Field(None, description="Phone number must be a 10-digit string")
    phone2: Optional[str] = Field(None, description="Phone number must be a 10-digit string")
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    gender: Optional[GenderEnum] = None
    last_updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    last_updated_by: Optional[str] = None

    @field_validator("phone1", "phone2")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not value.isdigit():
            raise ValueError("Phone number must contain only digits")
        if len(value) != 10:
            raise ValueError("Phone number must be exactly 10 digits")
        return value

class ILPUserResponse(BaseModel):
    id: Optional[str] = None
    is_active: Optional[bool] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_pic_url: Optional[str] = None
    phone1: Optional[str] = None  # Fixed: Should be string, not int
    phone2: Optional[str] = None  # Fixed: Should be string, not int
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
    id: str

    class Config:
        orm_mode = True
