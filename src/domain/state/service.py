from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
import re
from . import models, schemas
from fastapi import HTTPException
from resources.strings import STATE_CREATE_SUCCESSFUL, STATE_DELETE_SUCCESSFUL, STATE_UPDATE_SUCCESSFUL, STATE_DOES_NOT_EXIST_ERROR


async def get_state(db: AsyncSession, state_id: str):
    result = await db.execute(select(models.State).filter(models.State.id == state_id))
    return result.scalars().first()

async def get_state_by_name(db: AsyncSession, name: str):
    result = await db.execute(
        select(models.State).filter(func.lower(models.State.name) == name.lower())
    )    
    return result.scalar()

async def get_states(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.State).offset(skip).limit(limit))
    return result.scalars().all()


async def get_states_by_params(
    db: AsyncSession, selected_fields: list, filters: list, ordering: list, skip: int = 0, limit: int = 100
):
    orm_attributes = [getattr(models.State, field) for field in selected_fields]
    result = await db.execute(
        select(*orm_attributes).filter(*filters).order_by(*ordering).offset(skip).limit(limit)
    )
    return result.all()


async def create_state(db: AsyncSession, state: schemas.StateBase):
    try:
        db_state = models.State(**state.model_dump())
        db.add(db_state)
        await db.commit()
        await db.refresh(db_state)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return db_state


async def update_state(db: AsyncSession, state_id: str, state: schemas.StateUpdate):
    try:
        result = await db.execute(select(models.State).filter(models.State.id == state_id))
        db_state = result.scalars().first()
        if not db_state:
            raise HTTPException(status_code=404, detail=STATE_DOES_NOT_EXIST_ERROR)

        for key, value in state.model_dump(exclude_none=True).items():
            setattr(db_state, key, value)

        await db.commit()
        await db.refresh(db_state)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": STATE_UPDATE_SUCCESSFUL}


async def delete_state(db: AsyncSession, state_id: str):
    try:
        result = await db.execute(select(models.State).filter(models.State.id == state_id))
        db_state = result.scalars().first()
        if not db_state:
            raise HTTPException(status_code=404, detail=STATE_DOES_NOT_EXIST_ERROR)

        await db.delete(db_state)
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": STATE_DELETE_SUCCESSFUL}


def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)
    return match.group(1) if match else "Error occurred while processing the request"
