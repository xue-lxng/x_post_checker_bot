from __future__ import annotations

from typing import Any, Optional, Sequence, List

from sqlalchemy import delete, select, update, insert
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

from core.db.base import Base
from core.db.tables import (
    User,
    AppConfig,
    Tweet,
)


class DatabaseHandler:
    """
    Async database handler for managing shop operations.
    """

    def __init__(self, url: str):
        self.url = url
        self.engine = create_async_engine(self.url, echo=False)
        self.sessionmaker = async_sessionmaker(
            self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )

    async def init(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        await self.engine.dispose()

    # ==================== USER OPERATIONS ====================

    async def create_or_get_user(
        self,
        user_tg_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        language: Optional[str] = "ru",
    ) -> User:
        async with self.sessionmaker() as session:
            result = await session.execute(
                select(User).where(User.user_tg_id == user_tg_id)
            )
            user = result.scalar_one_or_none()

            if user:
                # Обновляем данные если изменились
                if username and user.username != username:
                    user.username = username
                if first_name and user.first_name != first_name:
                    user.first_name = first_name
                if last_name and user.last_name != last_name:
                    user.last_name = last_name
                await session.commit()
                return user

            # Создаем нового пользователя
            user = User(
                user_tg_id=user_tg_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
                language=language,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def get_user(self, user_tg_id: int) -> Optional[User]:
        async with self.sessionmaker() as session:
            result = await session.execute(
                select(User).where(User.user_tg_id == user_tg_id)
            )
            return result.scalar_one_or_none()

    async def update_user(self, user_tg_id: int, **kwargs: Any) -> Optional[User]:
        async with self.sessionmaker() as session:
            async with session.begin():
                result = await session.execute(
                    select(User).where(User.user_tg_id == user_tg_id)
                )
                user = result.scalar_one_or_none()
                if not user:
                    return None

                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)

            return user

    async def delete_user(self, user_tg_id: int) -> bool:
        async with self.sessionmaker() as session:
            async with session.begin():
                result = await session.execute(
                    delete(User).where(User.user_tg_id == user_tg_id)
                )
                return True

    async def ban_user(self, user_tg_id: int) -> bool:
        return await self.update_user(user_tg_id, is_banned=True) is not None

    async def unban_user(self, user_tg_id: int) -> bool:
        return await self.update_user(user_tg_id, is_banned=False) is not None

    async def get_all_users(
        self, limit: int = 100, offset: int = 0, is_banned: Optional[bool] = None
    ) -> Sequence[User]:
        async with self.sessionmaker() as session:
            stmt = select(User)
            if is_banned is not None:
                stmt = stmt.where(User.is_banned == is_banned)
            stmt = stmt.limit(limit).offset(offset).order_by(User.created_at.desc())
            result = await session.execute(stmt)
            return result.scalars().all()

    # ==================== APP CONFIG OPERATIONS ====================

    async def get_config(self, unique_name: str) -> Optional[Any]:
        async with self.sessionmaker() as session:
            result = await session.execute(
                select(AppConfig).where(AppConfig.unique_name == unique_name)
            )
            config = result.scalar_one_or_none()
            return config.get_value() if config else None

    async def set_config(
        self,
        unique_name: str,
        value: str,
        type_: str = "str",
        description: Optional[str] = None,
        description_en: Optional[str] = None,
        sub_data: Optional[str] = None,
    ) -> AppConfig:
        async with self.sessionmaker() as session:
            async with session.begin():
                result = await session.execute(
                    select(AppConfig).where(AppConfig.unique_name == unique_name)
                )
                config = result.scalar_one_or_none()

                if config:
                    config.value = value
                    config.type_ = type_
                    if description:
                        config.description = description
                    if description_en:
                        config.description_en = description_en
                    if sub_data:
                        config.sub_data = sub_data
                else:
                    config = AppConfig(
                        unique_name=unique_name,
                        value=value,
                        type_=type_,
                        description=description,
                        description_en=description_en,
                        sub_data=sub_data,
                    )
                    session.add(config)

                await session.commit()
                await session.refresh(config)
                return config

    async def get_all_active_tweets(self) -> List[Tweet]:
        async with self.sessionmaker() as session:
            result = await session.execute(select(Tweet).where(Tweet.is_active == True))
            return result.scalars().all()

    async def set_on_top_status(self, tweet_id: str, community_id: str, status: bool):
        async with self.sessionmaker() as session:
            await session.execute(
                update(Tweet)
                .where(Tweet.tweet_id == tweet_id, Tweet.community_id == community_id)
                .values(on_top=status)
            )
            await session.commit()
            return True

    async def set_as_inactive(
        self, tweet_id: str, status: bool = False, user_id: Optional[int] = None
    ):
        async with self.sessionmaker() as session:
            stmt = (
                update(Tweet).where(Tweet.tweet_id == tweet_id).values(is_active=status)
            )
            if user_id:
                stmt = stmt.where(Tweet.user_id == user_id)
            await session.execute(stmt)
            await session.commit()
            return True

    async def add_tweet(
        self,
        tweet_url: str,
        tweet_id: str,
        user_id: int,
        community_id: Optional[str] = None,
    ):
        async with self.sessionmaker() as session:
            await session.execute(
                insert(Tweet).values(
                    tweet_url=tweet_url,
                    tweet_id=tweet_id,
                    user_id=user_id,
                    community_id=community_id,
                )
            )
            await session.commit()
            return True
