from typing import Protocol

from src.core.interfaces.dal.base import Committer
from src.core.models import dto

class UserCreate(Committer, Protocol):
    async def create_user(self, user: dto.UserWithCreds) -> dto.User:
        raise NotImplementedError
    
    async def get_by_email(self, user: dto.User) -> dto.User:
        raise NotImplementedError


class UserUpserter(Committer, Protocol):
    async def upsert_user(self, user: dto.User) -> dto.User:
        raise NotImplementedError


class UserPasswordSetter(Committer, Protocol):
    async def set_password(self, user: dto.User, hashed_password: str):
        raise NotImplementedError


class UserByUsernameResolver(Protocol):
    async def get_by_username(self, username: str) -> dto.User:
        raise NotImplementedError


class UserByIdResolver(Protocol):
    async def get_by_id(self, id_: int) -> dto.User:
        raise NotImplementedError
