-- Monthly trend in initial inspection scores and closures
SELECT
    month,
    SUM(is_initial_cycle)                                          AS initial_inspections,
    ROUND(AVG(CASE WHEN is_initial_cycle = 1 THEN score END), 1)   AS avg_initial_score,
    SUM(closed)                                                    AS closures
FROM inspections
GROUP BY month
ORDER BY month;
