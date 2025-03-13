from sqlalchemy.orm import Session
import re
from . import models, schemas
from fastapi import HTTPException
from resources.strings import ASSET_CREATE_SUCCESSFUL, ASSET_DELETE_SUCCESSFUL, ASSET_DOES_NOT_EXIST_ERROR, ASSET_UPDATE_SUCCESSFUL  


def get_asset(db: Session, asset_id: str):
    return db.query(models.Asset).filter(models.Asset.id == asset_id).first()

def get_assets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Asset).offset(skip).limit(limit).all()

def get_assets_by_params(db: Session, selected_fields: list, filters:list, ordering:list, skip: int = 0, limit: int = 100):
    orm_attributes = [getattr(models.Asset, field) for field in selected_fields]
    return db.query(models.Asset).with_entities(*orm_attributes).filter(*filters).order_by(*ordering).offset(skip).limit(limit).all()

def create_asset(db: Session, asset: schemas.AssetBase):
    try:
        db_asset = models.Asset(**asset.model_dump())
        db.add(db_asset)
        db.commit()
        db.refresh(db_asset)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return db_asset

def update_asset(db: Session, asset_id: str, asset: schemas.AssetUpdate):
    try:
        db_asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
        if not db_asset:
            raise HTTPException(status_code=404, detail=ASSET_DOES_NOT_EXIST_ERROR)        
        for key, value in asset.model_dump(exclude_none=True).items():
            setattr(db_asset, key, value)
        db.commit()
        db.refresh(db_asset)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": ASSET_UPDATE_SUCCESSFUL}

def delete_asset(db: Session, asset_id: str):
    try:
        db_asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
        if not db_asset:
            raise HTTPException(status_code=404, detail=ASSET_DOES_NOT_EXIST_ERROR)
        db.delete(db_asset)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": ASSET_DELETE_SUCCESSFUL}

def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)

    if match:
        detail_text = match.group(1)
        return detail_text
    else:
        return "Error occurred while processing the request"

