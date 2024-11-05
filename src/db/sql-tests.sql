SELECT
    make_name, model_name, town_name, county_name
FROM
    cars
JOIN models USING (model_id)
JOIN makes USING (make_id)
JOIN towns USING (town_id)
JOIN counties USING (county_id)
WHERE
    make_name = 'Ford'
LIMIT 10;