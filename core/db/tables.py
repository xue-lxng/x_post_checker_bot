from datetime import datetime
from enum import Enum
from typing import Any, List

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    String,
    Text,
    func,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class TypeEnum(str, Enum):
    FLOAT = "float"
    INTEGER = "int"
    STRING = "str"
    DATETIME = "datetime"
    BOOLEAN = "bool"
    TIME = "time"


class AppConfig(Base):
    __tablename__ = "app_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    unique_name: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    type_: Mapped[TypeEnum] = mapped_column(
        String(16), nullable=False, default=TypeEnum.STRING
    )
    sub_data: Mapped[str | None] = mapped_column(String(64), nullable=True)

    def get_value(self) -> Any:
        if self.value is None:
            return None

        if self.type_ == TypeEnum.STRING:
            return self.value
        elif self.type_ == TypeEnum.INTEGER:
            return int(self.value)
        elif self.type_ == TypeEnum.FLOAT:
            return float(self.value)
        elif self.type_ == TypeEnum.DATETIME:
            return datetime.strptime(self.value, self.sub_data or "%Y-%m-%d %H:%M:%S")
        elif self.type_ == TypeEnum.TIME:
            return datetime.strptime(self.value, self.sub_data or "%H:%M:%S").time()
        elif self.type_ == TypeEnum.BOOLEAN:
            return self.value.lower() in ("true", "1", "yes", "y")
        return None


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_tg_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True
    )
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="ru")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    tweets: Mapped[List["Tweet"]] = relationship(back_populates="user")


class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_tg_id"), nullable=False)
    tweet_url: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    tweet_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    community_id: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    on_top: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="tweets")
