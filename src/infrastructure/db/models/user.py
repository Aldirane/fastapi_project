from datetime import datetime
from sqlalchemy import Boolean, Integer, String, TIMESTAMP, Text
from sqlalchemy.orm import Mapped, mapped_column
from src.core.models import dto
from src.infrastructure.db.models.base import Base


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=True
    )
    first_name: Mapped[str] = mapped_column(Text, nullable=True)
    last_name: Mapped[str] = mapped_column(Text, nullable=True)
    registered_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.utcnow
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    

    def to_dto(self) -> dto.User:
        return dto.User(
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
