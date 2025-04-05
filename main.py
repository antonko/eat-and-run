import asyncio
from datetime import UTC, datetime

import gel

from queries.get_meals_async_edgeql import get_meals

# Импортируем сгенерированные функции
from queries.insert_meals_async_edgeql import insert_meals
from settings import settings


async def main() -> None:
    """Основная функция для выполнения запросов к базе данных."""
    client = gel.create_async_client(
        host=settings.gel_host,
        port=settings.gel_port,
        user=settings.gel_user,
        password=settings.gel_password,
        branch=settings.gel_branch,
        tls_security=settings.gel_tls_security,
    )

    # Вставка данных о приемах пищи с timezone-aware datetime
    meal_data = [
        ("Овсянка", 300, 10.0, 5.0, 50.0, datetime(2023, 10, 1, 8, 0, 0, tzinfo=UTC)),
        (
            "Куриная грудка с рисом",
            450,
            35.0,
            10.0,
            40.0,
            datetime(2023, 10, 1, 13, 0, 0, tzinfo=UTC),
        ),
        ("Греческий салат", 250, 8.0, 15.0, 12.0, datetime(2023, 10, 1, 19, 0, 0, tzinfo=UTC)),
        (
            "Протеиновый коктейль",
            180,
            25.0,
            3.0,
            10.0,
            datetime(2023, 10, 2, 10, 0, 0, tzinfo=UTC),
        ),
    ]

    for meal in meal_data:
        result = await insert_meals(
            client,
            name=meal[0],
            calories=meal[1],
            proteins=meal[2],
            fats=meal[3],
            carbs=meal[4],
            date=meal[5],
        )
        print(f"Добавлен: {result.name}")

    # Получение данных о приемах пищи
    meals = await get_meals(client)

    print("\nПолучены данные о приемах пищи:")
    for meal_item in meals:
        print(
            f"- {meal_item.name}: {meal_item.calories} ккал, "
            f"Б: {meal_item.proteins}г, Ж: {meal_item.fats}г, У: {meal_item.carbs}г, "
            f"Дата: {meal_item.date}",
        )


asyncio.run(main())
