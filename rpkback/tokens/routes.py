from uuid import UUID

from fastapi import APIRouter, Depends

from . import schemas, services
from ..database import get_db
from ..schemas import DetailSchema
from ..users.services import get_current_user


tokens = APIRouter(prefix="/tokens", tags=["tokens"])


@tokens.get("/")
async def get_my_tokens(
    user=Depends(get_current_user), db=Depends(get_db)
) -> list[schemas.APIToken]:
    return await services.get_users_tokens(db, user)


@tokens.post("/")
async def create_token(
    data: schemas.CreateAPIToken, db=Depends(get_db), user=Depends(get_current_user)
) -> schemas.APITokenSecret:
    return await services.create_token(db, user.id, data.name, data.package)


@tokens.delete("/{token_id}")
async def delete_token(
    token_id: UUID, db=Depends(get_db), user=Depends(get_current_user)
) -> DetailSchema:
    await services.delete_token(db, token_id, user)
    return DetailSchema(detail="token has been successfully deleted")


@tokens.get("/{token_id}")
async def get_token(
    token_id: UUID, db=Depends(get_db), user=Depends(get_current_user)
) -> schemas.APIToken:
    return await services.get_token(db, token_id, user)
