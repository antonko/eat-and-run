import json

import gel

from data.models.users import UserModel


class UserRepository:
    """Репозиторий для работы с пользователями."""

    def __init__(self, executor: gel.AsyncIOExecutor) -> None:
        """Инициализация репозитория."""
        self.executor = executor

    async def get_user_by_chat_id(self, chat_id: str) -> UserModel | None:
        """Получить пользователя по chat_id."""
        query = """
        select User {
            id,
            chat_id,
            created_at,
            last_interaction_date,
            interaction_count,
            state
        }
        filter .chat_id = <str>$chat_id
        """
        result = await self.executor.query_single(query, chat_id=chat_id)
        if not result:
            return None
        return result

    async def create_user(self, user: UserModel) -> UserModel:
        """Создать нового пользователя."""
        query = """
        with
            chat_id := <str>$chat_id,
            created_at := datetime_current(),
            last_interaction_date := datetime_current(),
            interaction_count := <int64>$interaction_count,
            state := <json>$state
        select (
            insert User {
                chat_id := chat_id,
                created_at := created_at,
                last_interaction_date := last_interaction_date,
                interaction_count := interaction_count,
                state := state
            }
        )
        {
            id,
            chat_id,
            created_at,
            last_interaction_date,
            interaction_count,
            state
        }
        """
        return await self.executor.query_single(
            query,
            chat_id=user.chat_id,
            interaction_count=user.interaction_count,
            state=json.dumps(user.state),
        )

    async def update_user(self, user: UserModel) -> UserModel:
        """Обновить пользователя."""
        query = """
        with
            id := <uuid>$id,
            chat_id := <str>$chat_id,
            last_interaction_date := datetime_current(),
            interaction_count := <int64>$interaction_count,
            state := <json>$state
        select (
            update User
            filter .id = id
            set {
                chat_id := chat_id,
                last_interaction_date := last_interaction_date,
                interaction_count := interaction_count,
                state := state,
            }
        )
        { ** }
        """
        return await self.executor.query_single(
            query,
            id=user.id,
            chat_id=user.chat_id,
            interaction_count=user.interaction_count,
            state=json.dumps(user.state),
        )
