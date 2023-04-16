from datetime import datetime
from typing import TypeVar
from uuid import UUID

from pydantic import BaseModel, constr, FileUrl, Field

from rpkback.users.schemas import User

SemVer: TypeVar = constr(
    regex=r"^(?P<major>0|[1-9]\d*)\."
    r"(?P<minor>0|[1-9]\d*)\."
    r"(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


class PackageVersionInfo(BaseModel):
    name: str
    version: SemVer
    description: str
    license: str = Field(example="MIT")
    dependencies: dict[str, SemVer]

    class Config:
        orm_mode = True


class Package(BaseModel):
    name: str
    description: str | None
    latest_version: SemVer | None
    author: User
    created_at: datetime
    updated_at: datetime | None

    class Config:
        orm_mode = True


class PackageUpdate(BaseModel):
    description: str | None
    latest_version: str | None


class CreatePackage(BaseModel):
    name: str
    description: str | None


class PackageVersion(BaseModel):
    info: PackageVersionInfo
    package: Package
    url: str
    created_at: datetime

    class Config:
        orm_mode = True


class SearchSearchResult(BaseModel):
    total: int
    page: int
    page_count: int
    packages: list[Package]
