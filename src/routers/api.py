from fastapi import APIRouter

from . import ilpuser, auth, organization, school, state, teacher, zone, district, block, school_class, role, common, activity
from ..config import ROUTE_PREFIX_V1

router = APIRouter()


def include_api_routes():
    ''' Include to router all api rest routes with version prefix '''
    router.include_router(auth.router)
    router.include_router(ilpuser.router, prefix=ROUTE_PREFIX_V1)
    router.include_router(organization.router, prefix=ROUTE_PREFIX_V1)
    router.include_router(school.router, prefix=ROUTE_PREFIX_V1)
    router.include_router(school_class.router, prefix=ROUTE_PREFIX_V1)
    router.include_router(teacher.router, prefix=ROUTE_PREFIX_V1)
    router.include_router(state.router, prefix=ROUTE_PREFIX_V1)
    router.include_router(zone.router, prefix=ROUTE_PREFIX_V1)
    router.include_router(district.router, prefix=ROUTE_PREFIX_V1)
    router.include_router(block.router, prefix=ROUTE_PREFIX_V1)
    router.include_router(role.router, prefix=ROUTE_PREFIX_V1)
    router.include_router(activity.router, prefix=ROUTE_PREFIX_V1)
    router.include_router(common.router, prefix=ROUTE_PREFIX_V1)

include_api_routes()
