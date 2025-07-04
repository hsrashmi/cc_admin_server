from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import desc, asc, and_
from datetime import datetime
import re
from . import models, schemas
from fastapi import HTTPException
from resources.strings import (
    ACTIVITY_CREATE_SUCCESSFUL, ACTIVITY_DELETE_SUCCESSFUL,
    ACTIVITY_UPDATE_SUCCESSFUL, ACTIVITY_DOES_NOT_EXIST_ERROR
)


async def get_activity(db: AsyncSession, activity_id: str):
    result = await db.execute(select(models.Activity).filter(models.Activity.id == activity_id))
    return result.scalar()


async def get_activities(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Activity).offset(skip).limit(limit))
    return result.scalars().all()

async def get_activities_with_assets(db: AsyncSession, filters: schemas.ActivityFilter, skip: int = 0, limit: int = 100
):
    stmt = (
        select(models.Activity)
        .options(selectinload(models.Activity.assets))
        .order_by(models.Activity.auto_release_month_and_day.desc())
    )

    conditions = []
    if filters.year.startDate and filters.year.endDate:
        conditions.append(
            and_(
                models.Activity.auto_release_month_and_day >= filters.year.startDate,
                models.Activity.auto_release_month_and_day <= filters.year.endDate,
            )
        )
    if filters.grade:
        conditions.append(models.Activity.grade == filters.grade)

    if conditions:
        stmt = stmt.where(and_(*conditions))
    
    stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    return result.scalars().all()

async def get_activities_by_params(db: AsyncSession, selected_fields: list, filters: list, ordering: list, skip: int = 0, limit: int = 100):
    orm_attributes = [getattr(models.Activity, field) for field in selected_fields]
    result = await db.execute(
        select(*orm_attributes).filter(*filters).order_by(*ordering).offset(skip).limit(limit))
    
    return result.scalars().all()


async def get_activities_year(db: AsyncSession):
    result = await db.execute(select(models.Activity.auto_release_month_and_day))
    dates = result.scalars().all()
    years_set = set()
    for dt in dates:
        if dt:
            if isinstance(dt, str):
                dt = datetime.fromisoformat(dt)
            year = dt.year
            month = dt.month
            academic_year = f"{year}-{year + 1}" if month >= 5 else f"{year - 1}-{year}"
            years_set.add(academic_year)

    return sorted(years_set, reverse=True)

async def create_activity(db: AsyncSession, activity: schemas.ActivityBase):
    try:
        db_activity = models.Activity(**activity.model_dump())
        db.add(db_activity)
        await db.commit()
        await db.refresh(db_activity)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return db_activity


async def update_activity(db: AsyncSession, activity_id: str, activity: schemas.ActivityUpdate):
    try:
        result = await db.execute(select(models.Activity).filter(models.Activity.id == activity_id))
        db_activity = result.scalar()

        if not db_activity:
            raise HTTPException(status_code=404, detail=ACTIVITY_DOES_NOT_EXIST_ERROR)

        for key, value in activity.model_dump(exclude_none=True).items():
            setattr(db_activity, key, value)

        await db.commit()
        await db.refresh(db_activity)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": ACTIVITY_UPDATE_SUCCESSFUL}


async def delete_activity(db: AsyncSession, activity_id: str):
    try:
        result = await db.execute(select(models.Activity).filter(models.Activity.id == activity_id))
        db_activity = result.scalar()

        if not db_activity:
            raise HTTPException(status_code=404, detail=ACTIVITY_DOES_NOT_EXIST_ERROR)

        await db.delete(db_activity)
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": ACTIVITY_DELETE_SUCCESSFUL}


def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)
    return match.group(1) if match else "Error occurred while processing the request"
