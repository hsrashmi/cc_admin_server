from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..dependencies import get_db_session
from ..domain.zone import service, schemas, models
from .util_functions import UserQueryRequest, LoginQueryRequest, generate_uuid, string_hash, success_message_response, get_order_by_conditions, get_filter_conditions, get_select_fields
from resources.strings import ZONE_DOES_NOT_EXIST_ERROR, ZONE_ALREADY_EXISTS_ERROR

router = APIRouter(tags=["zones"])

@router.post("/zone/", response_model=schemas.ZoneResponse)
async def create_zone(zone: schemas.ZoneBase, db: Session = Depends(get_db_session)):
    db_zone = await service.get_zone_by_name(db, name=zone.name)
    if db_zone:
        raise HTTPException(status_code=400, detail=ZONE_ALREADY_EXISTS_ERROR)
    unique_id = str(generate_uuid())    
    updated_zone = zone.model_copy(update={"id": unique_id})   
    return await service.create_zone(db=db, zone=updated_zone)

@router.get("/zone/", response_model=List[schemas.ZoneResponse])
async def read_zones(page_no: int = 1, page_size: int = 100, db: Session = Depends(get_db_session)):
    limit = page_size
    skip = (page_no - 1) * page_size  # Offset calculation        
    zones = await service.get_zones(db, skip=skip, limit=limit)  # ✅ Await the async function
    return zones

@router.get("/zone/{zone_id}", response_model=schemas.ZoneResponse)
async def read_zone(zone_id: str, db: Session = Depends(get_db_session)):
    db_zone = await service.get_zone(db, zone_id=zone_id)
    if db_zone is None:
        raise HTTPException(status_code=404, detail=ZONE_DOES_NOT_EXIST_ERROR)
    return db_zone

@router.post("/getZonesByParams/", response_model=List[schemas.ZoneResponse])
async def read_zones_by_params(
        request: UserQueryRequest, 
        db: Session = Depends(get_db_session)):

    # Get all valid columns from the zone model
    table_fields = models.Zone.get_valid_fields()    
  
    selected_fields = get_select_fields(request.fields, table_fields)

    filter_cond = get_filter_conditions(request.filters, table_fields)

    ordering = get_order_by_conditions(request.order_by, table_fields)

    # Calculate Limit and Offset based on Page Number
    limit = request.page_size
    skip = (request.page_no - 1) * request.page_size  # Offset calculation

    db_zones = await service.get_zones_by_params(db, selected_fields, filter_cond, ordering, skip=skip, limit=limit)    
    return db_zones

@router.put("/zone/{zone_id}", response_model=success_message_response)
async def update_zone(zone_id: str, zone: schemas.ZoneUpdate, db: Session = Depends(get_db_session)):
    db_zone = await service.get_zone(db, zone_id=zone_id)
    if db_zone is None:
        raise HTTPException(status_code=404, detail=ZONE_DOES_NOT_EXIST_ERROR)
    return await service.update_zone(db=db, zone_id=zone_id, zone=zone)

@router.delete("/zone/{zone_id}", response_model=success_message_response)
async def delete_zone(zone_id: str, db: Session = Depends(get_db_session)):
    db_zone = await service.get_zone(db, zone_id=zone_id)
    if db_zone is None:
        raise HTTPException(status_code=404, detail=ZONE_DOES_NOT_EXIST_ERROR)
    return await service.delete_zone(db=db, zone_id=zone_id)