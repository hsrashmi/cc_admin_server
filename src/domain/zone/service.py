from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
import re
from . import models, schemas
from fastapi import HTTPException
from resources.strings import ZONE_UPDATE_SUCCESSFUL, ZONE_DOES_NOT_EXIST_ERROR, ZONE_DELETE_SUCCESSFUL


async def get_zone(db: AsyncSession, zone_id: str):
    result = await db.execute(select(models.Zone).filter(models.Zone.id == zone_id))
    return result.scalars().first()

async def get_zone_by_name(db: AsyncSession, name: str):
    result = await db.execute(
        select(models.Zone).filter(func.lower(models.Zone.name) == name.lower())
    )    
    return result.scalar()

async def get_zones(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Zone).offset(skip).limit(limit))
    return result.scalars().all()


async def get_zones_by_params(
    db: AsyncSession, selected_fields: list, filters: list, ordering: list, skip: int = 0, limit: int = 100
):
    orm_attributes = [getattr(models.Zone, field) for field in selected_fields]
    result = await db.execute(
        select(*orm_attributes).filter(*filters).order_by(*ordering).offset(skip).limit(limit)
    )
    return result.all()

async def create_zone(db: AsyncSession, zone: schemas.ZoneBase):    
    try:
        db_zone = models.Zone(**zone.model_dump())
        db.add(db_zone)
        await db.commit()
        await db.refresh(db_zone)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return db_zone


async def update_zone(db: AsyncSession, zone_id: str, zone: schemas.ZoneUpdate):
    try:
        result = await db.execute(select(models.Zone).filter(models.Zone.id == zone_id))
        db_zone = result.scalars().first()
        if not db_zone:
            raise HTTPException(status_code=404, detail=ZONE_DOES_NOT_EXIST_ERROR)

        for key, value in zone.model_dump(exclude_none=True).items():
            setattr(db_zone, key, value)

        await db.commit()
        await db.refresh(db_zone)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": ZONE_UPDATE_SUCCESSFUL}


async def delete_zone(db: AsyncSession, zone_id: str):
    try:
        result = await db.execute(select(models.Zone).filter(models.Zone.id == zone_id))
        db_zone = result.scalars().first()
        if not db_zone:
            raise HTTPException(status_code=404, detail=ZONE_DOES_NOT_EXIST_ERROR)

        await db.delete(db_zone)
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": ZONE_DELETE_SUCCESSFUL}


def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)
    return match.group(1) if match else "Error occurred while processing the request"
