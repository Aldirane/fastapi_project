from pydantic import BaseModel, EmailStr
from typing import Optional

from src.core.models import dto


class UserAuth(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    
    def to_dto(self):
        return dto.User(
            email=self.email,
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name
    )



class Token(BaseModel):
    access_token: str
    token_type: str
