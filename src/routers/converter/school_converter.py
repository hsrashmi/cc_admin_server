from typing import List

from ...domain.school import schemas, models


def convert(db_school: models.School):
    ''' Customized convertion to response template '''
    return schemas.SchoolResponse(
        school_id=db_school.id,
        name=db_school.name,
        long_name=db_school.long_name,
        dise_code=db_school.dise_code,
        address=db_school.address,
        city=db_school.city,
        state=db_school.state,
        pincode=db_school.pincode, 
        organization_id=db_school.organization_id,
        created_at=db_school.created_at,
        created_by=db_school.created_by,
        last_updated_at=db_school.last_updated_at,
        last_updated_by=db_school.last_updated_by 
    )


def convert_many(db_schools: List):
    ''' Convert list customized '''
    return [convert(db_school) for db_school in db_schools]
