import json
from typing import AsyncIterator

import aiohttp

from rpkback import config
from rpkback.exceptions import ItemAlreadyExists


class FileStorage:
    async def download_file(self, path: str) -> bytes:
        raise NotImplementedError

    async def upload_file(self, path: str, data: bytes, **kwargs):
        raise NotImplementedError

    async def remove_file(self, path: str):
        raise NotImplementedError

    async def get_upload_url(self, path, **kwargs):
        raise NotImplementedError

    async def get_download_url(self, path):
        raise NotImplementedError


class YandexFileStorage(FileStorage):
    BASE_URL = "https://cloud-api.yandex.net/v1/disk/resources"

    def __init__(self, token: str):
        self.token = token
        self._session: aiohttp.ClientSession | None = None

    async def start(self):
        self._session = aiohttp.ClientSession(
            headers={
                "Authorization": f"OAuth {self.token}",
                "Accept": "application/json",
            }
        )

    async def close(self):
        await self._session.close()
        self._session = None

    async def get_upload_url(self, path, overwrite=False, **kwargs):
        params = {"path": path, "overwrite": "true" if overwrite else "false"}
        async with self._session.get(
            f"{self.BASE_URL}/upload", params=params
        ) as response:
            response.raise_for_status()
            info = await response.json()
            return info["href"]

    async def upload_file(self, path, data, overwrite=True, **kwargs):
        url = await self.get_upload_url(path, overwrite, **kwargs)
        async with self._session.put(url, data=data) as response:
            print(await response.text())
            response.raise_for_status()

    async def remove_file(self, path):
        params = {"path": path}
        async with self._session.delete(self.BASE_URL, params=params) as response:
            response.raise_for_status()

    async def get_download_url(self, path):
        params = {"path": path}
        async with self._session.get(
            f"{self.BASE_URL}/download", params=params
        ) as response:
            info = await response.json()
            return info["href"]

    async def download_file(self, path) -> bytes:
        url = await self.get_download_url(path)
        async with self._session.get(url) as response:
            return await response.read()

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


async def get_storage() -> AsyncIterator[FileStorage]:
    async with YandexFileStorage(config.YANDEX_TOKEN) as storage:
        yield storage
