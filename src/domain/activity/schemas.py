from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from ..asset.schemas import AssetResponse
from typing import List
from datetime import date

class ActivityBase(BaseModel):
    id: Optional[str] = None
    name: str
    long_name: str
    description: str
    track: str
    long_name: str
    additional_data: Optional[str] = None
    auto_release_month_and_day: Optional[str] = None
    complete_within_days: int
    grade: Optional[str] = None  
    sequence_number: Optional[int] = None
    reward_points: int    
    created_at: Optional[datetime] = datetime.now()
    created_by: Optional[str] = "54be662c-eab6-4e60-8c43-40cd744d1fbd"

class ActivityUpdate(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    long_name: Optional[str] = None
    description: Optional[str] = None
    track: Optional[str] = None
    long_name: Optional[str] = None
    additional_data: Optional[str] = None
    auto_release_month_and_day: Optional[str] = None
    complete_within_days: Optional[int] = None
    grade: Optional[str] = None  
    sequence_number: Optional[int] = None
    reward_points: Optional[int] = None
    last_updated_at: Optional[datetime] = datetime.now()
    last_updated_by: Optional[str] = None

class ActivityResponse(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    long_name: Optional[str] = None
    description: Optional[str] = None
    track: Optional[str] = None
    additional_data: Optional[str] = None
    auto_release_month_and_day: Optional[str] = None
    complete_within_days: Optional[int] = None
    grade: Optional[str] = None  
    sequence_number: Optional[int] = None
    reward_points: Optional[int] = None 
    created_at: Optional[datetime]= None
    created_by: Optional[str]= None
    last_updated_at: Optional[datetime]= None
    last_updated_by: Optional[str]= None

class ActivityWithAssetsResponse(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    long_name: Optional[str] = None
    description: Optional[str] = None
    track: Optional[str] = None
    additional_data: Optional[str] = None
    auto_release_month_and_day: Optional[str] = None
    complete_within_days: Optional[int] = None
    grade: Optional[str] = None  
    sequence_number: Optional[int] = None
    reward_points: Optional[int] = None 
    created_at: Optional[datetime]= None
    created_by: Optional[str]= None
    last_updated_at: Optional[datetime]= None
    last_updated_by: Optional[str]= None
    assets: Optional[List[AssetResponse]] = []

class DateRange(BaseModel):
    startDate: Optional[str] = None
    endDate: Optional[str] = None

class ActivityFilter(BaseModel):
    year: Optional[DateRange]
    grade: Optional[str]

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: str

    class Config:
        orm_mode = True


