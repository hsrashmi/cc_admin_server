from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException
from resources.strings import USER_DOES_NOT_EXIST_ERROR, USER_DELETE_SUCCESSFUL, USER_UPDATE_SUCCESSFUL, AUTHENTICATION_FAILED_ERROR
import bcrypt
import re

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def login_user(db: Session, email: str, password: str):
    user = db.query(models.ILPUser).filter(models.ILPUser.email == email).first()
    is_pwd_same = verify_password(password, user.password)
    print("is pwd match ", is_pwd_same)
    if not user or not is_pwd_same:
        raise HTTPException(status_code=401, detail=AUTHENTICATION_FAILED_ERROR)
    return user
        

def get_user(db: Session, user_id: str):
    return db.query(models.ILPUser).filter(models.ILPUser.user_id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.ILPUser).filter(models.ILPUser.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ILPUser).offset(skip).limit(limit).all()

def get_users_by_params(db: Session, selected_fields: list, filters:list, ordering:list, skip: int = 0, limit: int = 100):
    orm_attributes = [getattr(models.ILPUser, field) for field in selected_fields]
    return db.query(models.ILPUser).with_entities(*orm_attributes).filter(*filters).order_by(*ordering).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.ILPUserBase):
    try:
        db_user = models.ILPUser(**user.model_dump())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        print("Error creating db entry for user - ", str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return db_user

def update_user(db: Session, user_id: str, user: schemas.ILPUserUpdate):
    try:
        db_user = db.query(models.ILPUser).filter(models.ILPUser.user_id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail=USER_DOES_NOT_EXIST_ERROR)
        for key, value in user.model_dump(exclude_none=True).items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": USER_UPDATE_SUCCESSFUL}
    
def delete_user(db: Session, user_id: str):
    try:
        db_user = db.query(models.ILPUser).filter(models.ILPUser.user_id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail=USER_DOES_NOT_EXIST_ERROR)
        db.delete(db_user)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": USER_DELETE_SUCCESSFUL}


def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)

    if match:
        detail_text = match.group(1)
        return detail_text
    else:
        return "Error occurred while processing the request"

