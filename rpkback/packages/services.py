import json
from uuid import UUID
import tarfile

import pydantic
from fastapi import UploadFile, HTTPException
from fastapi.encoders import jsonable_encoder

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


from . import schemas
from .models import Package, PackageVersion
from ..exceptions import ItemNotFound, ItemAlreadyExists, Forbidden
from ..storage import get_storage, FileStorage
from ..tokens.models import APIToken
from ..users.models import User


async def create_new_package(
    session: AsyncSession, name: str, description: str, author_id: UUID
) -> Package:
    package = Package(name=name, description=description, author_id=author_id)
    session.add(package)
    try:
        await session.commit()
    except IntegrityError:
        raise ItemAlreadyExists("Package with this name already exists")
    await session.refresh(package)
    return package


async def get_package(session: AsyncSession, name: str) -> Package:
    package = await session.get(Package, name)
    if package is None:
        raise ItemNotFound("Package not found")
    return package  # noqa


async def get_package_version(
    session: AsyncSession, package: str, version: str
) -> PackageVersion:
    version = await session.get(
        PackageVersion, {"package": package, "version": version}
    )
    if version is None:
        raise ItemNotFound("Package version not found")
    print(version.__dict__)
    return version  # noqa


async def create_package_version(
    session: AsyncSession, file: UploadFile, token_or_user: APIToken | User, storage: FileStorage
) -> PackageVersion:
    try:
        try:
            tar = tarfile.open(fileobj=file.file)
        except tarfile.ReadError:
            raise HTTPException(400, "File is not tar archive")
        try:
            fileobj = tar.extractfile("package.json")
        except KeyError:
            raise HTTPException(400, "Filename 'package.json' not found")
        try:
            content = json.loads(fileobj.read())
        except json.JSONDecodeError:
            raise HTTPException(400, 'Json decode error')
        try:
            info = schemas.PackageVersionInfo(content)
        except pydantic.ValidationError as e:
            raise HTTPException(status_code=422, detail=jsonable_encoder(e.errors()))
        package = await get_package(session, info.name)
        if isinstance(token_or_user, APIToken):
            error = Forbidden("Wrong api token")
            if token_or_user.user_id != package.author_id:
                raise error
            if (
                token_or_user.package_name != "*"
                and token_or_user.package_name != package.name
            ):
                raise error
        elif isinstance(token_or_user, User):
            if token_or_user.is_removed:
                raise ItemNotFound("User not found")
            if token_or_user.id != package.author_id:
                raise Forbidden("You are not author of this package")
        else:
            raise TypeError("wtf? its impossible")
        path = f"/versions/{info.name}-{info.version}.tar.gz"
        await storage.upload_file(path, await file.read(), overwrite=True)
        package_version = PackageVersion(
            package=info.name,
            version=info.version,
            info=info.dict(),
            url=path,
        )
        session.add(package_version)
        try:
            await session.commit()
        except IntegrityError:
            raise ItemAlreadyExists('Package version already exists')
        await session.refresh(package_version)
        return package_version
    finally:
        file.file.close()


async def search_package(
    session: AsyncSession, q: str | None = None, page: int = 1, size: int = 20
):
    query = select(Package)
    totq = select(func.count(Package.name))
    if q is not None:
        cond = Package.name.like(f"%{q}%") | Package.description.match(f"%{q}%")
        query = query.filter(cond)
        totq = totq.filter(cond)
    total = (await session.execute(totq)).scalar()
    page_count = total // size + (1 if total % size else 0)
    if not page_count:
        page_count = 1
    page = page if page <= page_count else page_count
    query = query.offset(size * (page - 1)).limit(size)
    res = await session.execute(query)
    packages = res.scalars().all()
    return {
        "total": total,
        "page": page,
        "page_count": page_count,
        "packages": packages,
    }
