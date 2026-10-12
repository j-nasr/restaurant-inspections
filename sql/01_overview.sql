-- Headline numbers for the whole dataset
SELECT
    COUNT(DISTINCT restaurant_id)                                        AS restaurants,
    COUNT(*)                                                             AS inspections,
    ROUND(100.0 * AVG(has_critical), 1)                                  AS pct_inspections_with_critical,
    SUM(closed)                                                          AS closures,
    ROUND(AVG(CASE WHEN is_initial_cycle = 1 THEN score END), 1)         AS avg_initial_score,
    ROUND(100.0 * SUM(grade = 'A') / SUM(grade IN ('A', 'B', 'C')), 1)   AS pct_a_of_letter_grades
FROM inspections;
