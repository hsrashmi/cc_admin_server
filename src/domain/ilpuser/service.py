from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from fastapi import HTTPException
import bcrypt
import re
from . import models, schemas
from resources.strings import (
    USER_DOES_NOT_EXIST_ERROR, USER_DELETE_SUCCESSFUL,
    USER_UPDATE_SUCCESSFUL, AUTHENTICATION_FAILED_ERROR
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


async def login_user(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(models.ILPUser).filter(func.lower(models.ILPUser.email) == email.lower()))
    user = result.scalar()

    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail=AUTHENTICATION_FAILED_ERROR)

    return user


async def get_user(db: AsyncSession, user_id: str):
    result = await db.execute(select(models.ILPUser).filter(models.ILPUser.id == user_id))
    return result.scalar()


async def get_user_by_email(db: AsyncSession, email: str):    
    result = await db.execute(select(models.ILPUser).filter(func.lower(models.ILPUser.email) == email.lower()))
    return result.scalar()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):    
    result = await db.execute(select(models.ILPUser).offset(skip).limit(limit))    
    return result.scalars().all()


async def get_users_by_params(db: AsyncSession, selected_fields: list, filters: list, ordering: list, skip: int = 0, limit: int = 100):
    orm_attributes = [getattr(models.ILPUser, field) for field in selected_fields]
    result = await db.execute(
        select(*orm_attributes).filter(*filters).order_by(*ordering).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def create_user(db: AsyncSession, user: schemas.ILPUserBase):
    try:
        db_user = models.ILPUser(**user.model_dump())
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
    except Exception as e:
        print("Error creating db entry for user -", str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return db_user


async def update_user(db: AsyncSession, user_id: str, user: schemas.ILPUserUpdate):
    try:
        result = await db.execute(select(models.ILPUser).filter(models.ILPUser.id == user_id))
        db_user = result.scalar()

        if not db_user:
            raise HTTPException(status_code=404, detail=USER_DOES_NOT_EXIST_ERROR)

        for key, value in user.model_dump(exclude_none=True).items():
            setattr(db_user, key, value)

        await db.commit()
        await db.refresh(db_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return {"message": USER_UPDATE_SUCCESSFUL}


async def delete_user(db: AsyncSession, user_id: str):
    try:
        result = await db.execute(select(models.ILPUser).filter(models.ILPUser.id == user_id))
        db_user = result.scalar()

        if not db_user:
            raise HTTPException(status_code=404, detail=USER_DOES_NOT_EXIST_ERROR)

        await db.delete(db_user)
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return {"message": USER_DELETE_SUCCESSFUL}


def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)
    return match.group(1) if match else "Error occurred while processing the request"
