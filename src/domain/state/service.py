from sqlalchemy.orm import Session
import re
from . import models, schemas
from fastapi import HTTPException
from resources.strings import STATE_CREATE_SUCCESSFUL, STATE_DELETE_SUCCESSFUL, STATE_UPDATE_SUCCESSFUL, STATE_DOES_NOT_EXIST_ERROR


def get_state(db: Session, state_id: str):
    return db.query(models.State).filter(models.State.id == state_id).first()

def get_states(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.State).offset(skip).limit(limit).all()

def get_states_by_params(db: Session, selected_fields: list, filters:list, ordering:list, skip: int = 0, limit: int = 100):
    orm_attributes = [getattr(models.State, field) for field in selected_fields]
    return db.query(models.State).with_entities(*orm_attributes).filter(*filters).order_by(*ordering).offset(skip).limit(limit).all()

def create_state(db: Session, state: schemas.StateBase):
    try:
        db_state = models.State(**state.model_dump())
        db.add(db_state)
        db.commit()
        db.refresh(db_state)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return db_state

def update_state(db: Session, state_id: str, state: schemas.StateUpdate):
    try:
        db_state = db.query(models.State).filter(models.State.id == state_id).first()
        if not db_state:
            raise HTTPException(status_code=404, detail=STATE_DOES_NOT_EXIST_ERROR)        
        for key, value in state.model_dump(exclude_none=True).items():
            setattr(db_state, key, value)
        db.commit()
        db.refresh(db_state)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": STATE_UPDATE_SUCCESSFUL}

def delete_state(db: Session, state_id: str):
    try:
        db_state = db.query(models.State).filter(models.State.id == state_id).first()
        if not db_state:
            raise HTTPException(status_code=404, detail=STATE_DOES_NOT_EXIST_ERROR)
        db.delete(db_state)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": STATE_CREATE_SUCCESSFUL}

def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)

    if match:
        detail_text = match.group(1)
        return detail_text
    else:
        return "Error occurred while processing the request"

