from sqlalchemy.orm import Session
import re
from . import models, schemas
from fastapi import HTTPException
from resources.strings import ZONE_CREATE_SUCCESSFUL, ZONE_UPDATE_SUCCESSFUL, ZONE_DOES_NOT_EXIST_ERROR, ZONE_DELETE_SUCCESSFUL 


def get_zone(db: Session, zone_id: str):
    return db.query(models.Zone).filter(models.Zone.id == zone_id).first()

def get_zones(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Zone).offset(skip).limit(limit).all()

def get_zones_by_params(db: Session, selected_fields: list, filters:list, ordering:list, skip: int = 0, limit: int = 100):
    orm_attributes = [getattr(models.Zone, field) for field in selected_fields]
    return db.query(models.Zone).with_entities(*orm_attributes).filter(*filters).order_by(*ordering).offset(skip).limit(limit).all()

def create_zone(db: Session, zone: schemas.ZoneBase):
    try:
        db_zone = models.Zone(**zone.model_dump())
        db.add(db_zone)
        db.commit()
        db.refresh(db_zone)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return db_zone

def update_zone(db: Session, zone_id: str, zone: schemas.ZoneUpdate):
    try:
        db_zone = db.query(models.Zone).filter(models.Zone.id == zone_id).first()
        if not db_zone:
            raise HTTPException(status_code=404, detail=ZONE_DOES_NOT_EXIST_ERROR)        
        for key, value in zone.model_dump(exclude_none=True).items():
            setattr(db_zone, key, value)
        db.commit()
        db.refresh(db_zone)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": ZONE_UPDATE_SUCCESSFUL}

def delete_zone(db: Session, zone_id: str):
    try:
        db_zone = db.query(models.Zone).filter(models.Zone.id == zone_id).first()
        if not db_zone:
            raise HTTPException(status_code=404, detail=ZONE_DOES_NOT_EXIST_ERROR)
        db.delete(db_zone)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": ZONE_DELETE_SUCCESSFUL}

def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)

    if match:
        detail_text = match.group(1)
        return detail_text
    else:
        return "Error occurred while processing the request"

