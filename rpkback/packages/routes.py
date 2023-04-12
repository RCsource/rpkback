from fastapi import APIRouter, File, UploadFile, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas, services
from ..database import get_db
from ..storage import get_storage
from ..tokens.models import APIToken
from ..tokens.services import get_current_token_or_user
from ..users.models import User
from ..users.services import get_current_user

packages = APIRouter(prefix="/packages", tags=["packages"])


@packages.post("/")
async def create_new_package(
    data: schemas.CreatePackage,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.Package:
    return await services.create_new_package(db, data.name, data.description, user.id)


@packages.post("/publish")
async def publish_package_version(
    version: UploadFile = File(description="tar archived package version"),
    token_or_user: User | APIToken = Depends(get_current_token_or_user),
    db=Depends(get_db),
    storage=Depends(get_storage)
) -> schemas.PackageVersion:
    version = await services.create_package_version(db, version, token_or_user, storage)
    return schemas.PackageVersion(
        package=await services.get_package(db, version.package),
        url=version.url,
        info=version.info,
        version=version.version,
        created_at=version.created_at
    )


@packages.get('/{package}')
async def get_package(package: str, db=Depends(get_db)) -> schemas.Package:
    return await services.get_package(db, package)


@packages.get("/{package}/{version}")
async def get_package_version_info(
    package: str, version: str | None = None, db=Depends(get_db)
) -> schemas.PackageVersion:
    version = await services.get_package_version(db, package, version)
    return schemas.PackageVersion(
        package=await services.get_package(db, version.package),
        version=version.version,
        url=version.url,
        created_at=version.created_at,
        info=version.info
    )


@packages.get("/")
async def search(
    q: str | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, lt=100),
    db=Depends(get_db),
) -> schemas.SearchSearchResult:
    print(q)
    return await services.search_package(db, q, page, size)
