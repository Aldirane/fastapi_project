from __future__ import annotations

from datetime import datetime
from pydantic import EmailStr
from typing import Optional
from pydantic.dataclasses import dataclass


@dataclass
class User:
    email: EmailStr
    id: Optional[int] = None
    username: Optional[str] = None
    registered_at: Optional[datetime] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
    is_active: Optional[bool] = True



    @property
    def fullname(self) -> str:
        if self.first_name is None:
            return ""
        if self.last_name is not None:
            return " ".join((self.first_name, self.last_name))
        return self.first_name


    def add_password(self, hashed_password: str) -> UserWithCreds:
        return UserWithCreds(
            id=self.id,
            hashed_password=hashed_password,
            email=self.email,
            username=self.username,
            registered_at=self.registered_at,
            first_name=self.first_name,
            last_name=self.last_name,
            is_verified=self.is_verified,
            is_superuser=self.is_superuser,
            is_active=self.is_active,
        )

    def safe_create_update(self, hashed_password) -> UserWithCreds:
        return UserWithCreds(
            hashed_password=hashed_password,
            email=self.email,
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
        )


    def unsafe_create_update(self, hashed_password) -> UserWithCreds:
        return User(
            hashed_password,
            email=self.email,
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            is_verified=self.is_verified,
            is_superuser=self.is_superuser,
            is_active=self.is_active,
        )



@dataclass
class UserWithCreds(User):
    hashed_password: Optional[str] = None

    def without_password(self) -> User:
        return User(
            id=self.id,
            email=self.email,
            username=self.username,
            registered_at=self.registered_at,
            first_name=self.first_name,
            last_name=self.last_name,
            is_verified=self.is_verified,
            is_superuser=self.is_superuser,
            is_active=self.is_active,
        )
