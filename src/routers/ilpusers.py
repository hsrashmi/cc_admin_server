from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .converter import ilpuser_converter
from ..dependencies import get_db
from ..domain.ilpuser import service, schemas, models
from .util_functions import UserQueryRequest, LoginQueryRequest, generate_uuid, string_hash, success_message_response, get_order_by_conditions, get_filter_conditions, get_select_fields
from resources.strings import ROLE_DOES_NOT_EXIST_ERROR, EMAIL_ALREADY_EXISTS_ERROR, AUTHENTICATION_FAILED_ERROR

router = APIRouter(tags=["ilpuser"])

@router.post("/login/", response_model=schemas.ILPUserResponse)
def login_user(request: LoginQueryRequest,db: Session = Depends(get_db)):
    print(request.email, request.password)
    db_user = service.get_user_by_email(db, email=request.email)
    if not db_user:
        raise HTTPException(status_code=401, detail=AUTHENTICATION_FAILED_ERROR)
    return service.login_user(db=db, email=request.email, password=request.password)


@router.post("/ilpuser/", response_model=schemas.ILPUserResponse)
def create_user(user: schemas.ILPUserBase, db: Session = Depends(get_db)):
    db_user = service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail=EMAIL_ALREADY_EXISTS_ERROR)
    unique_id = str(generate_uuid())
    hashed_password = string_hash(user.password)    
    updated_user = user.model_copy(update={"user_id": unique_id, "password": hashed_password})   
    return service.create_user(db=db, user=updated_user)

@router.get("/ilpuser/", response_model=List[schemas.ILPUserResponse])
def read_users(page_no: int = 1, page_size: int = 100, db: Session = Depends(get_db)):
    limit = page_size
    skip = (page_no - 1) * page_size  # Offset calculation
    users = service.get_users(db, skip=skip, limit=limit)
    return ilpuser_converter.convert_many(users)

@router.get("/ilpuser/{user_id}", response_model=schemas.ILPUserResponse)
def read_user(user_id: str, db: Session = Depends(get_db)):
    db_user = service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail=ROLE_DOES_NOT_EXIST_ERROR)
    return ilpuser_converter.convert(db_user)   

@router.post("/getIlpusersByParams/", response_model=list, response_model_exclude_none=True)
def read_users(
        request: UserQueryRequest, 
        db: Session = Depends(get_db)):

    # Get all valid columns from the User model
    table_fields = models.ILPUser.get_valid_fields()    
  
    selected_fields = get_select_fields(request.fields, table_fields)

    filter_cond = get_filter_conditions(request.filters, table_fields)

    ordering = get_order_by_conditions(request.order_by, table_fields)

    # Calculate Limit and Offset based on Page Number
    limit = request.page_size
    skip = (request.page_no - 1) * request.page_size  # Offset calculation

    db_users = service.get_users_by_params(db, selected_fields, filter_cond, ordering, skip=skip, limit=limit)
    return [dict(zip(selected_fields, user)) for user in db_users]

@router.put("/ilpuser/{user_id}", response_model=success_message_response)
def update_user(user_id: str, user: schemas.ILPUserUpdate, db: Session = Depends(get_db)):
    db_user = service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail=ROLE_DOES_NOT_EXIST_ERROR)
    return service.update_user(db=db, user_id=user_id, user=user)

@router.delete("/ilpuser/{user_id}", response_model=success_message_response)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    db_user = service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail=ROLE_DOES_NOT_EXIST_ERROR)
    return service.delete_user(db=db, user_id=user_id)