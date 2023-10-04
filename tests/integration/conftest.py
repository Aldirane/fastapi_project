import os
from typing import Generator, AsyncGenerator

import pytest
import pytest_asyncio
from alembic.command import upgrade
from alembic.config import Config as AlembicConfig
from dataclass_factory import Factory
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, close_all_sessions

from sqlalchemy.engine import make_url

from src.common import Paths
# from src.core.interfaces.clients.file_storage import FileStorage, FileGateway
# from src.infrastructure.clients.file_gateway import BotFileGateway
from src.infrastructure.db.dao.holder import HolderDao
# from tests.mocks.file_storage import MemoryFileStorage


@pytest_asyncio.fixture
async def dao(session: AsyncSession) -> HolderDao:
    dao_ = HolderDao(session=session)
    await clear_data(dao_)
    return dao_


@pytest_asyncio.fixture
async def check_dao(session: AsyncSession) -> HolderDao:
    return HolderDao(session=session)



async def clear_data(dao: HolderDao):
    await dao.user.delete_all()
    await dao.commit()


@pytest_asyncio.fixture
async def session(pool: sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    async with pool() as session_:
        yield session_


@pytest.fixture(scope="session")
def pool(postgres_url: str) -> Generator[sessionmaker, None, None]:
    engine = create_async_engine(url=make_url(postgres_url), echo=True)
    pool_: async_sessionmaker[AsyncSession] = async_sessionmaker(
        bind=engine, expire_on_commit=False, autoflush=False
    )
    yield pool_  # type: ignore[misc]
    close_all_sessions()


@pytest.fixture(scope="session")
def postgres_url() -> Generator[str, None, None]:
    postgres_url_ = "postgresql+asyncpg://aldar:password@localhost:5432/test_fastapi_project"
    return postgres_url_



@pytest.fixture(scope="session")
def alembic_config(postgres_url: str, paths: Paths) -> AlembicConfig:
    alembic_cfg = AlembicConfig(str(paths.app_dir.parent / "alembic.ini"))
    alembic_cfg.set_main_option(
        "script_location",
        str(paths.app_dir.parent / "src" / "infrastructure" / "db" / "migrations"),
    )
    alembic_cfg.set_main_option("sqlalchemy.url", postgres_url)
    return alembic_cfg


@pytest.fixture(scope="session", autouse=True)
def upgrade_schema_db(alembic_config: AlembicConfig):
    upgrade(alembic_config, "head")


# @pytest.fixture(scope="session")
# def file_storage() -> FileStorage:
#     return MemoryFileStorage()



# @pytest.fixture(autouse=True)
# def clean_up_memory(file_storage: MemoryFileStorage):
#     file_storage.storage.clear()
