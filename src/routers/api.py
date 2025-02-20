from fastapi import APIRouter

from . import ilpusers, auth, organization
from ..config import ROUTE_PREFIX_V1

router = APIRouter()


def include_api_routes():
    ''' Include to router all api rest routes with version prefix '''
    router.include_router(auth.router)
    router.include_router(ilpusers.router, prefix=ROUTE_PREFIX_V1)
    router.include_router(organization.router, prefix=ROUTE_PREFIX_V1)

include_api_routes()
