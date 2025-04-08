import datetime
from collections.abc import Callable
from typing import Any

from agent.food_analyzer import FoodAnalysis, FoodAnalyzer
from agent.utils import load_chat_model
from common import gel_client
from common.file_repository import get_image
from queries.get_meals_async_edgeql import GetMealsResult, get_meals
from queries.insert_meals_async_edgeql import insert_meals


async def analyze_image(image_guid: str) -> FoodAnalysis:
    """Анализирует изображение и возвращает результат анализа.

    Args:
        image_guid: guid of saved image

    Returns:
        FoodAnalysis: result of image analysis

    """
    llm = load_chat_model()
    food_analyzer = FoodAnalyzer(llm)

    image_data = await get_image(image_guid)
    return await food_analyzer.analyze_image(image_data)


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
    # Проверка на наличие часового пояса в дате
    if date.tzinfo is None:
        date = date.replace(tzinfo=datetime.UTC)

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


TOOLS: list[Callable[..., Any]] = [save_meals, get_all_meals, analyze_image]
