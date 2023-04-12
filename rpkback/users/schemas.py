from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class RegisterUser(BaseModel):
    username: str
    email: EmailStr
    password: str


class User(BaseModel):
    id: UUID
    username: str
    registered_at: datetime

    class Config:
        orm_mode = True


class MyProfile(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    registered_at: datetime

    class Config:
        orm_mode = True


class ChangeProfile(BaseModel):
    password: str
    new_password: str | None
    username: str | None
    email: EmailStr | None


class JWTToken(BaseModel):
    access_token: str
    token_type: str
