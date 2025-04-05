# AUTOGENERATED FROM 'queries/insert_meals.edgeql' WITH:
#     $ gel-py --dsn gel://test:test@localhost:5656/main --tls-security insecure


from __future__ import annotations
import dataclasses
import datetime
import gel
import uuid


class NoPydanticValidation:
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        # Pydantic 2.x
        from pydantic_core.core_schema import any_schema
        return any_schema()

    @classmethod
    def __get_validators__(cls):
        # Pydantic 1.x
        from pydantic.dataclasses import dataclass as pydantic_dataclass
        _ = pydantic_dataclass(cls)
        cls.__pydantic_model__.__get_validators__ = lambda: []
        return []


@dataclasses.dataclass
class InsertMealsResult(NoPydanticValidation):
    id: uuid.UUID
    name: str
    calories: int
    proteins: float
    fats: float
    carbs: float
    date: datetime.datetime


async def insert_meals(
    executor: gel.AsyncIOExecutor,
    *,
    name: str,
    calories: int,
    proteins: float,
    fats: float,
    carbs: float,
    date: datetime.datetime,
) -> InsertMealsResult:
    return await executor.query_single(
        """\
        with 
            name := <str>$name,
            calories := <int64>$calories,
            proteins := <float64>$proteins,
            fats := <float64>$fats,
            carbs := <float64>$carbs,
            date := <datetime>$date

        select (
            insert Meal {
                name := name,
                calories := calories,
                proteins := proteins,
                fats := fats,
                carbs := carbs,
                date := date
            }
        ) {
            name,
            calories,
            proteins,
            fats,
            carbs,
            date
        };\
        """,
        name=name,
        calories=calories,
        proteins=proteins,
        fats=fats,
        carbs=carbs,
        date=date,
    )
