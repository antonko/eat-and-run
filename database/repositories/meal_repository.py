from uuid import UUID

import gel

from database.models.meals import MealModel


class MealRepository:
    """Репозиторий для работы с приемами пищи."""

    def __init__(self, executor: gel.AsyncIOExecutor) -> None:
        """Инициализация репозитория."""
        self.executor = executor

    async def save_meal(self, meal: MealModel) -> MealModel:
        """Сохранить прием пищи."""
        query = """
        with
            name := <str>$name,
            calories := <int64>$calories,
            proteins := <float64>$proteins,
            fats := <float64>$fats,
            carbs := <float64>$carbs,
            weight := <float64>$weight,
            consumed_at := <datetime>$consumed_at,
            created_at := datetime_current(),
            is_junk_food := <bool>$is_junk_food,
            user_id := <uuid>$user_id,
            photo_id := <optional int64>$photo_id
        select (
            insert Meal {
                name := name,
                calories := calories,
                proteins := proteins,
                fats := fats,
                carbs := carbs,
                weight := weight,
                consumed_at := consumed_at,
                created_at := created_at,
                is_junk_food := is_junk_food,
                user := (select User filter .id = user_id),
                photo := (select Photo filter .id_int = photo_id)
            }
        )
        {
            id,
            name,
            calories,
            proteins,
            fats,
            carbs,
            weight,
            consumed_at,
            created_at,
            is_junk_food,
            user: {
                id
            },
            photo: {
                id_int
            }
        }
        """

        result = await self.executor.query_single_json(
            query,
            name=meal.name,
            calories=meal.calories,
            proteins=meal.proteins,
            fats=meal.fats,
            carbs=meal.carbs,
            weight=meal.weight,
            consumed_at=meal.consumed_at,
            is_junk_food=meal.is_junk_food,
            user_id=meal.user_id,
            photo_id=meal.photo_id,
        )

        return MealModel.model_validate_json(result, strict=False)

    async def get_meals_by_user_id(self, user_id: UUID) -> list[MealModel]:
        """Получить список приемов пищи по идентификатору пользователя."""
        query = """
        select Meal {
            id,
            name,
            calories,
            proteins,
            fats,
            carbs,
            weight,
            consumed_at,
            created_at,
            is_junk_food
        }
        filter .user.id = <uuid>$user_id
        order by .consumed_at desc
        """

        result = await self.executor.query_json(query, user_id=user_id)

        if result is None or result == "null":
            return []

        import json

        data = json.loads(result)

        return [MealModel.model_validate(item) for item in data]

    async def delete_meal(self, meal_id: UUID) -> None:
        """Удалить прием пищи по идентификатору."""
        query = """
        delete Meal filter .id = <uuid>$meal_id
        """
        await self.executor.query(query, meal_id=meal_id)
