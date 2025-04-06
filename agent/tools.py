import datetime
from collections.abc import Callable
from typing import Any

from common import gel_client
from queries.get_meals_async_edgeql import GetMealsResult, get_meals
from queries.insert_meals_async_edgeql import insert_meals


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
        executor=gel_client.gel_client,
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
    return await get_meals(executor=gel_client.gel_client)


TOOLS: list[Callable[..., Any]] = [save_meals, get_all_meals]
