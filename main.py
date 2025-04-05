import gel
import asyncio
from settings import settings
from datetime import datetime, timezone

# Импортируем сгенерированные функции
from queries.insert_meals_async_edgeql import insert_meals
from queries.get_meals_async_edgeql import get_meals
from queries.get_meal_by_name_async_edgeql import get_meal_by_name
from queries.delete_meal_async_edgeql import delete_meal
from queries.get_meals_by_date_range_async_edgeql import get_meals_by_date_range
from queries.update_meal_async_edgeql import update_meal

async def main():
    client = gel.create_async_client(
        host=settings.gel_host,
        port=settings.gel_port,
        user=settings.gel_user,
        password=settings.gel_password,
        branch=settings.gel_branch,
        tls_security=settings.gel_tls_security
    )
    
    # Вставка данных о приемах пищи с timezone-aware datetime
    meal_data = [
        ('Овсянка', 300, 10.0, 5.0, 50.0, datetime(2023, 10, 1, 8, 0, 0, tzinfo=timezone.utc)),
        ('Куриная грудка с рисом', 450, 35.0, 10.0, 40.0, datetime(2023, 10, 1, 13, 0, 0, tzinfo=timezone.utc)),
        ('Греческий салат', 250, 8.0, 15.0, 12.0, datetime(2023, 10, 1, 19, 0, 0, tzinfo=timezone.utc)),
        ('Протеиновый коктейль', 180, 25.0, 3.0, 10.0, datetime(2023, 10, 2, 10, 0, 0, tzinfo=timezone.utc))
    ]
    
    for meal in meal_data:
        result = await insert_meals(
            client,
            name=meal[0],
            calories=meal[1],
            proteins=meal[2],
            fats=meal[3],
            carbs=meal[4],
            date=meal[5]
        )
        print(f"Добавлен: {result.name}")
    
    # Получение данных о приемах пищи
    meals = await get_meals(client)
    
    print("\nПолучены данные о приемах пищи:")
    for meal in meals:
        print(f"- {meal.name}: {meal.calories} ккал, Б: {meal.proteins}г, Ж: {meal.fats}г, У: {meal.carbs}г, Дата: {meal.date}")
    
    # Пример получения приема пищи по названию
    meal_name = "Греческий салат"
    meals_by_name = await get_meal_by_name(client, name=meal_name)
    
    if meals_by_name:
        meal_by_name = meals_by_name[0]
        print(f"\nПоиск по названию '{meal_name}':")
        print(f"- {meal_by_name.name}: {meal_by_name.calories} ккал, Б: {meal_by_name.proteins}г, Ж: {meal_by_name.fats}г, У: {meal_by_name.carbs}г, Дата: {meal_by_name.date}")
    
    # Пример поиска приемов пищи по диапазону дат
    start_date = datetime(2023, 10, 1, 0, 0, 0, tzinfo=timezone.utc)
    end_date = datetime(2023, 10, 1, 23, 59, 59, tzinfo=timezone.utc)
    
    meals_by_date = await get_meals_by_date_range(
        client, 
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"\nПриемы пищи за {start_date.date()}:")
    for meal in meals_by_date:
        print(f"- {meal.name}: {meal.calories} ккал, Б: {meal.proteins}г, Ж: {meal.fats}г, У: {meal.carbs}г, Дата: {meal.date}")
    
    # Пример обновления приема пищи
    meal_to_update = "Овсянка"
    updated_meals = await update_meal(
        client,
        original_name=meal_to_update,
        name="Овсянка с ягодами",
        calories=350,
        proteins=12.0,
        fats=6.0,
        carbs=55.0,
        date=datetime(2023, 10, 1, 8, 0, 0, tzinfo=timezone.utc)
    )
    
    if updated_meals:
        updated_meal = updated_meals[0]
        print(f"\nОбновлен прием пищи: {meal_to_update} -> {updated_meal.name}")
    
    # Пример удаления приема пищи
    meal_to_delete = "Протеиновый коктейль"
    deleted_meals = await delete_meal(client, name=meal_to_delete)
    
    if deleted_meals:
        deleted_meal = deleted_meals[0]
        print(f"\nУдален прием пищи: {deleted_meal.name}")
    
    # Получение обновленного списка
    meals_after_changes = await get_meals(client)
    
    print("\nОбновленный список приемов пищи:")
    for meal in meals_after_changes:
        print(f"- {meal.name}: {meal.calories} ккал, Б: {meal.proteins}г, Ж: {meal.fats}г, У: {meal.carbs}г, Дата: {meal.date}")

asyncio.run(main())