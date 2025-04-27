from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..dependencies import get_db_session
from ..domain.role import service, schemas, models
from ..domain.role_assignment import service as userRoleService, schemas as userRoleSchemas, models as userRoleModels
from ..domain.role_assignment.models import LevelEnum
from .util_functions import UserQueryRequest, LoginQueryRequest, generate_uuid, string_hash, success_message_response, get_order_by_conditions, get_filter_conditions, get_select_fields
from resources.strings import ROLE_DOES_NOT_EXIST_ERROR, USER_ROLE_ASSOCIATION_DOES_NOT_EXIST_ERROR, USER_ROLE_ASSOCIATION_DOES_NOT_EXIST_ERROR

router = APIRouter(tags=["role"])

@router.get("/role/", response_model=list[schemas.RoleResponse])
async def get_roles(page_no: int = 1, page_size: int = 100, db: Session = Depends(get_db_session)):
    limit = page_size
    skip = (page_no - 1) * page_size
    return await service.get_roles(db, skip=skip, limit=limit)  

@router.post("/role/", response_model=schemas.RoleBase)
async def create_role(role: schemas.RoleBase, db: Session = Depends(get_db_session)):
    unique_id = str(generate_uuid())
    updated_role = role.model_copy(update={"id": unique_id})   
    return await service.create_role(db=db, role=updated_role)

@router.get("/role/{role_id}", response_model=schemas.RoleResponse)
async def read_role(role_id: str, db: Session = Depends(get_db_session)):
    db_role = await service.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail=ROLE_DOES_NOT_EXIST_ERROR)
    return db_role

@router.post("/getRolesByParams/", response_model=list[schemas.RoleResponse], response_model_exclude_none=True)
async def read_roles(
        request: UserQueryRequest, 
        db: Session = Depends(get_db_session)):

    # Get all valid columns from the User model
    table_fields = models.Role.get_valid_fields()    
  
    selected_fields = get_select_fields(request.fields, table_fields)

    filter_cond = get_filter_conditions(request.filters, table_fields)

    ordering = get_order_by_conditions(request.order_by, table_fields)

    # Calculate Limit and Offset based on Page Number
    limit = request.page_size
    skip = (request.page_no - 1) * request.page_size  # Offset calculation

    db_roles = await service.get_roles_by_params(db, selected_fields, filter_cond, ordering, skip=skip, limit=limit)
    return [dict(zip(selected_fields, role)) for role in db_roles]

@router.put("/role/{role_id}", response_model=success_message_response)
async def update_role(role_id: str, role: schemas.RoleUpdate, db: Session = Depends(get_db_session)):
    db_role = await service.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail=ROLE_DOES_NOT_EXIST_ERROR)
    return await service.update_role(db=db, role_id=role_id, role=role)

@router.delete("/role/{role_id}", response_model=success_message_response)
async def delete_role(role_id: str, db: Session = Depends(get_db_session)):
    db_role = await service.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail=ROLE_DOES_NOT_EXIST_ERROR)
    return await service.delete_role(db=db, role_id=role_id)


@router.get("/userRole/{user_id}", response_model=list)
async def read_role(user_id: str, db: Session = Depends(get_db_session)):
    user_roles = await userRoleService.get_user_roles_with_hierarchy(db, user_id)    
    if user_roles is None:
        raise HTTPException(status_code=404, detail=USER_ROLE_ASSOCIATION_DOES_NOT_EXIST_ERROR)
    return [userRoleService.serialize_user_role(ur) for ur in user_roles]

@router.post("/userRole/", response_model=userRoleSchemas.UserRoleResponse)
async def create_user_role(role: userRoleSchemas.UserRoleBase, db: Session = Depends(get_db_session)):
    unique_id = str(generate_uuid())
    updated_role = role.model_copy(update={"id": unique_id})   
    return await userRoleService.create_user_role(db=db, user_role=updated_role)

# @router.delete("/userRoleByLevelid/{level_id}", response_model=success_message_response)
# async def delete_role(level_id: str, db: Session = Depends(get_db_session)):
#     return await userRoleService.delete_user_role_by_levelid(db=db, level_id=level_id)

@router.delete("/userRoleByField/", response_model=success_message_response)
async def delete_role_by_field(
    field_name: str, 
    field_value: str, 
    db: Session = Depends(get_db_session)
):
    return await userRoleService.delete_user_role_by_field(
        db=db, field_name=field_name, field_value=field_value
    )

@router.post("/userRoleByField", response_model=list[userRoleSchemas.UserRoleResponseSchema])
async def get_user_role_by_fields(
    payload: userRoleSchemas.FilterRequest,
    db: Session = Depends(get_db_session)
):
    filters = {f.field_name: f.field_value for f in payload.fields}
    return await userRoleService.get_user_role_by_fields(db=db, filters=filters)

@router.get("/userRolesByHeirarchy/", response_model=list[userRoleSchemas.UserRoleResponseSchema])
async def get_user_role_by_fields(
     level_name: LevelEnum = Query(...), 
    level_id: str = Query(...), 
    db: Session = Depends(get_db_session)
):    
    return await userRoleService.get_user_role_by_heirarchy(db=db, region_level=level_name, region_id=level_id)


@router.delete("/userRole/{role_id}", response_model=success_message_response)
async def delete_role(role_id: str, db: Session = Depends(get_db_session)):
    db_role = await userRoleService.get_user_role(db, assignment_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail=USER_ROLE_ASSOCIATION_DOES_NOT_EXIST_ERROR)
    return await userRoleService.delete_user_role(db=db, assignment_id=role_id)
