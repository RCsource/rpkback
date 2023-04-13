from tempfile import NamedTemporaryFile
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from rpkback.packages.services import get_package_version
from rpkback.storage import FileStorage


async def get_package_version_archive(session: AsyncSession, package: str, version: str, storage: FileStorage):
    version = await get_package_version(session, package, version)
    data = await storage.download_file(version.url)
    return Response(data, media_type='application/tar+gzip')
