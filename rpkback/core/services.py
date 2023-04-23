import sqlalchemy.exc
from sqlalchemy import select

from ..database import async_session


async def check_database_connection() -> bool:
    async with async_session() as session:
        try:
            result = await session.execute(select(True))
        except sqlalchemy.exc.DBAPIError:
            return False
        return result.scalar()
