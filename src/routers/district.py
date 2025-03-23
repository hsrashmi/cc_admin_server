from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..dependencies import get_db_session
from ..domain.district import service, schemas, models
from .util_functions import UserQueryRequest, LoginQueryRequest, generate_uuid, string_hash, success_message_response, get_order_by_conditions, get_filter_conditions, get_select_fields
from resources.strings import DISTRICT_DOES_NOT_EXIST_ERROR, DISTRICT_ALREADY_EXISTS_ERROR

router = APIRouter(tags=["districts"])

@router.post("/district/", response_model=schemas.DistrictResponse)
async def create_district(district: schemas.DistrictBase, db: Session = Depends(get_db_session)):
    db_district = await service.get_district_by_name(db, name=district.name)
    if db_district:
        raise HTTPException(status_code=400, detail=DISTRICT_ALREADY_EXISTS_ERROR)
    unique_id = str(generate_uuid())    
    updated_district = district.model_copy(update={"id": unique_id})   
    return await service.create_district(db=db, district=updated_district)

@router.get("/district/", response_model=List[schemas.DistrictResponse])
async def read_districts(page_no: int = 1, page_size: int = 100, db: Session = Depends(get_db_session)):
    limit = page_size
    skip = (page_no - 1) * page_size  # Offset calculation        
    districts = await service.get_districts(db, skip=skip, limit=limit)  # ✅ Await the async function
    return districts

@router.get("/district/{district_id}", response_model=schemas.DistrictResponse)
async def read_district(district_id: str, db: Session = Depends(get_db_session)):
    db_district = await service.get_district(db, district_id=district_id)
    if db_district is None:
        raise HTTPException(status_code=404, detail=DISTRICT_DOES_NOT_EXIST_ERROR)
    return db_district

@router.post("/getDistrictsByParams/", response_model=List[schemas.DistrictResponse])
async def read_districts_by_params(
        request: UserQueryRequest, 
        db: Session = Depends(get_db_session)):

    # Get all valid columns from the district model
    table_fields = models.District.get_valid_fields()    
  
    selected_fields = get_select_fields(request.fields, table_fields)

    filter_cond = get_filter_conditions(request.filters, table_fields)

    ordering = get_order_by_conditions(request.order_by, table_fields)

    # Calculate Limit and Offset based on Page Number
    limit = request.page_size
    skip = (request.page_no - 1) * request.page_size  # Offset calculation

    db_districts = await service.get_districts_by_params(db, selected_fields, filter_cond, ordering, skip=skip, limit=limit)    
    return db_districts

@router.put("/district/{district_id}", response_model=success_message_response)
async def update_district(district_id: str, district: schemas.DistrictUpdate, db: Session = Depends(get_db_session)):
    db_district = await service.get_district(db, district_id=district_id)
    if db_district is None:
        raise HTTPException(status_code=404, detail=DISTRICT_DOES_NOT_EXIST_ERROR)
    return await service.update_district(db=db, district_id=district_id, district=district)

@router.delete("/district/{district_id}", response_model=success_message_response)
async def delete_district(district_id: str, db: Session = Depends(get_db_session)):
    db_district = await service.get_district(db, district_id=district_id)
    if db_district is None:
        raise HTTPException(status_code=404, detail=DISTRICT_DOES_NOT_EXIST_ERROR)
    return await service.delete_district(db=db, district_id=district_id)