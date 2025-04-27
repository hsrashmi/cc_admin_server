from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..dependencies import get_db_session
from ..domain.activity import service, schemas, models
from .util_functions import UserQueryRequest, LoginQueryRequest, generate_uuid, string_hash, success_message_response, get_order_by_conditions, get_filter_conditions, get_select_fields
from resources.strings import BLOCK_DOES_NOT_EXIST_ERROR, BLOCK_ALREADY_EXISTS_ERROR

router = APIRouter(tags=["activities"])

@router.post("/activity/", response_model=schemas.ActivityResponse)
async def create_block(activity: schemas.BlockBase, db: Session = Depends(get_db_session)):
    db_block = await service.get_block_by_name(db, name=activity.name)
    if db_block:
        raise HTTPException(status_code=400, detail=BLOCK_ALREADY_EXISTS_ERROR)
    unique_id = str(generate_uuid())    
    updated_block = activity.model_copy(update={"id": unique_id})   
    return await service.create_block(db=db, activity=updated_block)

@router.get("/activity/", response_model=List[schemas.ActivityResponse])
async def read_activities(page_no: int = 1, page_size: int = 100, db: Session = Depends(get_db_session)):
    limit = page_size
    skip = (page_no - 1) * page_size  # Offset calculation        
    activities = await service.get_activities(db, skip=skip, limit=limit)  # ✅ Await the async function
    return activities

@router.get("/activity/{block_id}", response_model=schemas.ActivityResponse)
async def read_block(block_id: str, db: Session = Depends(get_db_session)):
    db_block = await service.get_block(db, block_id=block_id)
    if db_block is None:
        raise HTTPException(status_code=404, detail=BLOCK_DOES_NOT_EXIST_ERROR)
    return db_block

@router.post("/getBlocksByParams/", response_model=List[schemas.ActivityResponse])
async def read_activities_by_params(
        request: UserQueryRequest, 
        db: Session = Depends(get_db_session)):

    # Get all valid columns from the activity model
    table_fields = models.Activity.get_valid_fields()    
  
    selected_fields = get_select_fields(request.fields, table_fields)

    filter_cond = get_filter_conditions(request.filters, table_fields)

    ordering = get_order_by_conditions(request.order_by, table_fields)

    # Calculate Limit and Offset based on Page Number
    limit = request.page_size
    skip = (request.page_no - 1) * request.page_size  # Offset calculation

    db_activities = await service.get_activities_by_params(db, selected_fields, filter_cond, ordering, skip=skip, limit=limit)    
    return db_activities

@router.put("/activity/{block_id}", response_model=success_message_response)
async def update_block(block_id: str, activity: schemas.BlockUpdate, db: Session = Depends(get_db_session)):
    db_block = await service.get_block(db, block_id=block_id)
    if db_block is None:
        raise HTTPException(status_code=404, detail=BLOCK_DOES_NOT_EXIST_ERROR)
    return await service.update_block(db=db, block_id=block_id, activity=activity)

@router.delete("/activity/{block_id}", response_model=success_message_response)
async def delete_block(block_id: str, db: Session = Depends(get_db_session)):
    db_block = await service.get_block(db, block_id=block_id)
    if db_block is None:
        raise HTTPException(status_code=404, detail=BLOCK_DOES_NOT_EXIST_ERROR)
    return await service.delete_block(db=db, block_id=block_id)