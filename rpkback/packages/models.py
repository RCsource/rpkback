from datetime import datetime
from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func

from ..database import Base


class Package(Base):
    __tablename__ = "packages"

    name: Mapped[str] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(nullable=True)
    author_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'))
    latest_version: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=True, default=datetime.now)
    author: Mapped["User"] = relationship(lazy='joined')


class PackageVersion(Base):
    __tablename__ = "package_versions"

    package: Mapped[str] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(primary_key=True)
    info = mapped_column(JSONB)
    url: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
