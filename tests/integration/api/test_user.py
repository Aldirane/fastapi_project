import pytest
import pytest_asyncio
from httpx import AsyncClient

from src.core.models import dto
from src.core.services.user import create_user_service
from src.infrastructure.db.dao.holder import HolderDao
from tests.fixtures.user_constant import create_dto_user



@pytest_asyncio.fixture
async def user(dao: HolderDao):
    password = "Password1#"
    user_ = await create_user_service(create_dto_user(), password, dao.user)
    return user_



@pytest.mark.asyncio
async def test_auth(client: AsyncClient, user: dto.User):
    resp = await client.post(
        "/auth/login",
        data={"username": user.email, "password": "Password1#"},
        follow_redirects = True,
    )
    assert resp.is_success
    resp = await client.get("/user/me")
    assert resp.is_success
    actual_user = dto.User(**resp.json())
    assert user.username == actual_user.username



@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, user: dto.User):
    resp = await client.post(
        "/auth/login",
        data={"username": user.email, "password": "Password1#"},
        follow_redirects = True,
    )
    assert resp.is_success
    resp = await client.put(
        "/user/me/password/",
        json="Password2@",
        follow_redirects=True,
    )
    assert resp.is_success
    resp = await client.post(
        "/auth/login",
        data={"username": user.email, "password": "Password1#"},
        follow_redirects = True,
    )
    assert not resp.is_success
    resp = await client.post(
        "/auth/login",
        data={"username": user.email, "password": "Password2@"},
        follow_redirects = True,
    )
    assert resp.is_success
