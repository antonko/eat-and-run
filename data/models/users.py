from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, Json, field_validator


class MemoryModel(BaseModel):
    """Представляет хранимые воспоминания пользователя."""

    id: Annotated[
        UUID | None,
        Field(default=None, description="Уникальный идентификатор воспоминания"),
    ]
    content: Annotated[str, Field(description="Содержание воспоминания")]
    importance: Annotated[
        int,
        Field(default=1, description="Важность воспоминания (по умолчанию 1)"),
    ]
    created_at: Annotated[
        datetime,
        Field(default_factory=datetime.now, description="Дата создания воспоминания"),
    ]
    updated_at: Annotated[
        datetime | None,
        Field(default=None, description="Дата последнего обновления воспоминания"),
    ]
    user_id: Annotated[
        str | None,
        Field(
            default=None,
            description="Идентификатор пользователя, которому принадлежит воспоминание",
        ),
    ]


class UserModel(BaseModel):
    """Представляет пользователя системы."""

    id: Annotated[
        UUID | None,
        Field(default=None, description="Уникальный идентификатор пользователя"),
    ]
    chat_id: Annotated[str, Field(description="ID чата пользователя (должно быть уникальным)")]
    created_at: Annotated[
        datetime,
        Field(default_factory=datetime.now, description="Дата регистрации пользователя"),
    ]
    last_interaction_date: Annotated[
        datetime | None,
        Field(default=None, description="Дата последнего взаимодействия с системой"),
    ]
    interaction_count: Annotated[
        int,
        Field(default=1, description="Количество взаимодействий с системой"),
    ]
    state: Annotated[
        Json,
        Field(default={}, description="JSON данные, хранящие текущее состояние"),
    ]
    memories: Annotated[
        list[MemoryModel],
        Field(default_factory=list, description="Список воспоминаний пользователя"),
    ]

    @field_validator("state", mode="before")
    @classmethod
    def validate_state(cls, value) -> Json:  # noqa: ANN001
        """Преобразует dict в JSON-строку, если это необходимо."""
        import json

        if isinstance(value, dict):
            return json.dumps(value)
        return value
