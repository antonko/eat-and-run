from datetime import datetime
from enum import Enum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class WorkoutType(str, Enum):
    """Типы тренировок."""

    RUNNING = "RUNNING"  # Бег, включая трусцой
    WALKING = "WALKING"  # Ходьба, пеший туризм
    CYCLING = "CYCLING"  # Велосипед
    SWIMMING = "SWIMMING"  # Плавание и другие водные
    STRENGTH_TRAINING = "STRENGTH_TRAINING"  # Силовые тренировки
    FLEXIBILITY = "FLEXIBILITY"  # Йога, растяжка, пилатес
    TEAM_SPORTS = "TEAM_SPORTS"  # Командные виды спорта
    MARTIAL_ARTS = "MARTIAL_ARTS"  # Боевые искусства
    WINTER_SPORTS = "WINTER_SPORTS"  # Зимние виды спорта
    OTHER = "OTHER"  # Другое


class WorkoutModel(BaseModel):
    """Представляет тренировку пользователя."""

    id: Annotated[
        UUID | None,
        Field(default=None, description="Уникальный идентификатор тренировки"),
    ]
    name: Annotated[
        str,
        Field(description="Название тренировки"),
    ]
    workout_type: Annotated[
        WorkoutType,
        Field(description="Тип тренировки"),
    ]
    duration_minutes: Annotated[
        int,
        Field(description="Продолжительность тренировки в минутах"),
    ]
    calories_burned: Annotated[
        int,
        Field(description="Количество сожженных калорий"),
    ]
    workout_date: Annotated[
        datetime,
        Field(description="Дата и время тренировки"),
    ]
    created_at: Annotated[
        datetime,
        Field(default_factory=datetime.now, description="Дата создания записи о тренировке"),
    ]
    distance_km: Annotated[
        float | None,
        Field(
            default=None,
            description="Пройденное расстояние в километрах (для беговых тренировок)",
        ),
    ]
    pace_min_per_km: Annotated[
        float | None,
        Field(default=None, description="Темп в минутах на километр (для беговых тренировок)"),
    ]
    user_id: Annotated[
        str | None,
        Field(default=None, description="Идентификатор пользователя, выполнившего тренировку"),
    ]
    photo_id: Annotated[
        str | None,
        Field(default=None, description="Идентификатор связанной фотографии"),
    ]
