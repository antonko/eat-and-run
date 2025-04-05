select Meal {
    name,
    calories,
    proteins,
    fats,
    carbs,
    date
}
filter .name = <str>$name; 