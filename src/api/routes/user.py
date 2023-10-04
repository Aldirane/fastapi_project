from fastapi import Cookie, Depends, APIRouter, HTTPException
from fastapi.params import Body

from src.api.dependencies import get_current_user, dao_provider
from src.api.models.auth import UserAuth
from src.core.models import dto
from src.core.services.user import (
    set_password, 
    create_user_service,
)
from src.infrastructure.db.dao.holder import HolderDao



async def read_users_me(current_user: dto.User = Depends(get_current_user)) -> dto.User:
    return current_user



async def register_user(
    user: UserAuth,
    dao: HolderDao = Depends(dao_provider),
) -> dto.User:
    password = user.password
    user = user.to_dto()
    return await create_user_service(user, password, dao.user)


async def set_password_route(
    password: str = Body(),  # type: ignore[assignment]
    user: dto.User = Depends(get_current_user),
    dao: HolderDao = Depends(dao_provider),
):
    await set_password(user, password, dao.user)
    raise HTTPException(status_code=200)



def setup(router: APIRouter):
    router.add_api_route("/user/me", read_users_me, methods=["GET"], response_model=dto.User)
    router.add_api_route("/user/me/password", set_password_route, methods=["PUT"])
    router.add_api_route("/user/register", register_user, methods=["POST"])