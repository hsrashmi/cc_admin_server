from typing import List

from ...domain.ilpuser import schemas, models


def convert(db_ilpuser: models.ILPUser):
    ''' Customized convertion to response template '''
    return schemas.ILPUserResponse(
        user_id=db_ilpuser.user_id,
        is_active=db_ilpuser.is_active, 
        username=db_ilpuser.username,
        email=db_ilpuser.email,
        first_name=db_ilpuser.first_name,
        last_name=db_ilpuser.last_name,
        phone1=db_ilpuser.phone1,
        phone2=db_ilpuser.phone2,
        profile_pic_url=db_ilpuser.profile_pic_url,
        address=db_ilpuser.address,
        city=db_ilpuser.city,
        state=db_ilpuser.state,
        country=db_ilpuser.country,
        gender=db_ilpuser.gender,   
        created_at=db_ilpuser.created_at,
        created_by=db_ilpuser.created_by,
        last_updated_at=db_ilpuser.last_updated_at,
        last_updated_by=db_ilpuser.last_updated_by  
    )


def convert_many(db_ilpusers: List):
    ''' Convert list customized '''
    return [convert(db_ilpuser) for db_ilpuser in db_ilpusers]
