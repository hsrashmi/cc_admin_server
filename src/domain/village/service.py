from sqlalchemy.orm import Session
import re
from . import models, schemas
from fastapi import HTTPException
from resources.strings import VILLAGE_CREATE_SUCCESSFUL, VILLAGE_DELETE_SUCCESSFUL, VILLAGE_UPDATE_SUCCESSFUL, VILLAGE_DOES_NOT_EXIST_ERROR


def get_village(db: Session, org_id: str):
    return db.query(models.Village).filter(models.Village.id == org_id).first()

def get_villages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Village).offset(skip).limit(limit).all()

def get_villages_by_params(db: Session, selected_fields: list, filters:list, ordering:list, skip: int = 0, limit: int = 100):
    orm_attributes = [getattr(models.Village, field) for field in selected_fields]
    return db.query(models.Village).with_entities(*orm_attributes).filter(*filters).order_by(*ordering).offset(skip).limit(limit).all()

def create_village(db: Session, village: schemas.VillageBase):
    try:
        db_village = models.Village(**village.model_dump())
        db.add(db_village)
        db.commit()
        db.refresh(db_village)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return db_village

def update_village(db: Session, org_id: str, village: schemas.VillageUpdate):
    try:
        db_village = db.query(models.Village).filter(models.Village.id == org_id).first()
        if not db_village:
            raise HTTPException(status_code=404, detail=VILLAGE_DOES_NOT_EXIST_ERROR)        
        for key, value in village.model_dump(exclude_none=True).items():
            setattr(db_village, key, value)
        db.commit()
        db.refresh(db_village)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": VILLAGE_UPDATE_SUCCESSFUL}

def delete_village(db: Session, org_id: str):
    try:
        db_village = db.query(models.Village).filter(models.Village.id == org_id).first()
        if not db_village:
            raise HTTPException(status_code=404, detail=VILLAGE_DOES_NOT_EXIST_ERROR)
        db.delete(db_village)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": VILLAGE_DELETE_SUCCESSFUL}

def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)

    if match:
        detail_text = match.group(1)
        return detail_text
    else:
        return "Error occurred while processing the request"

