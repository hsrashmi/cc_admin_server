from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import jwt

from src.dependencies import get_db_session
from src.domain.ilpuser import service, schemas

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    data["hashed_password"] = ""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


router = APIRouter(tags=["auth"])


@router.post("/login/", response_model=dict)
async def create_user(user: schemas.ILPUser, db: Session = Depends(get_db_session)):
    db_user = await service.get_user_by_email(db, email=user.email)
    if db_user and user.password == db_user.hashed_password:
        raise HTTPException(status_code=400, detail="Email already registered")
    return {"Authorization": "Bearer " + create_access_token(user.dict())}
