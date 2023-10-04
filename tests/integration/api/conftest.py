from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.api import dependencies, routes
from src.api.config.models.main import ApiConfig
from src.api.config.parser.main import load_config
from src.api.dependencies import AuthProvider
from src.api.main_factory import create_app
from src.common import Paths

from tests.mocks.config import DBConfig



@pytest.fixture(scope="session")
def api_config(paths: Paths) -> ApiConfig:
    return load_config(paths)


@pytest.fixture(autouse=True)
def patch_api_config(api_config: ApiConfig, postgres_url: str):
    api_config.db = DBConfig(postgres_url)  # type: ignore[assignment]


@pytest.fixture(scope="session")
def app(api_config: ApiConfig, pool: async_sessionmaker[AsyncSession]) -> FastAPI:
    app = create_app()
    dependencies.setup(app=app, pool=pool, config=api_config)
    routes.setup(app.router)
    return app


@pytest.fixture(scope="session")
def auth(api_config: ApiConfig):
    return AuthProvider(api_config.auth)


@pytest.mark.anyio
@pytest_asyncio.fixture(scope="session")
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="https://test") as ac:
        yield ac
