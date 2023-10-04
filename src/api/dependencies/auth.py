from datetime import datetime, timedelta
import logging
from typing import Literal, Optional, cast, Callable
from fastapi.responses import JSONResponse, RedirectResponse
import requests
import re
from starlette import status
from starlette.responses import HTMLResponse
from starlette.status import HTTP_403_FORBIDDEN

from fastapi import Request, Response, status 
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from src.api.config.models.auth import AuthConfig
from src.api.dependencies.db import dao_provider
from src.api.models.auth import Token
from src.core.models import dto
from src.core.utils.datetime_utils import tz_utc
from src.core.utils.exceptions import NoUsernameFound
from src.infrastructure.db.dao.holder import HolderDao

from sqlalchemy.exc import NoResultFound


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_current_user() -> dto.User:
    raise NotImplementedError


class AuthProvider:
    def __init__(self, config: AuthConfig):
        self.config = config
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = config.secret_key
        self.algorithm = "HS256"
        self.access_token_expire = config.token_expire
        self.auto_error: bool = True
        self.cookie_path_access: str = "/"
        self.cookie_name_access = "access"
        self.cookie_domain: Optional[str] = None
        self.cookie_secure: bool = True
        self.cookie_httponly: bool = True
        self.cookie_samesite: Literal["lax", "strict", "none"] = "lax"
        self.router = APIRouter()
        self.setup_auth_routes()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    async def authenticate_user(self, email: str, password: str, dao: HolderDao) -> dto.User:
        http_status_401 = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            user = await dao.user.get_by_email_with_password(email)
        except NoUsernameFound:
            raise http_status_401
        if not self.verify_password(password, user.hashed_password or ""):
            raise http_status_401
        return user.without_password()

    def create_token(self, data: dict, expires_delta: timedelta, secret) -> Token:
        to_encode = data.copy()
        expire = datetime.now(tz=tz_utc) + expires_delta
        to_encode.update({"exp": expire})
        token = jwt.encode(to_encode, secret, algorithm=self.algorithm)
        return token
    
    def create_access_token(self, user: dto.User) -> Token:
        return self.create_token(
            data={"sub": user.email}, 
            expires_delta=self.access_token_expire,
            secret=self.secret_key
        )
        

    async def get_cookie_token(self, request: Request) -> Optional[str]:
        api_key = request.cookies.get(self.cookie_name_access)
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authenticated",
            )
        return api_key


    async def get_current_user(
        self,
        request: Request,
        dao: HolderDao = Depends(dao_provider),
    ) -> dto.User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        token = await self.get_cookie_token(request)
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        try:
            user = await dao.user.get_by_email(email)
        except NoUsernameFound:
            raise credentials_exception
        return user


    async def login(
        self,
        form_data: OAuth2PasswordRequestForm = Depends(),
        dao: HolderDao = Depends(dao_provider),
    ) -> Token:
        user = await self.authenticate_user(form_data.username, form_data.password, dao)
        print("AUTHENTICATE USER")
        token = self.create_access_token(user)
        return await self.get_login_response(token)


    async def logout(
        self,
    ) -> Response:
        response = await self.get_logout_response()
        return response

    async def get_login_response(self, token: str) -> Response:
        response = Response(status_code=status.HTTP_204_NO_CONTENT)
        response = self._set_login_cookie(response, token, self.cookie_name_access, self.access_token_expire, self.cookie_path_access)
        return response


    async def get_logout_response(self) -> Response:
        response = Response(status_code=status.HTTP_204_NO_CONTENT)
        response = self._set_logout_cookie(response, self.cookie_name_access, self.cookie_path_access)
        return response


    def _set_login_cookie(self, response: Response, token: str, cookie_name: str, expire: timedelta, path: str) -> Response:
        response.set_cookie(
            cookie_name,
            token,
            max_age=int(expire.total_seconds()),
            path=path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )
        return response


    def _set_logout_cookie(self, response: Response, cookie_name: str, path: str) -> Response:
        response.set_cookie(
            cookie_name,
            "",
            max_age=0,
            path=path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )
        return response


    def setup_auth_routes(self):
        self.router.add_api_route("/auth/login", self.login, methods=["POST"])
        self.router.add_api_route("/auth/logout", self.logout, methods=["POST"])

