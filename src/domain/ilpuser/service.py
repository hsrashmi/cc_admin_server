from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, text
from fastapi import HTTPException, UploadFile,  File, Depends, HTTPException, Form
import bcrypt
import re
import shutil
import os
from . import models, schemas
from ..role_assignment.models import UserRole
from ..role.models import Role
from ..role_assignment.service import get_user_roles_with_hierarchy, serialize_user_role
from resources.strings import (
    USER_DOES_NOT_EXIST_ERROR, USER_DELETE_SUCCESSFUL,
    USER_UPDATE_SUCCESSFUL, AUTHENTICATION_FAILED_ERROR
)

UPLOAD_DIR = "uploads/profile_pics"
os.makedirs(UPLOAD_DIR, exist_ok=True) 

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

async def get_users_with_roles_by_params(
    db: AsyncSession,
    selected_fields: list,
    filters: list,
    ordering: list,
    skip: int = 0,
    limit: int = 100,
):
    orm_attributes = [getattr(models.ILPUser, field) for field in selected_fields]
     # Start the query with join to Role via UserRole
    query = (
        select(*orm_attributes)
        .select_from(models.ILPUser)
        .outerjoin(UserRole, UserRole.user_id == models.ILPUser.id)
        .outerjoin(Role, Role.id == UserRole.role_id)
        .filter(*filters)
        .order_by(*ordering)
        .offset(skip)
        .limit(limit)
    ).distinct()  # Distinct to avoid duplicate users due to joins

    result = await db.execute(query)
    users = result.all()

    enriched_users = []
    for row in users:
        user_dict = row._mapping if hasattr(row, "_mapping") else row.__dict__
        user_id = user_dict.get("id")

        # Fetch role + hierarchy for this user
        roles = await get_user_roles_with_hierarchy(db, user_id)
        roles_data = [serialize_user_role(role) for role in roles]

        enriched_users.append({
            **user_dict,
            "roles": roles_data
        })

    return enriched_users

async def get_users_with_roles_by_params_count(db: AsyncSession, filters: list  # This should include filters from ILPUser and joins (role name, user name etc.)
) -> int:
    print("fileter ", filters)
    stmt = (
        select(func.count(func.distinct(models.ILPUser.id)))
        .select_from(models.ILPUser)
        .outerjoin(UserRole, UserRole.user_id == models.ILPUser.id)
        .outerjoin(Role, Role.id == UserRole.role_id)
        .filter(*filters)
    )
    result = await db.execute(stmt)
    return result.scalar()

async def create_user(db: AsyncSession, user: schemas.ILPUserCreate):
    try:
        user_dict = user.model_dump()  # Convert Pydantic model to dictionary
        
        if user.profile_pic_file:
            file_path = f"{UPLOAD_DIR}/{user_dict['id']}_{user.profile_pic_file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(user.profile_pic_file.file, buffer)
            user_dict["profile_pic_url"] = file_path  # Store image path

        # Remove the extra field manually
        user_dict.pop("profile_pic_file", None)  # Now this will work ✅

        db_user = models.ILPUser(**user_dict)        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
    except Exception as e:
        print("Error creating db entry for user -", str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return db_user

async def update_user(db: AsyncSession, user_id: str, user: schemas.ILPUserUpdateWithFileSchema):
    try:
        result = await db.execute(select(models.ILPUser).filter(models.ILPUser.id == user_id))
        db_user = result.scalar()

        if not db_user:
            raise HTTPException(status_code=404, detail=USER_DOES_NOT_EXIST_ERROR)

        user_dict = user.model_dump(exclude_none=True)  # Convert to dictionary

        if user.profile_pic_file:
            file_path = f"{UPLOAD_DIR}/{user_id}_{user.profile_pic_file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(user.profile_pic_file.file, buffer)
            user_dict["profile_pic_url"] = file_path  # Store image path

        # Remove the extra field manually
        user_dict.pop("profile_pic_file", None)  # Now this works ✅

        # Update only valid fields
        for key, value in user_dict.items():
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

async def get_enum_values(db: AsyncSession, enum_type_name:str):
    query = text(f"""
        SELECT unnest(enum_range(NULL::{enum_type_name})) AS value;
    """)
    
    # Await the result of the query execution
    result = await db.execute(query)
    
    # Fetch the rows from the result and iterate over them
    return [row[0] for row in result.fetchall()]

def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)
    return match.group(1) if match else "Error occurred while processing the request"


