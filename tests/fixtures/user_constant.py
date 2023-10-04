from copy import copy

from src.core.models import dto

USER_EMAIL = "test@mail.ru"
USER_FIRST_NAME = "Boris"
USER_LAST_NAME = "Britva"
USERNAME = "britva"

USER_DTO = dto.User(
    email=USER_EMAIL,
    first_name=USER_FIRST_NAME,
    last_name=USER_LAST_NAME,
    username=USERNAME,
)


def create_dto_user() -> dto.User:
    return copy(USER_DTO)
