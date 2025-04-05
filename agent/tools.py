import datetime
from collections.abc import Callable
from typing import Any

import gel

from common.configuration import configuration
from queries.get_meals_async_edgeql import GetMealsResult, get_meals
from queries.insert_meals_async_edgeql import insert_meals

client = gel.create_async_client(
    host=configuration.gel_host,
    port=configuration.gel_port,
    user=configuration.gel_user,
    password=configuration.gel_password,
    branch=configuration.gel_branch,
    tls_security=configuration.gel_tls_security,
)


async def save_meals(
    name: str,
    calories: int,
    proteins: float,
    fats: float,
    carbs: float,
    date: datetime.datetime,
) -> None:
    """Сохраняет информацию о приеме пищи в базу данных.

    Эта функция сохраняет данные о блюде со всеми его пищевыми характеристиками (КЖБУ):

    Параметры:
        name: Название блюда или приема пищи (например, "овсянка с молоком", "куриная грудка с рисом")
        calories: Количество калорий в блюде (ккал)
        proteins: Количество белков в блюде (граммы)
        fats: Количество жиров в блюде (граммы)
        carbs: Количество углеводов в блюде (граммы)
        date: Дата и время приема пищи (если не указано, будет использовано текущее время)
    """
    await insert_meals(
        executor=client,
        name=name,
        calories=calories,
        proteins=proteins,
        fats=fats,
        carbs=carbs,
        date=date,
    )


async def get_all_meals() -> list[GetMealsResult]:
    """Получает все приемы пищи из базы данных.

    Эта функция извлекает все записи о приемах пищи, включая название блюда и КЖБУ.
    Записи сортируются по дате и времени приема пищи.

    Возвращает:
        Список объектов GetMealsResult, содержащих информацию о каждом приеме пищи
    """
    return await get_meals(executor=client)


TOOLS: list[Callable[..., Any]] = [save_meals, get_all_meals]
