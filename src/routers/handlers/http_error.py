from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse


###
# Exception Handlers for filter exception error and personalize messages
###

async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    ''' Personalize response when HTTPException '''
    return JSONResponse({"errors": [exc.detail]}, status_code=exc.status_code)
