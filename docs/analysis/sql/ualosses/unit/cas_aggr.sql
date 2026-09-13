SELECT
    mu.name AS military_unit_name,
    mu.url AS military_unit_url,

    COUNT(DISTINCT s.id) FILTER (
        WHERE s.date_of_death IS NOT NULL
    ) AS deaths,

    COUNT(DISTINCT s.id) FILTER (
        WHERE s.date_of_disappearance IS NOT NULL
    ) AS disappeared,

    COUNT(DISTINCT s.id) FILTER (
        WHERE
            s.date_of_death IS NOT NULL
            OR s.date_of_disappearance IS NOT NULL
    ) AS total

FROM soldiers s

JOIN military_units mu
    ON mu.id = s.military_unit_id

GROUP BY
    mu.id,
    mu.name,
    mu.url

ORDER BY
    total DESC;