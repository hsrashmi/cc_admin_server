from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..dependencies import get_db_session
from ..domain.school import service, schemas, models
from ..domain.role_assignment import service as roleService
from ..domain.role_assignment.schemas import StudentUpdateRequest
from .util_functions import UserQueryRequest, generate_uuid, string_hash, success_message_response, get_order_by_conditions, get_filter_conditions, get_select_fields
from pydantic import BaseModel, Field
from resources.strings import CLASS_DOES_NOT_EXIST_ERROR, INVALID_FIELDS_IN_REQUEST_ERROR

router = APIRouter(tags=["schoolClass"])

@router.post("/schoolClass", response_model=schemas.SchoolResponse)
async def create_School(school_class: schemas.ClassBase, db: Session = Depends(get_db_session)):
    unique_id = str(generate_uuid())   
    updated_class = school_class.model_copy(update={"id": unique_id})   
    return await service.create_school_class(db=db, school_class=updated_class)

@router.get("/schoolClass/{school_id}", response_model=List[schemas.ClassDetailsBase])
async def get_school_classes(school_id: str, db: Session = Depends(get_db_session)):
    schools = await service.get_school_classes(db, school_id=school_id)
    return schools

@router.get("/schoolClassStudents/{class_id}")
async def get_school_class_students(class_id: str, db: Session = Depends(get_db_session)):
    db_school = await roleService.get_school_class_students(db, class_id=class_id)
    return db_school

@router.put("/schoolClassStudents/{class_id}")
async def update_school_class_students(class_id: str, request:StudentUpdateRequest, db: Session = Depends(get_db_session)):
    db_school = await roleService.update_school_class_students(db, class_id=class_id, students_list=request.student_ids)
    return db_school

@router.get("/unassignedSchoolStudents/{school_id}")
async def get_unassigned_school_students(school_id: str, db: Session = Depends(get_db_session)):
    db_school = await roleService.get_unassigned_school_students(db, school_id=school_id)
    return db_school

@router.put("/unassignedSchoolStudents/{school_id}")
async def update_unassigned_school_students(school_id: str, request:StudentUpdateRequest, db: Session = Depends(get_db_session)):
    db_school = await roleService.update_unassigned_school_students(db, school_id=school_id, students_list=request.student_ids)
    return db_school

@router.post("/allSchoolDetails/", response_model=List[schemas.SchoolDetailsResponse],  response_model_exclude_none=True)
async def get_all_schools_details(
        request: UserQueryRequest, 
        db: Session = Depends(get_db_session)):
     # Get all valid columns from the User model
    table_fields = models.School.get_school_details_fields()  
    
    selected_fields = get_select_fields(request.fields, table_fields)

    filter_cond = get_filter_conditions(request.filters, table_fields)

    ordering = get_order_by_conditions(request.order_by, table_fields)

    # Calculate Limit and Offset based on Page Number
    limit = request.page_size
    skip = (request.page_no - 1) * request.page_size  # Offset calculation

    db_schools = await service.get_all_schools_details(db, selected_fields, filter_cond, ordering, skip=skip, limit=limit)
    return db_schools
    # return [dict(zip(selected_fields, school)) for school in db_schools]

@router.put("/schoolClass/{class_id}", response_model=success_message_response)
async def update_School(class_id: str, school_class: schemas.ClassUpdate, db: Session = Depends(get_db_session)):
    db_school_class = await service.get_school_class(db, class_id=class_id)
    return await service.update_school_class(db, class_id=class_id, school_class=school_class)

@router.delete("/schoolClass/{class_id}", response_model=success_message_response)
async def delete_School_class(class_id: str, db: Session = Depends(get_db_session)):
    return await service.delete_school_class(db=db, class_id=class_id)
