from fastapi import APIRouter, Depends
from sqlalchemy import select, func, literal, union_all, desc
from sqlalchemy.ext.asyncio import AsyncSession
from ..dependencies import get_db_session
from ..domain.ilpuser.models import ILPUser
from ..domain.role.models import Role
from ..domain.role_assignment.models import UserRole
from ..domain.state.models import State
from ..domain.zone.models import Zone
from ..domain.district.models import District
from ..domain.school.models import School, Class
from ..domain.block.models import Block

from sqlalchemy import select, func, desc
from .common_schemas import DashboardSummaryResponse 

router = APIRouter(tags=["dashboard"])

@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db_session)):
    # 1. Total Active Users
    users_count = await db.scalar(
        select(func.count()).select_from(ILPUser).where(ILPUser.is_active == True)
    )

    # 2. Role Distribution
    role_dist_query = await db.execute(
        select(Role.name, func.count())
        .select_from(Role)
        .join(UserRole, Role.id == UserRole.role_id)
        .group_by(Role.name)
    )
    roles = [{"role": r[0], "count": r[1]} for r in role_dist_query.all()]

    # 3. Region Counts
    states = await db.scalar(select(func.count()).select_from(State))
    zones = await db.scalar(select(func.count()).select_from(Zone))
    districts = await db.scalar(select(func.count()).select_from(District))
    blocks = await db.scalar(select(func.count()).select_from(Block))

    # 4. Recent Regions (5 latest from all region levels)
    state_q = select(
        State.name.label("name"),
        literal("state").label("type"),
        State.created_at.label("created_at")
    )
    zone_q = select(
        Zone.name.label("name"),
        literal("zone").label("type"),
        Zone.created_at.label("created_at")
    )
    district_q = select(
        District.name.label("name"),
        literal("district").label("type"),
        District.created_at.label("created_at")
    )
    block_q = select(
        Block.name.label("name"),
        literal("block").label("type"),
        Block.created_at.label("created_at")
    )

    region_union = union_all(state_q, zone_q, district_q, block_q).subquery()
    recent_regions_query = await db.execute(
        select(
            region_union.c.name,
            region_union.c.type,
            region_union.c.created_at
        )
        .order_by(region_union.c.created_at.desc())
        .limit(10)
    )

    recent_regions = [
        {
            "name": row.name,
            "type": row.type,
            "created_at": row.created_at.isoformat() if row.created_at else None
        }
        for row in recent_regions_query.all()
    ]

    # 5. Schools and Classes
    schools = await db.scalar(select(func.count()).select_from(School))
    classes = await db.scalar(select(func.count()).select_from(Class))

        # 6. Recent Schools (10 latest)
    recent_schools_query = await db.execute(
        select(
            School.name.label("name"),
            School.city.label("city"),
            School.created_at.label("created_at")
        )
        .order_by(School.created_at.desc())
        .limit(10)
    )

    recent_schools = []
    for row in recent_schools_query.all():
        recent_schools.append({
            "name": row.name,
            "city": row.city,
            "created_at": row.created_at.isoformat() if row.created_at else None
        })

    return {
        "active_users": users_count,
        "role_distribution": roles,
        "region_counts": {
            "states": states,
            "zones": zones,
            "districts": districts,
            "blocks": blocks
        },
        "recent_regions": recent_regions,
        "school_counts": {
            "schools": schools,
            "classes": classes
        },
        "recent_schools": recent_schools
    }