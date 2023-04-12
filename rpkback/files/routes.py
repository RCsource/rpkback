from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse, FileResponse

from rpkback.database import get_db
from rpkback.files import services
from rpkback.storage import get_storage

files = APIRouter(prefix='/files', tags=['files'])


@files.get('/versions/{package}-{version}.tar.gz')
async def get_package_version_archive(package: str, version: str, db=Depends(get_db), storage=Depends(get_storage)):
    return await services.get_package_version_archive(db, package, version, storage)

