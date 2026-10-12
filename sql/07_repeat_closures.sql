-- How concentrated are closures? Restaurants by number of DOHMH closures in the period
SELECT
    closures_per_restaurant,
    COUNT(*) AS restaurants
FROM (
    SELECT restaurant_id, SUM(closed) AS closures_per_restaurant
    FROM inspections
    GROUP BY restaurant_id
)
WHERE closures_per_restaurant > 0
GROUP BY closures_per_restaurant
ORDER BY closures_per_restaurant;
