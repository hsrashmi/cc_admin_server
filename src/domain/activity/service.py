from sqlalchemy.orm import Session
import re
from . import models, schemas
from fastapi import HTTPException
from resources.strings import ACTIVITY_CREATE_SUCCESSFUL, ACTIVITY_DELETE_SUCCESSFUL, ACTIVITY_UPDATE_SUCCESSFUL, ACTIVITY_DOES_NOT_EXIST_ERROR


def get_activity(db: Session, activity_id: str):
    return db.query(models.Activity).filter(models.Activity.id == activity_id).first()

def get_activities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Activity).offset(skip).limit(limit).all()

def get_activities_by_params(db: Session, selected_fields: list, filters:list, ordering:list, skip: int = 0, limit: int = 100):
    orm_attributes = [getattr(models.Activity, field) for field in selected_fields]
    return db.query(models.Activity).with_entities(*orm_attributes).filter(*filters).order_by(*ordering).offset(skip).limit(limit).all()

def create_activity(db: Session, activity: schemas.ActivityBase):
    try:
        db_activity = models.Activity(**activity.model_dump())
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return db_activity

def update_activity(db: Session, activity_id: str, activity: schemas.ActivityUpdate):
    try:
        db_activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
        if not db_activity:
            raise HTTPException(status_code=404, detail=ACTIVITY_DOES_NOT_EXIST_ERROR)        
        for key, value in activity.model_dump(exclude_none=True).items():
            setattr(db_activity, key, value)
        db.commit()
        db.refresh(db_activity)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": ACTIVITY_UPDATE_SUCCESSFUL}

def delete_activity(db: Session, activity_id: str):
    try:
        db_activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
        if not db_activity:
            raise HTTPException(status_code=404, detail=ACTIVITY_DOES_NOT_EXIST_ERROR)
        db.delete(db_activity)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": ACTIVITY_DELETE_SUCCESSFUL}

def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)

    if match:
        detail_text = match.group(1)
        return detail_text
    else:
        return "Error occurred while processing the request"

