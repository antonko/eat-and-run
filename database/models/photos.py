from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class PhotoModel(BaseModel):
    """Представляет фотографию, загруженную пользователем."""

    id: Annotated[
        UUID | None,
        Field(default=None, description="Уникальный идентификатор фотографии"),
    ]
    id_int: Annotated[
        int | None,
        Field(default=None, description="Целочисленный идентификатор фотографии"),
    ]
    file_data_base64: Annotated[
        str,
        Field(description="Бинарные данные файла фотографии в формате base64"),
    ]
    file_name: Annotated[
        str,
        Field(description="Оригинальное имя файла фотографии"),
    ]
    mime_type: Annotated[
        str,
        Field(description="MIME-тип файла фотографии (например, image/jpeg)"),
    ]
    created_at: Annotated[
        datetime,
        Field(default_factory=datetime.now, description="Дата создания записи о фотографии"),
    ]
    description: Annotated[
        str | None,
        Field(default=None, description="Описание фотографии"),
    ]
    user_id: Annotated[
        UUID | None,
        Field(default=None, description="Идентификатор пользователя, загрузившего фотографию"),
    ]
