with 
    original_name := <str>$original_name,
    name := <str>$name,
    calories := <int64>$calories,
    proteins := <float64>$proteins,
    fats := <float64>$fats,
    carbs := <float64>$carbs,
    date := <datetime>$date

select (
    update Meal
    filter .name = original_name
    set {
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