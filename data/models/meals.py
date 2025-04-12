from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class MealModel(BaseModel):
    """Представляет прием пищи пользователя."""

    id: Annotated[
        UUID | None,
        Field(default=None, description="Уникальный идентификатор приема пищи"),
    ]
    name: Annotated[
        str,
        Field(description="Название блюда или продукта"),
    ]
    calories: Annotated[
        int,
        Field(description="Калорийность в ккал"),
    ]
    proteins: Annotated[
        float,
        Field(description="Содержание белков в граммах"),
    ]
    fats: Annotated[
        float,
        Field(description="Содержание жиров в граммах"),
    ]
    carbs: Annotated[
        float,
        Field(description="Содержание углеводов в граммах"),
    ]
    weight: Annotated[
        float,
        Field(description="Вес порции в граммах"),
    ]
    consumed_at: Annotated[
        datetime,
        Field(description="Дата и время приема пищи"),
    ]
    created_at: Annotated[
        datetime,
        Field(default_factory=datetime.now, description="Дата создания записи о приеме пищи"),
    ]
    is_junk_food: Annotated[
        bool,
        Field(default=False, description="Флаг нездоровой пищи"),
    ]
    user_id: Annotated[
        UUID | None,
        Field(default=None, description="Идентификатор пользователя, сделавшего прием пищи"),
    ]
    photo_id: Annotated[
        UUID | None,
        Field(default=None, description="Идентификатор связанной фотографии"),
    ]
