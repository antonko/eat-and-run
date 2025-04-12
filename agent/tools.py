import datetime
import logging
from collections.abc import Callable
from typing import Annotated, Any
from uuid import UUID

from langgraph.prebuilt import InjectedState

from agent.food_analyzer import FoodAnalysis, FoodAnalyzer
from agent.utils import load_chat_model
from common import gel_client
from database.models.meals import MealModel
from database.repositories.meal_repository import MealRepository
from database.repositories.photo_repository import PhotoRepository

logger = logging.getLogger(__name__)


async def analyze_image(
    photo_id_int: int,
    user_id: Annotated[UUID, InjectedState("user_id")],
) -> FoodAnalysis:
    """Анализирует изображение и возвращает результат анализа.

    Args:
        photo_id: Целочисленный идентификатор фотографии (id_int)

    Returns:
        FoodAnalysis: result of image analysis

    """
    llm = load_chat_model()
    food_analyzer = FoodAnalyzer(llm)
    photo_repository = PhotoRepository(gel_client.gel_client)

    photo = await photo_repository.get_photo_by_id_int(photo_id_int)
    if not photo:
        raise ValueError(f"Фотография с id {photo_id_int} не найдена")

    return await food_analyzer.analyze_image(photo.file_data_base64)


async def save_meals(
    name: str,
    calories: int,
    proteins: float,
    fats: float,
    carbs: float,
    weight: float,
    consumed_at: datetime.datetime,
    user_id: Annotated[UUID, InjectedState("user_id")],
    is_junk_food: bool = False,
) -> dict:
    """Создает новую запись о приеме пищи в базе данных.

    Эта функция создает запись о приеме пищи со всеми его характеристиками и связями.

    Args:
        name: Название блюда или продукта (например, "Салат Цезарь", "Яблоко")
        calories: Количество калорий в блюде (ккал)
        proteins: Количество белков в блюде (граммы)
        fats: Количество жиров в блюде (граммы)
        carbs: Количество углеводов в блюде (граммы)
        weight: Вес порции в граммах
        consumed_at: Дата и время приема пищи
        is_junk_food: Флаг, указывающий является ли пища нездоровой (по умолчанию False)

    Returns:
        dict: Информация о созданном приеме пищи

    """
    # Проверка на наличие часового пояса в дате
    if consumed_at.tzinfo is None:
        consumed_at = consumed_at.replace(tzinfo=datetime.UTC)

    meal_repository = MealRepository(gel_client.gel_client)
    meal = MealModel(
        name=name,
        calories=calories,
        proteins=proteins,
        fats=fats,
        carbs=carbs,
        weight=weight,
        consumed_at=consumed_at,
        is_junk_food=is_junk_food,
        user_id=user_id,
    )

    saved_meal = await meal_repository.save_meal(meal)

    return {
        "id": str(saved_meal.id),
        "name": saved_meal.name,
        "calories": saved_meal.calories,
        "proteins": saved_meal.proteins,
        "fats": saved_meal.fats,
        "carbs": saved_meal.carbs,
        "weight": saved_meal.weight,
        "consumed_at": saved_meal.consumed_at.isoformat(),
        "is_junk_food": saved_meal.is_junk_food,
    }


async def get_meals(user_id: Annotated[UUID, InjectedState("user_id")]) -> list[MealModel]:
    """Получает список всех приемов пищи пользователя.

    Эта функция извлекает все записи о приемах пищи для указанного пользователя.
    Записи отсортированы по дате и времени приема пищи (от новых к старым).

    Returns:
        list[MealModel]: Список приемов пищи

    """
    meal_repository = MealRepository(gel_client.gel_client)

    return await meal_repository.get_meals_by_user_id(user_id)


async def delete_meal(
    meal_id: UUID,
    user_id: Annotated[UUID, InjectedState("user_id")],
) -> None:
    """Удаляет запись о приеме пищи по его идентификатору.

    Args:
        meal_id: Идентификатор приема пищи

    """
    meal_repository = MealRepository(gel_client.gel_client)
    await meal_repository.delete_meal(meal_id)


TOOLS: list[Callable[..., Any]] = [
    analyze_image,
    save_meals,
    get_meals,
    delete_meal,
]
