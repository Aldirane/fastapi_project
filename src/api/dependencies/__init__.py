from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.api.config.models.main import ApiConfig
from src.api.dependencies.auth import get_current_user, AuthProvider
from src.api.dependencies.db import DbProvider, dao_provider
from src.api.dependencies.file import file_provider


def setup(app: FastAPI, pool: async_sessionmaker[AsyncSession], config: ApiConfig):
    db_provider = DbProvider(pool=pool)
    auth_provider = AuthProvider(config.auth)
    app.include_router(auth_provider.router)

    app.dependency_overrides[get_current_user] = auth_provider.get_current_user
    app.dependency_overrides[dao_provider] = db_provider.dao
    app.dependency_overrides[AuthProvider] = lambda: auth_provider
    app.dependency_overrides[file_provider] = lambda: config.file_storage_config