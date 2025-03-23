from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
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


async def get_activities_by_params(db: AsyncSession, selected_fields: list, filters: list, ordering: list, skip: int = 0, limit: int = 100):
    orm_attributes = [getattr(models.Activity, field) for field in selected_fields]
    result = await db.execute(
        select(*orm_attributes).filter(*filters).order_by(*ordering).offset(skip).limit(limit)
    )
    return result.scalars().all()


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
