from sqlalchemy.orm import Session
import re
from . import models, schemas
from fastapi import HTTPException
from resources.strings import BLOCK_CREATE_SUCCESSFUL, BLOCK_UPDATE_SUCCESSFUL, BLOCK_DELETE_SUCCESSFUL, BLOCK_DOES_NOT_EXIST_ERROR 


def get_block(db: Session, block_id: str):
    return db.query(models.Block).filter(models.Block.id == block_id).first()

def get_blocks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Block).offset(skip).limit(limit).all()

def get_blocks_by_params(db: Session, selected_fields: list, filters:list, ordering:list, skip: int = 0, limit: int = 100):
    orm_attributes = [getattr(models.Block, field) for field in selected_fields]
    return db.query(models.Block).with_entities(*orm_attributes).filter(*filters).order_by(*ordering).offset(skip).limit(limit).all()

def create_block(db: Session, block: schemas.BlockBase):
    try:
        db_block = models.Block(**block.model_dump())
        db.add(db_block)
        db.commit()
        db.refresh(db_block)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return db_block

def update_block(db: Session, block_id: str, block: schemas.BlockUpdate):
    try:
        db_block = db.query(models.Block).filter(models.Block.id == block_id).first()
        if not db_block:
            raise HTTPException(status_code=404, detail=BLOCK_DOES_NOT_EXIST_ERROR)        
        for key, value in block.model_dump(exclude_none=True).items():
            setattr(db_block, key, value)
        db.commit()
        db.refresh(db_block)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": BLOCK_UPDATE_SUCCESSFUL}

def delete_block(db: Session, block_id: str):
    try:
        db_block = db.query(models.Block).filter(models.Block.id == block_id).first()
        if not db_block:
            raise HTTPException(status_code=404, detail=BLOCK_DOES_NOT_EXIST_ERROR)
        db.delete(db_block)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": BLOCK_DELETE_SUCCESSFUL}

def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)

    if match:
        detail_text = match.group(1)
        return detail_text
    else:
        return "Error occurred while processing the request"

