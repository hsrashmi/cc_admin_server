from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
import re
from . import models, schemas
from fastapi import HTTPException
from resources.strings import (
    DISTRICT_CREATE_SUCCESSFUL, DISTRICT_UPDATE_SUCCESSFUL,
    DISTRICT_DELETE_SUCCESSFUL, DISTRICT_DOES_NOT_EXIST_ERROR
)


async def get_district(db: AsyncSession, dist_id: str):
    result = await db.execute(select(models.District).filter(models.District.id == dist_id))
    return result.scalar()

async def get_district_by_name(db: AsyncSession, name: str):
    result = await db.execute(
        select(models.Zone).filter(func.lower(models.Zone.name) == name.lower())
    )    
    return result.scalar()

async def get_districts(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.District).offset(skip).limit(limit))
    return result.scalars().all()


async def get_districts_by_params(db: AsyncSession, selected_fields: list, filters: list, ordering: list, skip: int = 0, limit: int = 100):
    orm_attributes = [getattr(models.District, field) for field in selected_fields]
    result = await db.execute(
        select(*orm_attributes).filter(*filters).order_by(*ordering).offset(skip).limit(limit)
    )
    return result.all()


async def create_district(db: AsyncSession, district: schemas.DistrictBase):
    try:
        db_district = models.District(**district.model_dump())
        db.add(db_district)
        await db.commit()
        await db.refresh(db_district)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return db_district


async def update_district(db: AsyncSession, dist_id: str, district: schemas.DistrictUpdate):
    try:
        result = await db.execute(select(models.District).filter(models.District.id == dist_id))
        db_district = result.scalar()

        if not db_district:
            raise HTTPException(status_code=404, detail=DISTRICT_DOES_NOT_EXIST_ERROR)

        for key, value in district.model_dump(exclude_none=True).items():
            setattr(db_district, key, value)

        await db.commit()
        await db.refresh(db_district)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": DISTRICT_UPDATE_SUCCESSFUL}


async def delete_district(db: AsyncSession, dist_id: str):
    try:
        result = await db.execute(select(models.District).filter(models.District.id == dist_id))
        db_district = result.scalar()

        if not db_district:
            raise HTTPException(status_code=404, detail=DISTRICT_DOES_NOT_EXIST_ERROR)

        await db.delete(db_district)
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": DISTRICT_DELETE_SUCCESSFUL}


def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)
    return match.group(1) if match else "Error occurred while processing the request"
