from datetime import datetime, timedelta
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from rpkback.config import ALGORITHM, SECRET_KEY
from rpkback.database import get_db
from rpkback.exceptions import ItemNotFound, ItemAlreadyExists, Forbidden
from rpkback.users.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def create_user(
    session: AsyncSession, username: str, email: str, password: str
) -> User:
    user = User(username=username, email=email, hashed_password=hash_password(password))
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        raise ItemAlreadyExists("user already exists")
    await session.refresh(user)
    return user


async def remove_user(session: AsyncSession, user: User):
    if user.is_removed:
        raise ItemNotFound("user already deleted")
    user.is_removed = True
    await session.commit()
    await session.refresh(user)


async def change_user_info(
    session: AsyncSession,
    user: User,
    *,
    password: str,
    username: str | None = None,
    email: str | None = None,
    new_password: str | None = None,
):
    if not verify_password(password, user.hashed_password):
        raise Forbidden("wrong password")
    if user is not None:
        user.username = username
    if email is not None:
        user.email = email
    if new_password is not None:
        user.hashed_password = hash_password(new_password)
    await session.commit()
    await session.refresh(user)


async def get_user_by_name(session: AsyncSession, username: str) -> User:
    resp = await session.execute(select(User).where(User.username == username).limit(1))
    user = resp.scalar_one_or_none()
    if user is None:
        raise ItemNotFound("user not found")
    return user


async def get_user_by_id(session: AsyncSession, id_: UUID) -> User:
    user = await session.get(User, id_)
    if user is None:
        raise ItemNotFound("user not found")
    return user  # noqa


async def authenticate_user(session: AsyncSession, username: str, password: str):
    user = await get_user_by_name(session, username)
    if not verify_password(password, user.hashed_password):
        return None
    if user.is_removed:
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    session: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        _id: str = payload.get("sub")
        if _id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user_by_id(session, id_=UUID(_id))
    if user is None:
        raise credentials_exception
    return user
