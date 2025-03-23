from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
import re
from . import models, schemas
from resources.strings import (
    USER_ROLE_ASSOCIATION_DOES_NOT_EXIST_ERROR, ROLE_DELETE_SUCCESSFUL,
    ROLE_UPDATE_SUCCESSFUL, ROLE_DOES_NOT_EXIST_ERROR
)


async def get_roles(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Role).offset(skip).limit(limit))
    return result.scalars().all()


async def create_role(db: AsyncSession, role: schemas.RoleBase):
    try:
        db_role = models.Role(**role.model_dump())
        db.add(db_role)
        await db.commit()
        await db.refresh(db_role)
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return db_role


async def update_role(db: AsyncSession, role_id: str, role: schemas.RoleUpdate):
    try:
        result = await db.execute(select(models.Role).filter(models.Role.id == role_id))
        db_role = result.scalar()

        if not db_role:
            raise HTTPException(status_code=404, detail=ROLE_DOES_NOT_EXIST_ERROR)

        for key, value in role.model_dump(exclude_none=True).items():
            setattr(db_role, key, value)

        await db.commit()
        await db.refresh(db_role)
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return {"message": ROLE_UPDATE_SUCCESSFUL}


async def delete_role(db: AsyncSession, role_id: str):
    try:
        result = await db.execute(select(models.Role).filter(models.Role.id == role_id))
        db_role = result.scalar()

        if not db_role:
            raise HTTPException(status_code=404, detail=ROLE_DOES_NOT_EXIST_ERROR)

        await db.delete(db_role)
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return {"message": ROLE_DELETE_SUCCESSFUL}


async def get_users_roles(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.UserRole).offset(skip).limit(limit))
    return result.scalars().all()


async def get_user_roles(db: AsyncSession, user_id: str, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.UserRole).filter(models.UserRole.user_id == user_id).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def create_user_role(db: AsyncSession, user_role: schemas.UserRoleBase):
    try:
        db_user_role = models.UserRole(**user_role.model_dump())
        db.add(db_user_role)
        await db.commit()
        await db.refresh(db_user_role)
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return db_user_role


async def update_user_role(db: AsyncSession, user_role_id: str, role: schemas.UserRoleUpdate):
    try:
        result = await db.execute(select(models.UserRole).filter(models.UserRole.id == user_role_id))
        db_user_role = result.scalar()

        if not db_user_role:
            raise HTTPException(status_code=404, detail=USER_ROLE_ASSOCIATION_DOES_NOT_EXIST_ERROR)

        for key, value in role.model_dump(exclude_none=True).items():
            setattr(db_user_role, key, value)

        await db.commit()
        await db.refresh(db_user_role)
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return {"message": ROLE_UPDATE_SUCCESSFUL}


async def delete_user_role(db: AsyncSession, role_id: str):
    try:
        result = await db.execute(select(models.UserRole).filter(models.UserRole.id == role_id))
        db_user_role = result.scalar()

        if not db_user_role:
            raise HTTPException(status_code=404, detail=USER_ROLE_ASSOCIATION_DOES_NOT_EXIST_ERROR)

        await db.delete(db_user_role)
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return {"message": ROLE_DELETE_SUCCESSFUL}


def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)
    return match.group(1) if match else "Error occurred while processing the request"
