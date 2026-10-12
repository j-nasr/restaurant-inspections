-- The ten most frequently cited violations, and how often they appear
SELECT
    v.violation_code,
    c.critical,
    c.description,
    COUNT(*)                                                                    AS times_cited,
    ROUND(100.0 * COUNT(DISTINCT v.inspection_id) / (SELECT COUNT(*) FROM inspections), 1) AS pct_of_inspections
FROM violations v
JOIN violation_codes c ON c.violation_code = v.violation_code
GROUP BY v.violation_code, c.critical, c.description
ORDER BY times_cited DESC
LIMIT 10;
