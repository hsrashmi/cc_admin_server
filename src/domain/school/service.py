from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from fastapi import HTTPException
from typing import Optional
import re
from . import models, schemas
from ..role.models import UserRole
from resources.strings import (
    SCHOOL_DOES_NOT_EXIST_ERROR, SCHOOL_DELETE_SUCCESSFUL, SCHOOL_UPDATE_SUCCESSFUL
)
from sqlalchemy.orm import selectinload

async def get_school(db: AsyncSession, school_id: str):
    result = await db.execute(select(models.School).filter(models.School.school_id == school_id))
    return result.scalar()

async def get_schools(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.School).offset(skip).limit(limit))
    return result.scalars().all()

async def get_school_details(db: AsyncSession, school_id: str = None):
    query = select(models.School).options(
        selectinload(models.School.block)
        .selectinload(models.Block.district)
        .selectinload(models.District.zone)
        .selectinload(models.Zone.state),
        selectinload(models.School.creator),  # Load creator relationship
        selectinload(models.School.updater),  # Load updater relationship
    )

    result = await db.execute(query.where(models.School.id == school_id))
    school = result.scalars().first()

    school_data = {}
    school_data = {
        "id": school.id,
        "name": school.name,
        **{field: getattr(school, field) for field in school.__table__.columns.keys()},
        "block_id": school.block.id if school.block else None,
        "block_name": school.block.name if school.block else None,
        "district_id": school.block.district.id if school.block and school.block.district else None,            
        "district_name": school.block.district.name if school.block and school.block.district else None,
        "zone_id": school.block.district.zone.id if school.block and school.block.district and school.block.district.zone else None,            
        "zone_name": school.block.district.zone.name if school.block and school.block.district and school.block.district.zone else None,
        "state_id": school.block.district.zone.state.id if school.block and school.block.district and school.block.district.zone and school.block.district.zone.state else None,           
        "state_name": school.block.district.zone.state.name if school.block and school.block.district and school.block.district.zone and school.block.district.zone.state else None,
        "created_by": school.creator.email if school.creator else None,
        "updated_by": school.updater.email if school.updater else None,
    }
    return school_data

async def get_all_schools_details(db: AsyncSession, selected_fields: list, filters: list, ordering: list, skip: int = 0, limit: int = 100):
    query = select(models.School).options(
        selectinload(models.School.block)
        .selectinload(models.Block.district)
        .selectinload(models.District.zone)
        .selectinload(models.Zone.state),
        selectinload(models.School.creator),  # Load creator relationship
        selectinload(models.School.updater),  # Load updater relationship
    )

    for condition in filters:
        query = query.where(condition)

    if ordering:
        query = query.order_by(*ordering)

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    schools = result.scalars().all()

    # Process results based on requested fields
    school_data = []
    for school in schools:
        school_dict = {
            "id": school.id,
            "name": school.name,
            **{field: getattr(school, field) for field in school.__table__.columns.keys()},
            "block_id": school.block.id if school.block else None,
            "block_name": school.block.name if school.block else None,
            "district_id": school.block.district.id if school.block and school.block.district else None,            
            "district_name": school.block.district.name if school.block and school.block.district else None,
            "zone_id": school.block.district.zone.id if school.block and school.block.district and school.block.district.zone else None,            
            "zone_name": school.block.district.zone.name if school.block and school.block.district and school.block.district.zone else None,
            "state_id": school.block.district.zone.state.id if school.block and school.block.district and school.block.district.zone and school.block.district.zone.state else None,           
            "state_name": school.block.district.zone.state.name if school.block and school.block.district and school.block.district.zone and school.block.district.zone.state else None,
            "created_by": school.creator.email if school.creator else None,
            "updated_by": school.updater.email if school.updater else None,
        }

        # Return only requested fields
        filtered_data = {key: school_dict[key] for key in selected_fields if key in school_dict}
        school_data.append(filtered_data)

    return school_data

async def get_schools_by_params(db: AsyncSession, selected_fields: list, filters: list, ordering: list, skip: int = 0, limit: int = 100):
    orm_attributes = [getattr(models.School, field) for field in selected_fields]
    result = await db.execute(select(*orm_attributes).filter(*filters).order_by(*ordering).offset(skip).limit(limit))
    return result.all()


async def create_school(db: AsyncSession, school: schemas.SchoolBase):
    try:
        db_school = models.School(**school.model_dump())
        db.add(db_school)
        await db.commit()
        await db.refresh(db_school)
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return db_school


async def update_school(db: AsyncSession, school_id: str, school: schemas.SchoolUpdate):
    try:
        result = await db.execute(select(models.School).filter(models.School.school_id == school_id))
        db_school = result.scalar()

        if not db_school:
            raise HTTPException(status_code=404, detail=SCHOOL_DOES_NOT_EXIST_ERROR)

        for key, value in school.model_dump(exclude_none=True).items():
            setattr(db_school, key, value)

        await db.commit()
        await db.refresh(db_school)
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return {"message": SCHOOL_UPDATE_SUCCESSFUL}


async def delete_school(db: AsyncSession, school_id: str):
    try:
        result = await db.execute(select(models.School).filter(models.School.school_id == school_id))
        db_school = result.scalar()

        if not db_school:
            raise HTTPException(status_code=404, detail=SCHOOL_DOES_NOT_EXIST_ERROR)

        await db.delete(db_school)
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return {"message": SCHOOL_DELETE_SUCCESSFUL}


async def get_school_classes(db: AsyncSession, school_id: str):
    subquery_teacher = (
        select(UserRole.user_id)
        .filter(UserRole.level_id == models.Class.id, UserRole.level == 'teacher')
        .limit(1)
        .scalar_subquery()
    )

    subquery_student_count = (
        select(func.count())
        .filter(UserRole.level_id == models.Class.id, UserRole.level == 'student')
        .scalar_subquery()
    )

    result = await db.execute(
        select(
            models.Class.id.label('class_id'),
            models.Class.grade,
            models.Class.section,
            subquery_teacher.label('class_teacher'),
            subquery_student_count.label('student_count'),
        ).filter(models.Class.school_id == school_id)
    )

    return result.mappings().all()


async def create_school_class(db: AsyncSession, school_class: schemas.ClassBase):
    try:
        db_class = models.Class(**school_class.model_dump())
        db.add(db_class)
        await db.commit()
        await db.refresh(db_class)
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return db_class


async def delete_school_class(db: AsyncSession, school_id: str, class_id: str):
    try:
        result = await db.execute(
            select(models.Class).filter(
                models.Class.school_id == school_id,
                models.Class.id == class_id
            )
        )
        db_class = result.scalar()

        if not db_class:
            raise HTTPException(status_code=404, detail=SCHOOL_DOES_NOT_EXIST_ERROR)

        await db.delete(db_class)
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return {"message": SCHOOL_DELETE_SUCCESSFUL}


def _extract_detail_text(error_message: str) -> str:
    print(error_message)
    match = re.search(r"DETAIL:\s+(.*)", error_message)
    return match.group(1) if match else "Error occurred while processing the request"
