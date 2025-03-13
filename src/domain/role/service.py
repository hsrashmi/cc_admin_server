from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException
from resources.strings import ROLE_DOES_NOT_EXIST_ERROR, ROLE_DELETE_SUCCESSFUL, ROLE_UPDATE_SUCCESSFUL
import re

def get_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Role).offset(skip).limit(limit).all()

def create_role(db: Session, role: schemas.RoleBase):
    try:
        db_role = models.Role(**role.model_dump())
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
    except Exception as e:
        print("Error creating db entry for role - ", str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return db_role

def update_role(db: Session, role_id: str, role: schemas.RoleUpdate):
    try:
        db_role = db.query(models.Role).filter(models.Role.id == role_id).first()
        if not db_role:
            raise HTTPException(status_code=404, detail=ROLE_DOES_NOT_EXIST_ERROR)
        for key, value in role.model_dump(exclude_none=True).items():
            setattr(db_role, key, value)
        db.commit()
        db.refresh(db_role)
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": ROLE_UPDATE_SUCCESSFUL}
    
def delete_role(db: Session, role_id: str):
    try:
        db_role = db.query(models.Role).filter(models.Role.id == role_id).first()
        if not db_role:
            raise HTTPException(status_code=404, detail=ROLE_DOES_NOT_EXIST_ERROR)
        db.delete(db_role)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": ROLE_DELETE_SUCCESSFUL}

def get_users_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.UserRole).offset(skip).limit(limit).all()

def get_user_roles(db: Session, user_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.UserRole).filter(models.UserRole.user_id == user_id).first()

def create_user_role(db: Session, user_role: schemas.UserRoleBase):
    try:
        db_user_role = models.UserRole(**user_role.model_dump())
        db.add(db_user_role)
        db.commit()
        db.refresh(db_user_role)
    except Exception as e:
        print("Error creating db entry for role - ", str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return db_user_role

def update_user_role(db: Session, user_role_id: str, role: schemas.UserRoleUpdate):
    try:
        db_user_role = db.query(models.UserRole).filter(models.UserRole.id == user_role_id).first()
        if not db_user_role:
            raise HTTPException(status_code=404, detail=ROLE_DOES_NOT_EXIST_ERROR)
        for key, value in role.model_dump(exclude_none=True).items():
            setattr(db_user_role, key, value)
        db.commit()
        db.refresh(db_user_role)
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": ROLE_UPDATE_SUCCESSFUL}
    
def delete_user_role(db: Session, role_id: str):
    try:
        db_user_role = db.query(models.UserRole).filter(models.UserRole.id == role_id).first()
        if not db_user_role:
            raise HTTPException(status_code=404, detail=ROLE_DOES_NOT_EXIST_ERROR)
        db.delete(db_user_role)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": ROLE_DELETE_SUCCESSFUL}

def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)

    if match:
        detail_text = match.group(1)
        return detail_text
    else:
        return "Error occurred while processing the request"