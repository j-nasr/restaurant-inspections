-- How do boroughs compare? Scores use initial cycle inspections only (lower score = cleaner).
-- NYC grade bands: A = 0-13 points, B = 14-27, C = 28+.
SELECT
    borough,
    COUNT(DISTINCT restaurant_id)                                              AS restaurants,
    SUM(is_initial_cycle)                                                      AS initial_inspections,
    ROUND(AVG(CASE WHEN is_initial_cycle = 1 THEN score END), 1)               AS avg_initial_score,
    ROUND(100.0 * AVG(CASE WHEN is_initial_cycle = 1 THEN score <= 13 END), 1) AS pct_initial_in_a_range,
    ROUND(100.0 * AVG(CASE WHEN is_initial_cycle = 1 THEN has_critical END), 1) AS pct_initial_with_critical,
    ROUND(100.0 * SUM(closed) / COUNT(*), 2)                                   AS closures_per_100_inspections
FROM inspections
WHERE borough <> 'Unknown'
GROUP BY borough
ORDER BY avg_initial_score DESC;
