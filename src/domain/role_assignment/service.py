from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from fastapi import HTTPException
from typing import Optional, List
import re
from ..school.models import Class, School
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.attributes import InstrumentedAttribute
from ..block.models import Block
from ..district.models import District
from ..zone.models import Zone
from ..state.models import State
from . import models, schemas
from ..ilpuser.models import ILPUser
from ..role.service import get_role_by_name
from ..role.models import Role, RoleEnum
from ..role_assignment.models import UserRole, LevelEnum
from resources.strings import (
    USER_ROLE_ASSOCIATION_DOES_NOT_EXIST_ERROR, ROLE_DELETE_SUCCESSFUL,
    ROLE_UPDATE_SUCCESSFUL, TEACHER_UPDATE_SUCCESSFUL
)

async def get_users_roles(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.UserRole).offset(skip).limit(limit))
    return result.scalars().all()

async def get_user_role(db: AsyncSession, assignment_id:str):
    result = await db.execute(select(models.UserRole).filter(models.UserRole.id == assignment_id))    
    return result.scalar()

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


async def delete_user_role(db: AsyncSession, assignment_id: str):
    try:
        result = await db.execute(select(models.UserRole).filter(models.UserRole.id == assignment_id))
        db_user_role = result.scalar()

        if not db_user_role:
            raise HTTPException(status_code=404, detail=USER_ROLE_ASSOCIATION_DOES_NOT_EXIST_ERROR)

        await db.delete(db_user_role)
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return {"message": ROLE_DELETE_SUCCESSFUL}

# async def delete_user_role_by_levelid(db: AsyncSession, level_id: str):
#     try:
#         result = await db.execute(select(models.UserRole).filter(models.UserRole.level_id == level_id))
#         db_user_role = result.scalar()

#         if not db_user_role:
#             raise HTTPException(status_code=404, detail=USER_ROLE_ASSOCIATION_DOES_NOT_EXIST_ERROR)

#         await db.delete(db_user_role)
#         await db.commit()
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

#     return {"message": ROLE_DELETE_SUCCESSFUL}

async def delete_user_role_by_field(db: AsyncSession, field_name: str, field_value: str):
    try:
        # Get the column dynamically from the model
        column_attr: InstrumentedAttribute = getattr(models.UserRole, field_name, None)

        if not column_attr:
            raise HTTPException(status_code=400, detail=f"Invalid field name: {field_name}")

        # Perform the query
        result = await db.execute(select(models.UserRole).filter(column_attr == field_value))
        db_user_role = result.scalar()

        if not db_user_role:
            raise HTTPException(status_code=404, detail=USER_ROLE_ASSOCIATION_DOES_NOT_EXIST_ERROR)

        await db.delete(db_user_role)
        await db.commit()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return {"message": ROLE_DELETE_SUCCESSFUL}

async def get_user_role_by_fields(db: AsyncSession, filters: dict):
    try:
        # Dynamically build filter conditions
        conditions = []
        for field, value in filters.items():
            column_attr = getattr(models.UserRole, field, None)
            if column_attr is None:
                raise HTTPException(status_code=400, detail=f"Invalid field name: {field}")
            conditions.append(column_attr == value)

        query = (
            select(models.UserRole)
            .options(
                selectinload(models.UserRole.user),
                selectinload(models.UserRole.role),
            )
            .filter(or_(*conditions))  # or and_(*conditions) if you want AND
        )

        result = await db.execute(query)
        user_roles = result.scalars().all()  # 🚀 Fetch all matches

        if not user_roles:
            raise HTTPException(status_code=404, detail=USER_ROLE_ASSOCIATION_DOES_NOT_EXIST_ERROR)

        # Convert each user_role to dict
        return [
            {
                "id": ur.id,
                "user_id": ur.user_id,
                "user_name": f"{ur.user.first_name} {ur.user.last_name}" if ur.user else None,
                "role_id": ur.role_id,
                "role_name": ur.role.name if ur.role else None,
                "access_type": ur.access_type,
                "level": ur.level,
                "level_id": ur.level_id,
                "created_at": ur.created_at,
                "last_updated_at": ur.last_updated_at,
            }
            for ur in user_roles
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

async def get_user_role_by_field(db: AsyncSession, field_name: str, field_value: str):
    try:
        column_attr = getattr(models.UserRole, field_name, None)
        if not column_attr:
            raise HTTPException(status_code=400, detail=f"Invalid field name: {field_name}")

        query = select(models.UserRole).options(
            selectinload(models.UserRole.user),
            selectinload(models.UserRole.role),
        ).filter(column_attr == field_value)

        result = await db.execute(query)
        user_role = result.scalar()

        if not user_role:
            raise HTTPException(status_code=404, detail=USER_ROLE_ASSOCIATION_DOES_NOT_EXIST_ERROR)

        return {
            "id": user_role.id,
            "user_id": user_role.user_id,
            "user_name": f"{user_role.user.first_name} {user_role.user.last_name}" if user_role.user else None,
            "role_id": user_role.role_id,
            "role_name": user_role.role.name if user_role.role else None,
            "access_type": user_role.access_type,
            "level": user_role.level,
            "level_id": user_role.level_id,
            "created_at": user_role.created_at,
            "last_updated_at": user_role.last_updated_at,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))


async def get_user_role_by_heirarchy(db: AsyncSession, region_level: LevelEnum, region_id: str):
    region_chain = []

    # Step 1: walk up the region hierarchy
    if region_level == LevelEnum.BLOCK:
        block = await db.get(Block, region_id)
        region_chain.append((LevelEnum.BLOCK, block.id, block.name))
        district = await db.get(District, block.district_id)
        region_chain.append((LevelEnum.DISTRICT, district.id, district.name))
        zone = await db.get(Zone, district.zone_id)
        region_chain.append((LevelEnum.ZONE, zone.id, zone.name))
        state = await db.get(State, zone.state_id)
        region_chain.append((LevelEnum.STATE, state.id, state.name))
        region_chain.append((LevelEnum.ROOT, None, "ROOT"))

    elif region_level == LevelEnum.DISTRICT:
        district = await db.get(District, region_id)
        region_chain.append((LevelEnum.DISTRICT, district.id, district.name))
        zone = await db.get(Zone, district.zone_id)
        region_chain.append((LevelEnum.ZONE, zone.id, zone.name))
        state = await db.get(State, zone.state_id)
        region_chain.append((LevelEnum.STATE, state.id, state.name))
        region_chain.append((LevelEnum.ROOT, None, "ROOT"))

    elif region_level == LevelEnum.ZONE:
        zone = await db.get(Zone, region_id)
        region_chain.append((LevelEnum.ZONE, zone.id, zone.name))
        state = await db.get(State, zone.state_id)
        region_chain.append((LevelEnum.STATE, state.id, state.name))
        region_chain.append((LevelEnum.ROOT, None, "ROOT"))

    elif region_level == LevelEnum.STATE:
        state = await db.get(State, region_id)
        region_chain.append((LevelEnum.STATE, state.id, state.name))
        region_chain.append((LevelEnum.ROOT, None, "ROOT"))

    elif region_level == LevelEnum.ROOT:
        region_chain.append((LevelEnum.ROOT, None, "ROOT"))

    # Step 2: query UserRole for each level in chain
    results = []
    for level, level_id, region_name in region_chain:
        stmt = (
            select(UserRole)
            .where(UserRole.level == level, UserRole.level_id == level_id)
            .options(selectinload(UserRole.user), selectinload(UserRole.role))
        )
        role_assignment = (await db.execute(stmt)).scalars().all()

        for ra in role_assignment:
            results.append({
                "id": ra.id,
                "user_id": ra.user.id,
                "user_name": f"{ra.user.first_name} {ra.user.last_name}",
                "role_id": ra.role_id,
                "role_name": ra.role.name,
                "access_type": ra.access_type,
                "level": level.name,
                "level_id": ra.level_id,
                "region_name": region_name,
            })
    return results

async def get_teachers(school_id: str, db: AsyncSession, skip: int = 0, limit: int = 100):
    student_role_id_subquery = (
        select(Role.id)
        .filter(Role.name == RoleEnum.TEACHER)
        .limit(1)
        .scalar_subquery()
    )
        
    result = await db.execute(
        select(models.UserRole.user_id)
        .filter(
            (models.UserRole.level == models.LevelEnum.SCHOOL) &
            ((models.UserRole.level_id == school_id) | (models.UserRole.level_id == None)),
            models.UserRole.role_id == student_role_id_subquery
        )
        .offset(skip)
        .limit(limit)
    )

    user_ids = result.scalars().all()

    users = await db.execute(
        select(ILPUser).filter(ILPUser.id.in_(user_ids))
    )
    return users.scalars().all()


async def assign_teacher_to_class(teacherDetails: schemas.TeacherCreate, db: AsyncSession):
    role = await get_role_by_name(RoleEnum.TEACHER, db=db)
    teacher_items = teacherDetails.model_dump()
    updated_details = {
            "role_id": role.id, 
            'level': models.LevelEnum.CLASS, 
            'access_type': models.AccessTypeEnum.WRITE,
            'level_id': teacher_items['class_id'],
            'user_id':  teacher_items['user_id'],
            'id': teacher_items['id']
            }
    user_role = schemas.UserRoleBase.model_construct(**updated_details) 
    return await create_user_role(db, user_role)

async def update_teacher_to_class(teacherDetails: schemas.TeacherUpdate, assignment_id: str, db: AsyncSession):
    try:        
        db_assignment_dtl = await get_user_role(db=db, assignment_id=assignment_id)
        if not db_assignment_dtl:
            raise HTTPException(status_code=404, detail=USER_ROLE_ASSOCIATION_DOES_NOT_EXIST_ERROR)

        # Handle the special mapping for class_id → level_id
        field_mapping = {"class_id": "level_id"}

        for key, value in teacherDetails.model_dump(exclude_none=True).items():
            # Use the mapped field if it exists, else use the original key
            setattr(db_assignment_dtl, field_mapping.get(key, key), value)

        await db.commit()
        await db.refresh(db_assignment_dtl)
    except Exception as e:        
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return {"message": TEACHER_UPDATE_SUCCESSFUL}


async def get_school_class_students(db: AsyncSession, class_id: str):
    try:
        student_role_id_subquery = (
            select(Role.id)
            .filter(Role.name == RoleEnum.STUDENT)
            .limit(1)
            .scalar_subquery()
        )
        # Query to get all students in a given class
        result = await db.execute(
            select(ILPUser)
            .join(UserRole, UserRole.user_id == ILPUser.id)
            .filter(
                UserRole.level_id == class_id,
                UserRole.level == LevelEnum.CLASS,
                UserRole.role_id == student_role_id_subquery
            )
        )
        students = result.scalars().all()
        return students
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

async def update_school_class_students(db: AsyncSession, class_id: str, students_list: list):
    try:
        await db.execute(
            UserRole.__table__.update()
            .where(UserRole.user_id.in_(students_list))
            .values(                
                level=LevelEnum.CLASS,                
                level_id=class_id
            )
        )
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    
async def get_unassigned_school_students(db: AsyncSession, school_id: str):
    try:
        student_role_id_subquery = (
            select(Role.id)
            .filter(Role.name == RoleEnum.STUDENT)
            .limit(1)
            .scalar_subquery()
        )
        # Query to get all students in a given class
        result = await db.execute(
            select(ILPUser)
            .join(UserRole, UserRole.user_id == ILPUser.id)
            .filter(
                UserRole.level_id == school_id,
                UserRole.level == LevelEnum.SCHOOL,
                UserRole.role_id == student_role_id_subquery
            )
        )
        students = result.scalars().all()
        return students
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    


async def update_unassigned_school_students(db: AsyncSession, school_id: str, students_list: list):
    try:
        await db.execute(
            UserRole.__table__.update()
            .where(UserRole.user_id.in_(students_list))
            .values(                
                level=LevelEnum.SCHOOL,                
                level_id=school_id
            )
        )
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    

async def get_user_roles_with_hierarchy(session, user_id: str):
    query = (
        select(UserRole)
        .options(
            joinedload(UserRole.role),  # Load role details (role_name)
            joinedload(UserRole.user),  # Load user details (user_name)

            # Load hierarchy relationships
            joinedload(UserRole.class_info).joinedload(Class.school).joinedload(School.block)
            .joinedload(Block.district).joinedload(District.zone).joinedload(Zone.state),
            
            joinedload(UserRole.school_info).joinedload(School.block)
            .joinedload(Block.district).joinedload(District.zone).joinedload(Zone.state),

            joinedload(UserRole.block_info).joinedload(Block.district)
            .joinedload(District.zone).joinedload(Zone.state),

            joinedload(UserRole.district_info).joinedload(District.zone).joinedload(Zone.state),

            joinedload(UserRole.zone_info).joinedload(Zone.state),

            joinedload(UserRole.state_info),
        )
        .where(UserRole.user_id == user_id)
    )
    result = await session.execute(query)
    return result.scalars().all()

def serialize_user_role(user_role: UserRole):
    level = user_role.level.name

    # Fetch role and user details
    role_name = user_role.role.name if user_role.role else None
    user_name = f"{user_role.user.first_name} {user_role.user.last_name}" if user_role.user else None

    class_info = user_role.class_info if level == "CLASS" else None
    school = class_info.school if class_info else (user_role.school_info if level == "SCHOOL" else None)
    block = school.block if school else (user_role.block_info if level == "BLOCK" else None)
    district = block.district if block else (user_role.district_info if level == "DISTRICT" else None)
    zone = district.zone if district else (user_role.zone_info if level == "ZONE" else None)
    state = zone.state if zone else (user_role.state_info if level == "STATE" else None)

    response = {
        "id": user_role.id,
        "user_id": user_role.user_id,
        "user_name": user_name,  # Include user name
        "access_type": user_role.access_type,
        "role_id": user_role.role_id,
        "role_name": role_name,  # Include role name
        "level": level,
        "level_id": user_role.level_id,
    }

    if level == "CLASS":
        response.update({
            "class_id": user_role.level_id,
            "class_name": class_info.grade+" "+class_info.section if class_info else None,
            "school_id": school.id if school else None,
            "school_name": school.name if school else None,
            "block_id": block.id if block else None,
            "block_name": block.name if block else None,
            "district_id": district.id if district else None,
            "district_name": district.name if district else None,
            "zone_id": zone.id if zone else None,
            "zone_name": zone.name if zone else None,
            "state_id": state.id if state else None,
            "state_name": state.name if state else None,
        })
    elif level == "SCHOOL":
        response.update({
            "school_id": user_role.level_id,
            "school_name": school.name if school else None,
            "block_id": block.id if block else None,
            "block_name": block.name if block else None,
            "district_id": district.id if district else None,
            "district_name": district.name if district else None,
            "zone_id": zone.id if zone else None,
            "zone_name": zone.name if zone else None,
            "state_id": state.id if state else None,
            "state_name": state.name if state else None,
        })
    elif level == "BLOCK":
        response.update({
            "block_id": user_role.level_id,
            "block_name": block.name if block else None,
            "district_id": district.id if district else None,
            "district_name": district.name if district else None,
            "zone_id": zone.id if zone else None,
            "zone_name": zone.name if zone else None,
            "state_id": state.id if state else None,
            "state_name": state.name if state else None,
        })
    elif level == "DISTRICT":
        response.update({
            "district_id": user_role.level_id,
            "district_name": district.name if district else None,
            "zone_id": zone.id if zone else None,
            "zone_name": zone.name if zone else None,
            "state_id": state.id if state else None,
            "state_name": state.name if state else None,
        })
    elif level == "ZONE":
        response.update({
            "zone_id": user_role.level_id,
            "zone_name": zone.name if zone else None,
            "state_id": state.id if state else None,
            "state_name": state.name if state else None,
        })
    elif level == "STATE":
        response.update({
            "state_id": user_role.level_id,
            "state_name": state.name if state else None,
        })

    return response

def _extract_detail_text(error_message: str) -> str:
    print("!!! Error !!! ", error_message)
    match = re.search(r"DETAIL:\s+(.*)", error_message)
    return match.group(1) if match else "Error occurred while processing the request"


