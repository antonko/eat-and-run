select (
    delete Meal 
    filter .name = <str>$name
) {
    name,
    calories,
    proteins,
    fats,
    carbs,
    date
}; 