from sqlalchemy.orm import Session
import re
from . import models, schemas
from fastapi import HTTPException
from resources.strings import ORG_DOES_NOT_EXIST_ERROR, ORG_DELETE_SUCCESSFUL, ORG_CREATE_SUCCESSFUL, ORG_UPDATE_SUCCESSFUL


def get_organization(db: Session, org_id: str):
    return db.query(models.Organization).filter(models.Organization.organization_id == org_id).first()

def get_organizations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Organization).offset(skip).limit(limit).all()

def get_organizations_by_params(db: Session, selected_fields: list, filters:list, ordering:list, skip: int = 0, limit: int = 100):
    orm_attributes = [getattr(models.Organization, field) for field in selected_fields]
    return db.query(models.Organization).with_entities(*orm_attributes).filter(*filters).order_by(*ordering).offset(skip).limit(limit).all()

def create_organization(db: Session, organization: schemas.OrganizationBase):
    try:
        db_organization = models.Organization(**organization.model_dump())
        db.add(db_organization)
        db.commit()
        db.refresh(db_organization)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return db_organization

def update_organization(db: Session, org_id: str, organization: schemas.OrganizationUpdate):
    try:
        db_organization = db.query(models.Organization).filter(models.Organization.organization_id == org_id).first()
        if not db_organization:
            raise HTTPException(status_code=404, detail=ORG_DOES_NOT_EXIST_ERROR)        
        for key, value in organization.model_dump(exclude_none=True).items():
            setattr(db_organization, key, value)
        db.commit()
        db.refresh(db_organization)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": ORG_UPDATE_SUCCESSFUL}

def delete_organization(db: Session, org_id: str):
    try:
        db_organization = db.query(models.Organization).filter(models.Organization.organization_id == org_id).first()
        if not db_organization:
            raise HTTPException(status_code=404, detail=ORG_DOES_NOT_EXIST_ERROR)
        db.delete(db_organization)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": ORG_DELETE_SUCCESSFUL}

def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)

    if match:
        detail_text = match.group(1)
        return detail_text
    else:
        return "Error occurred while processing the request"

