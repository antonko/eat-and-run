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
}; 