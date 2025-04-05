select Meal {
    name,
    calories,
    proteins,
    fats,
    carbs,
    date
}
filter .date >= <datetime>$start_date
and .date <= <datetime>$end_date
order by .date; 