-- Which cuisines score worst and best on initial inspections? (cuisines with 300+ initial inspections)
SELECT
    cuisine,
    COUNT(DISTINCT restaurant_id)                                    AS restaurants,
    COUNT(*)                                                         AS initial_inspections,
    ROUND(AVG(score), 1)                                             AS avg_initial_score,
    ROUND(100.0 * AVG(score >= 28), 1)                               AS pct_c_range,
    ROUND(100.0 * AVG(closed), 2)                                    AS pct_closed
FROM inspections
WHERE is_initial_cycle = 1 AND score IS NOT NULL
GROUP BY cuisine
HAVING COUNT(*) >= 300
ORDER BY avg_initial_score DESC;
