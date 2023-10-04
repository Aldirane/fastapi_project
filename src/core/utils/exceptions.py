from typing import Any, Union

from src.core.models import dto


class SHError(Exception):
    notify_user = "Ошибка"

    def __init__(
        self,
        text: str = "",
        user_id: Union[int, None] = None,
        user: Union[dto.User, None] = None,
        notify_user: Union[str, None] = None,
        *args,
        **kwargs,
    ):
        super(SHError, self).__init__(args, kwargs)
        self.text = text
        self.user_id = user_id
        self.user = user
        self.notify_user = notify_user or self.notify_user

    def __repr__(self):
        result_msg = f"Error: {self.text}"
        if self.user_id:
            result_msg += f", by user {self.user_id}"
        if self.notify_user:
            result_msg += f". Information for user: {self.notify_user}"
        return result_msg

    def __str__(self):
        return (
            f"Error.\ntype: {self.__class__.__name__}\n"
            f"text: {self.text}\n"
            f"notify info: {self.notify_user}"
        )


class FileNotFound(SHError, AttributeError):
    notify_user = "Файл не найден"


class UsernameResolverError(SHError):
    notify_user = "Не удалось найти пользователя по username"

    def __init__(self, username: Union[str, None] = None, **kwargs):
        super().__init__(**kwargs)
        self.username = username


class NoUsernameFound(UsernameResolverError):
    notify_user = "К сожалению по этому username ничего не найдено"


class MultipleUsernameFound(UsernameResolverError):
    notify_user = "К сожалению по этому username найдено несколько пользователей"


class InvalidPassword(SHError):
    notify_user = "Неправильно введен пароль"

class EmailValidationError(SHError):
    notify_user = "Email не прошел валидацию!"

