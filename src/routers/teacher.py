from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..dependencies import get_db_session
from ..domain.role_assignment import service, schemas, models
from .util_functions import UserQueryRequest, LoginQueryRequest, generate_uuid, string_hash, success_message_response, get_order_by_conditions, get_filter_conditions, get_select_fields
from resources.strings import STATE_DOES_NOT_EXIST_ERROR, STATE_ALREADY_EXISTS_ERROR, USER_ROLE_ASSOCIATION_DOES_NOT_EXIST_ERROR

router = APIRouter(tags=["teachers"])

@router.post("/teacher/", response_model=schemas.UserRoleResponse)
async def create_role(role: schemas.UserRoleBase, db: Session = Depends(get_db_session)):
    db_role = await service.get_teachers(db, name=role.name)
    if db_role:
        raise HTTPException(status_code=400, detail=STATE_ALREADY_EXISTS_ERROR)
    unique_id = str(generate_uuid())    
    updated_role = role.model_copy(update={"id": unique_id})   
    return await service.create_role(db=db, role=updated_role)

@router.post("/assignTeacherToClass/", response_model=schemas.UserRoleResponse)
async def assign_teacher_to_class(teacherDetails: schemas.TeacherCreate, db: Session = Depends(get_db_session)):
    unique_id = str(generate_uuid())    
    updated_details = teacherDetails.model_copy(update={"id": unique_id}) 
    db_teacher = await service.assign_teacher_to_class(updated_details, db)
    return db_teacher

@router.put("/assignTeacherToClass/{assignment_id}", response_model=success_message_response)
async def update_teacher_to_class(assignment_id: str, teacherDetails: schemas.TeacherUpdate, db: Session = Depends(get_db_session)):
    try: 
        return await service.update_teacher_to_class(teacherDetails=teacherDetails, assignment_id=assignment_id, db=db)        
    except Exception as e:     
        print("------------ error ", str(e))   
        return {"message": USER_ROLE_ASSOCIATION_DOES_NOT_EXIST_ERROR}

@router.get("/teacher/{school_id}")
async def read_roles(school_id: str, page_no: int = 1, page_size: int = 100, db: Session = Depends(get_db_session)):
    limit = page_size
    skip = (page_no - 1) * page_size  # Offset calculation        
    return await service.get_teachers(school_id, db, skip=skip, limit=limit)  # ✅ Await the async function
    
