from fastapi import HTTPException
from src.core.interfaces.dal.user import UserUpserter, UserPasswordSetter, UserByIdResolver, UserCreate
from src.core.models import dto
from src.core.utils.exceptions import InvalidPassword, EmailValidationError, NoUsernameFound
from passlib.context import CryptContext
import re
from sqlalchemy.exc import NoResultFound


async def authentication():
    return


async def create_user_service(user: dto.User, password: str, dao: UserCreate) -> dto.User:
    await validate_email_service(user, dao)
    validate_password_service(password)
    hashed_password = get_password_hash(password)
    user = user.safe_create_update(hashed_password)
    return await dao.create_user(user)




def get_password_hash(password: str) -> str:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


async def get_user(id_: int, dao: UserByIdResolver):
    return await dao.get_by_id(id_)


async def set_password(user: dto.User, password: str, dao: UserPasswordSetter):
    validate_password_service(password)
    hashed_password = get_password_hash(password)
    await dao.set_password(user, hashed_password)
    await dao.commit()


async def upsert_user(user: dto.User, user_dao: UserUpserter) -> dto.User:
    saved_user = await user_dao.upsert_user(user)
    await user_dao.commit()
    return saved_user


async def validate_email_service(user: dto.User, dao: UserCreate) -> None:
    try:
        await _validate_email(user, dao)
    except EmailValidationError as e:
        raise HTTPException(
            status_code=400,
            detail=e.text,
        )
    


def validate_password_service(password:str) -> None:
    try:
        _validate_password(password)
    except InvalidPassword as e:
        raise HTTPException(
            status_code=400, 
            detail=e.text,
        )
    


async def _validate_email(user: dto.User, dao: UserCreate) -> None:
    try:
        await dao.get_by_email(user.email)
    except NoResultFound:
        pass
    except NoUsernameFound:
        pass
    else:
        raise EmailValidationError("Пользователь с данным email уже существует!")
    


def _validate_password(password:str) -> None:
    if not 8 <= len(password) <= 18:
        raise InvalidPassword("Пароль должен содержать не менее 8 символов и не более 18")
    if not re.search('(?=.*?[A-Z])', password):
        raise InvalidPassword("Пароль должен содержать как минимум 1 заглавную букву!")
    if not re.search('(?=.*?[a-z])', password):
        raise InvalidPassword("Пароль должен содержать как минимум 1 маленькую букву!")
    if not re.search('(?=.*?[0-9])', password):
        raise InvalidPassword("Пароль должен содержать как минимум 1 цифру!")
    if not re.search('(?=.*?[#?!@$%^&*-])', password):
        raise InvalidPassword("Пароль должен содержать как минимум 1 спец символ!")
    
