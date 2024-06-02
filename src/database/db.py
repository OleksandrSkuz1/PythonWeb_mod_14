import contextlib

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.conf.config import config


class DataBaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(autoflush=False, autocommit=False,
                                                                     bind=self._engine)

    @property
    def async_engine(self):
        return self._engine

    @property
    def async_session(self):
        return self._session_maker

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Session does not exist")
        session = self._session_maker()
        try:
            yield session
        except HTTPException as err:
            raise err  # Raise the HTTPException to be handled by FastAPI
        except Exception as err:
            print(err)
            await session.rollback()
            raise err  # Raise the generic exception to be handled by FastAPI
        finally:
            await session.close()


sessionmanager = DataBaseSessionManager(config.DB_URL)


async def get_db():
    async with sessionmanager.session() as session:
        yield session



