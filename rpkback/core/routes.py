from fastapi import APIRouter


core = APIRouter(tags=['core'])


@core.get('/health')
async def check_health():
    return {'status': 'i am alive'}
