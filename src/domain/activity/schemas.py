from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ActivityBase(BaseModel):
    id: Optional[str] = None
    name: str
    long_name: str
    description: str
    track = str
    long_name = str
    additional_data = Optional[str] = None
    auto_release_month_and_day = Optional[str] = None
    complete_winthin_days = int
    grades = Optional[str] = None  
    sequence_number = Optional[str] = None
    reward_points = int    
    created_at: Optional[datetime] = datetime.now()
    created_by: Optional[str] = "root@ilp.com"

class ActivityUpdate(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    long_name: Optional[str] = None
    description: Optional[str] = None
    track = Optional[str] = None
    long_name = Optional[str] = None
    additional_data = Optional[str] = None
    auto_release_month_and_day = Optional[str] = None
    complete_winthin_days = Optional[int] = None
    grades = Optional[str] = None  
    sequence_number = Optional[str] = None
    reward_points = Optional[int] = None
    last_updated_at: Optional[datetime] = datetime.now()
    last_updated_by: Optional[str] = None

class ActivityResponse(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    long_name: Optional[str] = None
    description: Optional[str] = None
    track = Optional[str] = None
    long_name = Optional[str] = None
    additional_data = Optional[str] = None
    auto_release_month_and_day = Optional[str] = None
    complete_winthin_days = Optional[int] = None
    grades = Optional[str] = None  
    sequence_number = Optional[str] = None
    reward_points = Optional[int] = None 
    created_at: Optional[datetime]= None
    created_by: Optional[str]= None
    last_updated_at: Optional[datetime]= None
    last_updated_by: Optional[str]= None

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: str

    class Config:
        orm_mode = True


