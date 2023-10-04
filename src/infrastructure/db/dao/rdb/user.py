from typing import Sequence

from sqlalchemy import select, ScalarResult, Result
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func as safunc

from src.core.models import dto
from src.core.utils.exceptions import MultipleUsernameFound, NoUsernameFound
from src.infrastructure.db.models import User
from .base import BaseDAO


class UserDao(BaseDAO[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def create_user(self, user_dto: dto.UserWithCreds) -> dto.User:
        created_user = User(
            email=user_dto.email,
            username=user_dto.username,
            first_name = user_dto.first_name,
            last_name = user_dto.last_name,
            hashed_password=user_dto.hashed_password,
            is_active = user_dto.is_active,
            is_verified = user_dto.is_verified,
            is_superuser = user_dto.is_superuser
        )
        self.session.add(created_user)
        await self.commit()
        return created_user.to_dto()

    
    async def get_by_email_with_password(self, email: str) -> dto.UserWithCreds:
        user = await self._get_by_email(email)
        return user.to_dto().add_password(user.hashed_password)


    async def get_by_email(self, email: str) -> dto.User:
        user = await self._get_by_email(email)
        return user.to_dto()
    

    async def get_by_id(self, id_: int) -> dto.User:
        return (await self._get_by_id(id_)).to_dto()


    async def get_by_username(self, username: str) -> dto.User:
        user = await self._get_by_username(username)
        return user.to_dto()


    async def get_by_username_with_password(self, username: str) -> dto.UserWithCreds:
        user = await self._get_by_username(username)
        return user.to_dto().add_password(user.hashed_password)


    async def set_password(self, user: dto.UserWithCreds, hashed_password: str):
        assert user.id
        db_user = await self._get_by_id(user.id)
        db_user.hashed_password = hashed_password
        user.hashed_password = hashed_password


    async def upsert_user(self, user: dto.UserWithCreds) -> dto.User:
        kwargs = dict(
            hashed_password=user.hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            email=user.email,
            is_active = user.is_active,
            is_verified = user.is_verified,
            is_superuser = user.is_superuser,
        )
        saved_user = await self.session.execute(
            insert(User)
            .values(**kwargs)
            .on_conflict_do_update(
                index_elements=(User.id,), set_=kwargs, where=User.id == user.id
            )
            .returning(User)
        )
        return saved_user.scalar_one().to_dto()
    

    async def _get_by_email(self, email: str) -> User:
        result: Result[tuple[User]] = await self.session.execute(
            select(User).where(safunc.lower(User.email) == email.lower().strip())
        )
        try:
            user = result.scalar_one()
        except MultipleResultsFound as e:
            raise MultipleUsernameFound(username=email) from e
        except NoResultFound as e:
            raise NoUsernameFound(username=email) from e
        return user
        

    async def _get_by_username(self, username: str) -> User:
        result: Result[tuple[User]] = await self.session.execute(
            select(User).where(User.username == username)
        )
        try:
            user = result.scalar_one()
        except MultipleResultsFound as e:
            raise MultipleUsernameFound(username=username) from e
        except NoResultFound as e:
            raise NoUsernameFound(username=username) from e
        return user


