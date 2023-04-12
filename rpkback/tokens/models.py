from datetime import datetime
from uuid import UUID

from sqlalchemy import text, ForeignKey, UniqueConstraint, func

from ..database import Base
from sqlalchemy.orm import mapped_column, Mapped


class APIToken(Base):
    __tablename__ = "api_tokens"
    __table_args__ = (UniqueConstraint("user_id", "name", name="_api_token_uc"),)

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    token: Mapped[str] = mapped_column(
        server_default=text("md5(random()::text)"), unique=True
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str]
    package_name: Mapped[str] = mapped_column(ForeignKey("packages.name"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    last_usage_at: Mapped[datetime] = mapped_column(nullable=True)
