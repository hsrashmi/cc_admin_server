from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
import re
from . import models, schemas
from resources.strings import (
    ORG_DOES_NOT_EXIST_ERROR, ORG_DELETE_SUCCESSFUL,
    ORG_CREATE_SUCCESSFUL, ORG_UPDATE_SUCCESSFUL
)


async def get_organization(db: AsyncSession, org_id: str):
    result = await db.execute(select(models.Organization).filter(models.Organization.id == org_id))
    return result.scalar()


async def get_organizations(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Organization).offset(skip).limit(limit))
    return result.scalars().all()


async def get_organizations_by_params(db: AsyncSession, selected_fields: list, filters: list, ordering: list, skip: int = 0, limit: int = 100):
    orm_attributes = [getattr(models.Organization, field) for field in selected_fields]
    result = await db.execute(
        select(*orm_attributes).filter(*filters).order_by(*ordering).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def create_organization(db: AsyncSession, organization: schemas.OrganizationBase):
    try:
        db_organization = models.Organization(**organization.model_dump())
        db.add(db_organization)
        await db.commit()
        await db.refresh(db_organization)
    except Exception as e:
        print("Error creating db entry for organization -", str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return db_organization


async def update_organization(db: AsyncSession, org_id: str, organization: schemas.OrganizationUpdate):
    try:
        result = await db.execute(select(models.Organization).filter(models.Organization.id == org_id))
        db_organization = result.scalar()

        if not db_organization:
            raise HTTPException(status_code=404, detail=ORG_DOES_NOT_EXIST_ERROR)

        for key, value in organization.model_dump(exclude_none=True).items():
            setattr(db_organization, key, value)

        await db.commit()
        await db.refresh(db_organization)
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return {"message": ORG_UPDATE_SUCCESSFUL}


async def delete_organization(db: AsyncSession, org_id: str):
    try:
        result = await db.execute(select(models.Organization).filter(models.Organization.id == org_id))
        db_organization = result.scalar()

        if not db_organization:
            raise HTTPException(status_code=404, detail=ORG_DOES_NOT_EXIST_ERROR)

        await db.delete(db_organization)
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))

    return {"message": ORG_DELETE_SUCCESSFUL}


def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)
    return match.group(1) if match else "Error occurred while processing the request"
