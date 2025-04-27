from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class RoleDistributionItem(BaseModel):
    role: str
    count: int

class RegionCounts(BaseModel):
    states: int
    zones: int
    districts: int
    blocks: int

class RegionItem(BaseModel):
    name: str
    type: str
    created_at: Optional[str]  # You can change to datetime if you prefer

class SchoolCounts(BaseModel):
    schools: int
    classes: int

class RecentSchoolItem(BaseModel):
    name: str
    city: Optional[str]
    created_at: Optional[str]  # ISO format or datetime

class DashboardSummaryResponse(BaseModel):
    active_users: int
    role_distribution: List[RoleDistributionItem]
    region_counts: RegionCounts
    recent_regions: List[RegionItem]
    school_counts: SchoolCounts
    recent_schools: List[RecentSchoolItem]



