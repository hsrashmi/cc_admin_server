from typing import List

from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

###
# Properties configurations
###

API_PREFIX = "/ilp"

JWT_TOKEN_PREFIX = "Authorization"

config = Config(".env")

ROUTE_PREFIX_V1 = "/v1"

ALLOWED_HOSTS: List[str] = config("ALLOWED_HOSTS")
