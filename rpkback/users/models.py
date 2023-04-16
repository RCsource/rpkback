import datetime
from uuid import UUID

from sqlalchemy import func, text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    email: Mapped[str]
    registered_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    is_removed: Mapped[bool] = mapped_column(server_default="f")
