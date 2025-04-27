from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..dependencies import get_db_session
from ..domain.school import service, schemas, models
from .util_functions import UserQueryRequest, generate_uuid, string_hash, success_message_response, get_order_by_conditions, get_filter_conditions, get_select_fields
from pydantic import BaseModel, Field
from resources.strings import SCHOOL_DOES_NOT_EXIST_ERROR, INVALID_FIELDS_IN_REQUEST_ERROR

router = APIRouter(tags=["school"])


@router.post("/school/", response_model=schemas.SchoolResponse)
async def create_School(school: schemas.SchoolBase, db: Session = Depends(get_db_session)):
    unique_id = str(generate_uuid())   
    updated_school = school.model_copy(update={"id": unique_id})   
    return await service.create_school(db=db, school=updated_school)

@router.get("/school/", response_model=List[schemas.SchoolResponse])
async def read_schools(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    schools = await service.get_schools(db, skip=skip, limit=limit)
    return schools

@router.get("/school/{school_id}", response_model=schemas.SchoolResponse)
async def read_School(school_id: str, db: Session = Depends(get_db_session)):
    db_school = await service.get_School(db, school_id=school_id)
    if db_school is None:
        raise HTTPException(status_code=404, detail=SCHOOL_DOES_NOT_EXIST_ERROR)
    return db_school

@router.get("/schoolDetails/{school_id}", response_model=schemas.SchoolDetailsResponse)
async def read_School_details(school_id: str, db: Session = Depends(get_db_session)):
    db_school = await service.get_school_details(db, school_id=school_id)
    if db_school is None:
        raise HTTPException(status_code=404, detail=SCHOOL_DOES_NOT_EXIST_ERROR)
    return db_school

@router.post("/allSchoolDetails/", response_model=List[schemas.SchoolDetailsResponse],  response_model_exclude_none=True)
async def read_schools_details(
        request: UserQueryRequest, 
        db: Session = Depends(get_db_session)):
     # Get all valid columns from the User model
    table_fields = models.School.get_school_details_fields()  
    
    selected_fields = get_select_fields(request.fields, table_fields)
    
    # filter_cond = get_filter_conditions(request.filters, table_fields)
    filter_cond = request.filters

    ordering = get_order_by_conditions(request.order_by, table_fields)

    # Calculate Limit and Offset based on Page Number
    limit = request.page_size
    skip = (request.page_no - 1) * request.page_size  # Offset calculation

    db_schools = await service.get_all_schools_details(db, selected_fields, filter_cond, ordering, skip=skip, limit=limit)
    return db_schools
    # return [dict(zip(selected_fields, school)) for school in db_schools]

@router.post("/getSchoolsByParams/", response_model=list, response_model_exclude_none=True)
async def read_schools_by_params(
        request: UserQueryRequest, 
        db: Session = Depends(get_db_session)):
    
    # Get all valid columns from the User model
    table_fields = models.School.get_valid_fields()    
    
    selected_fields = get_select_fields(request.fields, table_fields)

    filter_cond = get_filter_conditions(request.filters, table_fields)

    ordering = get_order_by_conditions(request.order_by, table_fields)

    # Calculate Limit and Offset based on Page Number
    limit = request.page_size
    skip = (request.page_no - 1) * request.page_size  # Offset calculation

    db_schools = await service.get_schools_by_params(db, selected_fields, filter_cond, ordering, skip=skip, limit=limit)
    return [dict(zip(selected_fields, school)) for school in db_schools]

@router.put("/school/{school_id}", response_model=success_message_response)
async def update_School(school_id: str, school: schemas.SchoolUpdate, db: Session = Depends(get_db_session)):
    db_school = await service.get_school(db, school_id=school_id)
    if db_school is None:
        raise HTTPException(status_code=404, detail=SCHOOL_DOES_NOT_EXIST_ERROR)
    return await service.update_school(db=db, school_id=school_id, school=school)

@router.delete("/school/{school_id}", response_model=success_message_response)
async def delete_School(school_id: str, db: Session = Depends(get_db_session)):
    db_school = await service.get_school(db, school_id=school_id)
    if db_school is None:
        raise HTTPException(status_code=404, detail=SCHOOL_DOES_NOT_EXIST_ERROR)
    return await service.delete_school(db=db, school_id=school_id)
