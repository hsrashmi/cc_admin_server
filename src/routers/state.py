from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..dependencies import get_db_session
from ..domain.state import service, schemas, models
from .util_functions import UserQueryRequest, LoginQueryRequest, generate_uuid, string_hash, success_message_response, get_order_by_conditions, get_filter_conditions, get_select_fields
from resources.strings import STATE_DOES_NOT_EXIST_ERROR, STATE_ALREADY_EXISTS_ERROR

router = APIRouter(tags=["states"])

@router.post("/state/", response_model=schemas.StateResponse)
async def create_state(state: schemas.StateBase, db: Session = Depends(get_db_session)):
    db_state = await service.get_state_by_name(db, name=state.name)
    if db_state:
        raise HTTPException(status_code=400, detail=STATE_ALREADY_EXISTS_ERROR)
    unique_id = str(generate_uuid())    
    updated_state = state.model_copy(update={"id": unique_id})   
    return await service.create_state(db=db, state=updated_state)

@router.get("/state/", response_model=List[schemas.StateResponse])
async def read_states(page_no: int = 1, page_size: int = 100, db: Session = Depends(get_db_session)):
    limit = page_size
    skip = (page_no - 1) * page_size  # Offset calculation        
    states = await service.get_states(db, skip=skip, limit=limit)  # ✅ Await the async function
    return states

@router.get("/state/{state_id}", response_model=schemas.StateResponse)
async def read_state(state_id: str, db: Session = Depends(get_db_session)):
    db_state = await service.get_state(db, state_id=state_id)
    if db_state is None:
        raise HTTPException(status_code=404, detail=STATE_DOES_NOT_EXIST_ERROR)
    return db_state

@router.post("/getStatesByParams/", response_model=list, response_model_exclude_none=True)
async def read_states(
        request: UserQueryRequest, 
        db: Session = Depends(get_db_session)):

    # Get all valid columns from the state model
    table_fields = models.State.get_valid_fields()    
  
    selected_fields = get_select_fields(request.fields, table_fields)

    filter_cond = get_filter_conditions(request.filters, table_fields)

    ordering = get_order_by_conditions(request.order_by, table_fields)

    # Calculate Limit and Offset based on Page Number
    limit = request.page_size
    skip = (request.page_no - 1) * request.page_size  # Offset calculation

    db_states = await service.get_states_by_params(db, selected_fields, filter_cond, ordering, skip=skip, limit=limit)
    return db_states

@router.put("/state/{state_id}", response_model=success_message_response)
async def update_state(state_id: str, state: schemas.StateUpdate, db: Session = Depends(get_db_session)):
    db_state = await service.get_state(db, state_id=state_id)
    if db_state is None:
        raise HTTPException(status_code=404, detail=STATE_DOES_NOT_EXIST_ERROR)
    return await service.update_state(db=db, state_id=state_id, state=state)

@router.delete("/state/{state_id}", response_model=success_message_response)
async def delete_state(state_id: str, db: Session = Depends(get_db_session)):
    db_state = await service.get_state(db, state_id=state_id)
    if db_state is None:
        raise HTTPException(status_code=404, detail=STATE_DOES_NOT_EXIST_ERROR)
    return await service.delete_state(db=db, state_id=state_id)