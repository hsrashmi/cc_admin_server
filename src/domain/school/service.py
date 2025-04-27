from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, literal, String, cast
from fastapi import HTTPException
from typing import Optional
import re
from . import models, schemas
from ..role_assignment.models import UserRole, AccessTypeEnum, LevelEnum
from ..ilpuser.models import ILPUser
from ..role.models import Role, RoleEnum
from resources.strings import (
    SCHOOL_DOES_NOT_EXIST_ERROR, SCHOOL_DELETE_SUCCESSFUL, SCHOOL_UPDATE_SUCCESSFUL, CLASS_DOES_NOT_EXIST_ERROR, CLASS_UPDATE_SUCCESSFUL
)
from sqlalchemy.orm import selectinload

async def get_school(db: AsyncSession, school_id: str):
    result = await db.execute(select(models.School).filter(models.School.id == school_id))
    return result.scalar()

async def get_school_by_dise_code(db: AsyncSession, dise_code: int):
    result = await db.execute(select(models.School).filter(models.School.dise_code == dise_code))
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

async def get_all_schools_details(db: AsyncSession, selected_fields: list, filters: dict, ordering: list, skip: int = 0, limit: int = 100):
    query = select(models.School).options(
        selectinload(models.School.block)
        .selectinload(models.Block.district)
        .selectinload(models.District.zone)
        .selectinload(models.Zone.state),
        selectinload(models.School.creator),  # Load creator relationship
        selectinload(models.School.updater),  # Load updater relationship
    )
    # Map search fields to models and relationships
    search_field_mapping = {
        # School fields
        "name": models.School.name,
        "dise_code": models.School.dise_code,
        "address": models.School.address,  # Assuming description is part of address
        # Related fields
        "block_name": models.Block.name,
        "district_name": models.District.name,
        "zone_name": models.Zone.name,
        "state_name": models.State.name,
        "created_by": models.ILPUser.email,
        "updated_by": models.ILPUser.email,
        "state_id":  models.State.id, 
        "block_id": models.Block.id, 
        "district_id": models.District.id, 
        "zone_id": models.Zone.id
    }
    # Join related tables and apply filters
    filter_data = []
    for key, value in filters.items():
        if key in search_field_mapping:
            if isinstance(search_field_mapping[key].type, String):
                filter_data.append(search_field_mapping[key].ilike(f"%{value}%"))  # Case-insensitive for strings
            else:
                filter_data.append(cast(search_field_mapping[key], String).ilike(f"%{value}%"))  # Convert non-string columns to text

        # Perform joins if necessary
        if key in ["block_name", "district_name", "zone_name", "state_id", "block_id", "district_id", "zone_id", "state_id"]:
            query = query.join(models.School.block)
        if key in ["district_name", "zone_name", "state_name", "district_id", "zone_id", "state_id"]:
            query = query.join(models.Block.district)
        if key in ["zone_name", "state_name", "zone_id", "state_id"]:
            query = query.join(models.District.zone)
        if key in ["state_name", "state_id"]:
            query = query.join(models.Zone.state)
        if key in ["created_by", "updated_by"]:
            query = query.join(models.School.creator) if key == "created_by" else query.join(models.School.updater)

        # Apply the filter condition (case-insensitive search)
    for each_filter in filter_data:
        query = query.filter(each_filter)

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
        result = await db.execute(select(models.School).filter(models.School.id == school_id))
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
        result = await db.execute(select(models.School).filter(models.School.id == school_id))
        db_school = result.scalar()

        if not db_school:
            raise HTTPException(status_code=404, detail=SCHOOL_DOES_NOT_EXIST_ERROR)

        await db.delete(db_school)
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return {"message": SCHOOL_DELETE_SUCCESSFUL}

async def get_school_class(db: AsyncSession, class_id: str):
    result = await db.execute(select(models.Class).filter(models.Class.id == class_id))
    return result.scalar()

async def get_school_classes(db: AsyncSession, school_id: str):
    # Fetch role_id for RoleEnum.STUDENT
    student_role_id_subquery = (
        select(Role.id)
        .filter(Role.name == RoleEnum.STUDENT)
        .limit(1)
        .scalar_subquery()
    )

    # Subquery to get class teacher's user_id
    subquery_teacher = (
        select(UserRole.user_id)
        .filter(UserRole.level_id == models.Class.id, UserRole.level == LevelEnum.CLASS)
        .limit(1)
        .scalar_subquery()
    )

    subquery_teacher_assignment_id = (
        select(UserRole.id)
        .filter(UserRole.level_id == models.Class.id, UserRole.level == LevelEnum.CLASS)
        .limit(1)
        .scalar_subquery()
    )

    # Subquery to count students in each class
    subquery_student_count = (
        select(func.count())
        .filter(
            UserRole.level_id == models.Class.id,
            UserRole.level == LevelEnum.CLASS,
            UserRole.role_id == student_role_id_subquery  # Filter by student role_id
        )
        .scalar_subquery()
    )

    # Correlated subquery to get teacher's name
    subquery_teacher_name = (
        select(func.concat(ILPUser.first_name, literal(" "), ILPUser.last_name))
        .join(UserRole, UserRole.user_id == ILPUser.id)
        .filter(
            UserRole.level_id == models.Class.id,
            UserRole.level == LevelEnum.CLASS
        )
        .limit(1)
        .scalar_subquery()
    )

    # Main query to fetch class information with teacher's name and student count
    result = await db.execute(
        select(
            models.Class.id.label('class_id'),
            models.Class.grade,
            models.Class.section,
            subquery_teacher.label('class_teacher_id'),
            subquery_teacher_name.label('class_teacher_name'),
            subquery_student_count.label('student_count'),
            subquery_teacher_assignment_id.label('teacher_assignment_id'),
        ).filter(models.Class.school_id == school_id))

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

async def update_school_class(db: AsyncSession, class_id: str, school_class: schemas.ClassUpdate):    
    try:
        result = await db.execute(select(models.Class).filter(models.Class.id == class_id))
        db_school = result.scalar()

        if not db_school:
            raise HTTPException(status_code=404, detail=CLASS_DOES_NOT_EXIST_ERROR)

        for key, value in school_class.model_dump(exclude_none=True).items():
            setattr(db_school, key, value)

        await db.commit()
        await db.refresh(db_school)
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return {"message": CLASS_UPDATE_SUCCESSFUL}


async def delete_school_class(db: AsyncSession, class_id: str):
    try:
        result = await db.execute(
            select(models.Class).filter(
                models.Class.id == class_id
            )
        )
        db_class = result.scalar()

        if not db_class:
            raise HTTPException(status_code=404, detail=CLASS_DOES_NOT_EXIST_ERROR)

        await db.delete(db_class)
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return {"message": SCHOOL_DELETE_SUCCESSFUL}


def _extract_detail_text(error_message: str) -> str:
    print(error_message)
    match = re.search(r"DETAIL:\s+(.*)", error_message)
    return match.group(1) if match else "Error occurred while processing the request"
