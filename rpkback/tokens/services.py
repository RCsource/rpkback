from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security.api_key import APIKeyHeader

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_403_FORBIDDEN

from rpkback.database import get_db
from rpkback.exceptions import ItemNotFound, Forbidden, ItemAlreadyExists
from rpkback.packages.services import get_package
from rpkback.tokens.models import APIToken
from rpkback.users.models import User
from rpkback.users.services import get_current_user


async def create_token(
    session: AsyncSession, user_id: UUID, name: str, package: str
) -> APIToken:
    package = await get_package(session, package)
    if package.author_id != user_id:
        raise Forbidden("You are not owner of this package")
    token = APIToken(user_id=user_id, package_name=package.name, name=name)
    session.add(token)
    try:
        await session.commit()
    except IntegrityError:
        raise ItemAlreadyExists("Token with this name already exists")
    await session.refresh(token)
    return token


async def get_token(session: AsyncSession, token_id: UUID, by_user: User) -> APIToken:
    token = await session.get(APIToken, token_id)
    if token is None:
        raise ItemNotFound("Token not found")
    if token.user_id != by_user.id:
        raise Forbidden("You are not the owner of this token")
    return token  # noqa


async def find_token_by_value(session: AsyncSession, value: str) -> APIToken:
    result = await session.execute(select(APIToken).where(APIToken.token == value))
    token = result.scalar_one_or_none()
    if token is None:
        raise ItemNotFound("Token with this value is not exists")
    return token


async def get_users_tokens(session: AsyncSession, user: User) -> list[APIToken]:
    result = await session.execute(select(APIToken).where(APIToken.user_id == user.id))
    return result.scalars().all()  # noqa


async def delete_token(session: AsyncSession, token_id: UUID, by_user: User):
    token = await get_token(session, token_id, by_user)
    await session.delete(token)
    await session.commit()


header = APIKeyHeader(name="Authorization")


async def get_current_token_or_user(
    token: str = Depends(header), session: AsyncSession = Depends(get_db)
) -> User | APIToken:
    try:
        schema, value = token.split()
    except ValueError:
        raise HTTPException(401, "Wrong token format. use 'Bearer <token>' or 'apiKey <token>'")
    if schema.lower() == "bearer":
        return await get_current_user(session, token)
    elif schema.lower() == "apikey":
        return await find_token_by_value(session, value)
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid authentication credentials",
        )
