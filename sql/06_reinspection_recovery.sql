-- When a restaurant fails to earn an A on its initial inspection (14+ points),
-- how often does it reach the A range on the re-inspection that follows?
-- The re-inspection must come before the restaurant's next initial inspection (same inspection cycle).
-- Initial inspections after 2026-06-30 are excluded because many have not been re-inspected yet.
WITH failed_initial AS (
    SELECT restaurant_id, inspection_date, score
    FROM inspections
    WHERE inspection_type = 'Cycle Inspection / Initial Inspection'
      AND score >= 14
      AND inspection_date < '2026-07-01'
),
paired AS (
    SELECT
        f.restaurant_id,
        f.score AS initial_score,
        (SELECT r.score
           FROM inspections r
          WHERE r.restaurant_id = f.restaurant_id
            AND r.inspection_type = 'Cycle Inspection / Re-inspection'
            AND r.inspection_date > f.inspection_date
            AND NOT EXISTS (
                SELECT 1 FROM inspections x
                 WHERE x.restaurant_id = f.restaurant_id
                   AND x.inspection_type = 'Cycle Inspection / Initial Inspection'
                   AND x.inspection_date > f.inspection_date
                   AND x.inspection_date < r.inspection_date)
          ORDER BY r.inspection_date
          LIMIT 1) AS reinspection_score
    FROM failed_initial f
)
SELECT
    COUNT(*)                                                         AS initial_inspections_scoring_14_plus,
    COUNT(reinspection_score)                                        AS with_reinspection_in_same_cycle,
    ROUND(AVG(CASE WHEN reinspection_score IS NOT NULL THEN initial_score END), 1) AS avg_initial_score,
    ROUND(AVG(reinspection_score), 1)                                AS avg_reinspection_score,
    ROUND(100.0 * SUM(reinspection_score <= 13) / COUNT(reinspection_score), 1) AS pct_reaching_a_range
FROM paired;
