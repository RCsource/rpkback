from datetime import datetime
from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, text, func

from ..database import Base


class Package(Base):
    __tablename__ = "packages"

    name: Mapped[str] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(nullable=True)
    author_id: Mapped[UUID]
    latest_version: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=True, default=datetime.now)


class PackageVersion(Base):
    __tablename__ = "package_versions"

    package: Mapped[str] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(primary_key=True)
    info = mapped_column(JSONB)
    url: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
