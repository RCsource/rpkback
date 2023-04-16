from typing import AsyncIterator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from .config import DB_USER, DB_PORT, DB_HOST, DB_PSWD, DB_NAME


DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PSWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

Base = declarative_base()
engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session
