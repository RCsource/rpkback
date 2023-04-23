from fastapi import APIRouter
from fastapi.responses import JSONResponse

from . import schemas, services


core = APIRouter(tags=['core'])


@core.get('/health', response_model=schemas.HealthStatusSchema)
async def check_health():
    status, code = ("i am alive", 200) if await services.check_database_connection() else ("i am dead", 500)
    return JSONResponse(
        content={'status': status},
        status_code=code
    )
