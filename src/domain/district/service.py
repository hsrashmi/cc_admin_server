from sqlalchemy.orm import Session
import re
from . import models, schemas
from fastapi import HTTPException
from resources.strings import DISTRICT_CREATE_SUCCESSFUL, DISTRICT_UPDATE_SUCCESSFUL, DISTRICT_DELETE_SUCCESSFUL, DISTRICT_DOES_NOT_EXIST_ERROR


def get_district(db: Session, dist_id: str):
    return db.query(models.District).filter(models.District.id == dist_id).first()

def get_districts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.District).offset(skip).limit(limit).all()

def get_districts_by_params(db: Session, selected_fields: list, filters:list, ordering:list, skip: int = 0, limit: int = 100):
    orm_attributes = [getattr(models.District, field) for field in selected_fields]
    return db.query(models.District).with_entities(*orm_attributes).filter(*filters).order_by(*ordering).offset(skip).limit(limit).all()

def create_district(db: Session, district: schemas.DistrictBase):
    try:
        db_district = models.District(**district.model_dump())
        db.add(db_district)
        db.commit()
        db.refresh(db_district)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return db_district

def update_district(db: Session, dist_id: str, district: schemas.DistrictUpdate):
    try:
        db_district = db.query(models.District).filter(models.District.id == dist_id).first()
        if not db_district:
            raise HTTPException(status_code=404, detail=DISTRICT_DOES_NOT_EXIST_ERROR)        
        for key, value in district.model_dump(exclude_none=True).items():
            setattr(db_district, key, value)
        db.commit()
        db.refresh(db_district)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": DISTRICT_UPDATE_SUCCESSFUL}

def delete_district(db: Session, dist_id: str):
    try:
        db_district = db.query(models.District).filter(models.District.id == dist_id).first()
        if not db_district:
            raise HTTPException(status_code=404, detail=DISTRICT_DOES_NOT_EXIST_ERROR)
        db.delete(db_district)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": DISTRICT_DELETE_SUCCESSFUL}

def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)

    if match:
        detail_text = match.group(1)
        return detail_text
    else:
        return "Error occurred while processing the request"

