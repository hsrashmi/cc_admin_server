from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import re
from . import models, schemas
from fastapi import HTTPException
from resources.strings import (
    ASSET_CREATE_SUCCESSFUL, ASSET_DELETE_SUCCESSFUL, 
    ASSET_DOES_NOT_EXIST_ERROR, ASSET_UPDATE_SUCCESSFUL
)


async def get_asset(db: AsyncSession, asset_id: str):
    result = await db.execute(select(models.Asset).filter(models.Asset.id == asset_id))
    return result.scalar()


async def get_assets(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Asset).offset(skip).limit(limit))
    return result.scalars().all()


async def get_assets_by_params(db: AsyncSession, selected_fields: list, filters: list, ordering: list, skip: int = 0, limit: int = 100):
    orm_attributes = [getattr(models.Asset, field) for field in selected_fields]
    result = await db.execute(
        select(*orm_attributes).filter(*filters).order_by(*ordering).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def create_asset(db: AsyncSession, asset: schemas.AssetBase):
    try:
        db_asset = models.Asset(**asset.model_dump())
        db.add(db_asset)
        await db.commit()
        await db.refresh(db_asset)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return db_asset


async def update_asset(db: AsyncSession, asset_id: str, asset: schemas.AssetUpdate):
    try:
        result = await db.execute(select(models.Asset).filter(models.Asset.id == asset_id))
        db_asset = result.scalar()

        if not db_asset:
            raise HTTPException(status_code=404, detail=ASSET_DOES_NOT_EXIST_ERROR)

        for key, value in asset.model_dump(exclude_none=True).items():
            setattr(db_asset, key, value)

        await db.commit()
        await db.refresh(db_asset)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": ASSET_UPDATE_SUCCESSFUL}


async def delete_asset(db: AsyncSession, asset_id: str):
    try:
        result = await db.execute(select(models.Asset).filter(models.Asset.id == asset_id))
        db_asset = result.scalar()

        if not db_asset:
            raise HTTPException(status_code=404, detail=ASSET_DOES_NOT_EXIST_ERROR)

        await db.delete(db_asset)
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": ASSET_DELETE_SUCCESSFUL}


def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)
    return match.group(1) if match else "Error occurred while processing the request"
