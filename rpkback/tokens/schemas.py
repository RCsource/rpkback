from datetime import datetime
from uuid import UUID

from ..schemas import BaseModel


class CreateAPIToken(BaseModel):
    name: str
    package: str


class APIToken(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    package_name: str
    created_at: datetime
    last_usage_at: datetime | None

    class Config:
        orm_mode = True


class APITokenSecret(APIToken):
    token: str
