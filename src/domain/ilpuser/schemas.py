from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from fastapi import UploadFile, File

class ILPUserBase(BaseModel):
    id: Optional[str] = None
    is_active: Optional[bool] = True
    username: str
    first_name: str
    last_name: str
    phone1: str = Field(..., description="Phone number must be a 10-digit integer")
    phone2: Optional[str] = Field(None)
    email: EmailStr
    password: str
    address:  Optional[str]
    city:  Optional[str]
    state:  Optional[str]
    country:  Optional[str]
    gender:  Optional[str]
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    created_by: Optional[str] = "54be662c-eab6-4e60-8c43-40cd744d1fbd"
    
    @field_validator("phone1", "phone2")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None or str(value).strip().lower() in ["", "null"]:
            return None

        # Convert to string
        value_str = str(value).strip()

        # Remove decimal if present (e.g., '6767676566.0' -> '6767676566')
        if value_str.endswith(".0"):
            value_str = value_str[:-2]

        # Ensure it's digits only
        if not value_str.isdigit():
            raise ValueError("Phone number must contain only digits")

        if len(value_str) != 10:
            raise ValueError("Phone number must be exactly 10 digits")

        return value_str
class ILPUserUpdate(BaseModel):
    id: Optional[str] = None
    is_active: Optional[bool] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone1: Optional[str] = Field(None, description="Phone number must be a 10-digit string")
    phone2: Optional[str] = Field(None, description="Phone number must be a 10-digit string")
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None    
    profile_pic_url: Optional[str] = None
    gender: Optional[str] = None
    last_updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    last_updated_by: Optional[str] = None

# Separate file field for FastAPI
class ILPUserUpdateWithFileSchema(ILPUserUpdate):
    profile_pic_file: Optional[UploadFile] = File(None)  # File is optional

    @field_validator("phone1", "phone2")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None or str(value).strip().lower() in ["", "null"]:
            return None

        # Convert to string
        value_str = str(value).strip()

        # Remove decimal if present (e.g., '6767676566.0' -> '6767676566')
        if value_str.endswith(".0"):
            value_str = value_str[:-2]

        # Ensure it's digits only
        if not value_str.isdigit():
            raise ValueError("Phone number must contain only digits")

        if len(value_str) != 10:
            raise ValueError("Phone number must be exactly 10 digits")

        return value_str

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
    gender: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    last_updated_by: Optional[str] = None

class ILPUserCreate(ILPUserBase):
    profile_pic_file: Optional[UploadFile] = File(None)  # File is optional
    
class UserRoleResponse(BaseModel):
    name: str
    type: Optional[str]  # role_type
    level_id: Optional[int]

class ILPUserDetailedResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: Optional[str]
    phone1: Optional[str]
    phone2: Optional[str]
    gender: Optional[str]
    address: Optional[str]
    profile_pic: str  # URL to profile pic
    roles: List[UserRoleResponse]

class ILPUser(ILPUserBase):
    id: str

    class Config:
        orm_mode = True
