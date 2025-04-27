from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
import re
from . import models, schemas
from fastapi import HTTPException
from resources.strings import (
    BLOCK_CREATE_SUCCESSFUL, BLOCK_UPDATE_SUCCESSFUL,
    BLOCK_DELETE_SUCCESSFUL, BLOCK_DOES_NOT_EXIST_ERROR
)


async def get_block(db: AsyncSession, block_id: str):
    result = await db.execute(select(models.Block).filter(models.Block.id == block_id))
    return result.scalar()

async def get_block_by_name(db: AsyncSession, name: str):
    result = await db.execute(
        select(models.Block).filter(func.lower(models.Block.name) == name.lower())
    )    
    return result.scalar()

async def get_blocks(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Block).offset(skip).limit(limit))
    return result.scalars().all()


async def get_blocks_by_params(db: AsyncSession, selected_fields: list, filters: list, ordering: list, skip: int = 0, limit: int = 100):
    orm_attributes = [getattr(models.Block, field) for field in selected_fields]
    result = await db.execute(
        select(*orm_attributes).filter(*filters).order_by(*ordering).offset(skip).limit(limit)
    )
    return result.all()


async def create_block(db: AsyncSession, block: schemas.BlockBase):
    try:
        db_block = models.Block(**block.model_dump())
        db.add(db_block)
        await db.commit()
        await db.refresh(db_block)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return db_block


async def update_block(db: AsyncSession, block_id: str, block: schemas.BlockUpdate):
    try:
        result = await db.execute(select(models.Block).filter(models.Block.id == block_id))
        db_block = result.scalar()

        if not db_block:
            raise HTTPException(status_code=404, detail=BLOCK_DOES_NOT_EXIST_ERROR)

        for key, value in block.model_dump(exclude_none=True).items():
            setattr(db_block, key, value)

        await db.commit()
        await db.refresh(db_block)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": BLOCK_UPDATE_SUCCESSFUL}


async def delete_block(db: AsyncSession, block_id: str):
    try:
        result = await db.execute(select(models.Block).filter(models.Block.id == block_id))
        db_block = result.scalar()

        if not db_block:
            raise HTTPException(status_code=404, detail=BLOCK_DOES_NOT_EXIST_ERROR)

        await db.delete(db_block)
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": BLOCK_DELETE_SUCCESSFUL}


def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)
    return match.group(1) if match else "Error occurred while processing the request"
