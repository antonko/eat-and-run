import json

import gel

from database.models.users import UserModel


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
        result = await self.executor.query_single_json(query, chat_id=chat_id)

        if result is None or result == "null":
            return None

        return UserModel.model_validate_json(result, strict=False)

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
        # Убедимся, что state - это строка JSON
        state_json = user.state
        if not isinstance(state_json, str):
            state_json = json.dumps(state_json)

        result = await self.executor.query_single_json(
            query,
            chat_id=user.chat_id,
            interaction_count=user.interaction_count,
            state=state_json,
        )
        return UserModel.model_validate_json(result, strict=False)

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
        # Убедимся, что state - это строка JSON
        state_json = user.state
        if not isinstance(state_json, str):
            state_json = json.dumps(state_json)

        result = await self.executor.query_single_json(
            query,
            id=user.id,
            chat_id=user.chat_id,
            interaction_count=user.interaction_count,
            state=state_json,
        )

        return UserModel.model_validate_json(result, strict=False)
