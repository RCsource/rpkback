from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from . import schemas, services
from .services import authenticate_user, create_access_token, get_current_user
from ..config import ACCESS_TOKEN_EXPIRE_MINUTES
from ..database import get_db
from ..schemas import DetailSchema


users = APIRouter(prefix="/users", tags=["users"])


@users.post("/")
async def register_user(data: schemas.RegisterUser, db=Depends(get_db)) -> schemas.User:
    """
    регистрация пользователя по username, email и паролю.
    системы подтвереждения по почте пока нет, но она обязательно появится
    """
    return await services.create_user(db, data.username, data.email, data.password)


@users.get("/me")
async def get_my_profile(user=Depends(get_current_user)) -> schemas.MyProfile:
    """получение данных текущего пользака из Authorization хедера"""
    return user


@users.put("/me")
async def change_my_profile(
    data: schemas.ChangeProfile, user=Depends(get_current_user), db=Depends(get_db)
) -> schemas.User:
    await services.change_user_info(db, user, **data.dict())
    return user


@users.delete("/me")
async def delete_my_profile(
    user=Depends(get_current_user), db=Depends(get_db)
) -> DetailSchema:
    """
    удаляет профиль с лица земли (нет).
    удалённый юзер остаётся в базе, но на него нельзя залогиниться и публиковать новые версии пакетов
    """
    await services.remove_user(db, user)
    return DetailSchema(detail="your profile has been successfully deleted")


@users.get("/{user_id}")
async def get_user_by_id(user_id: UUID, db=Depends(get_db)) -> schemas.User:
    """ну получаем юзера по айдихе, чего бубнить"""
    return await services.get_user_by_id(db, user_id)


@users.post("/login")
async def get_jwt_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)
) -> schemas.JWTToken:
    """получение jwt токена по юзернейму и паролю для взаимодействия с апишкой пользователя"""
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
