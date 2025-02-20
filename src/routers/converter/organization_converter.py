from typing import List

from ...domain.organization import schemas, models


def convert(db_organization: models.Organization):
    ''' Customized convertion to response template '''
    return schemas.OrganizationResponse(
        organization_id=db_organization.organization_id,
        name=db_organization.name,
        long_name=db_organization.long_name,
        description=db_organization.description,
        placeholder1=db_organization.placeholder1,
        placeholder2=db_organization.placeholder2,
        placeholder3=db_organization.placeholder3,
        created_at=db_organization.created_at,
        created_by=db_organization.created_by,
        last_updated_at=db_organization.last_updated_at,
        last_updated_by=db_organization.last_updated_by 
    )


def convert_many(db_organizations: List):
    ''' Convert list customized '''
    return [convert(db_organization) for db_organization in db_organizations]
