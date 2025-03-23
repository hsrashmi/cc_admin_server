from fastapi import APIRouter

from . import ilpusers, auth, organization, school, state, zone, district, block
from ..config import ROUTE_PREFIX_V1

router = APIRouter()


def include_api_routes():
    ''' Include to router all api rest routes with version prefix '''
    router.include_router(auth.router)
    router.include_router(ilpusers.router, prefix=ROUTE_PREFIX_V1)
    router.include_router(organization.router, prefix=ROUTE_PREFIX_V1)
    router.include_router(school.router, prefix=ROUTE_PREFIX_V1)
    router.include_router(state.router, prefix=ROUTE_PREFIX_V1)
    router.include_router(zone.router, prefix=ROUTE_PREFIX_V1)
    router.include_router(district.router, prefix=ROUTE_PREFIX_V1)
    router.include_router(block.router, prefix=ROUTE_PREFIX_V1)

include_api_routes()
