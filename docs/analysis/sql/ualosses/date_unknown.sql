SELECT
    COUNT(*) AS total_soldiers,

    -- Немає жодної з 2 дат
    COUNT(*) FILTER (
        WHERE date_of_disappearance IS NULL
          AND date_of_death IS NULL
    ) AS no_dates,

    -- Є хоча б одна дата з точністю до дня
    COUNT(*) FILTER (
        WHERE date_of_disappearance_precision ='DAY'
           OR date_of_death_precision = 'DAY'
    ) AS day_precision,

    -- Немає жодної DAY, але є хоча б одна MONTH
    COUNT(*) FILTER (
        WHERE NOT (
            date_of_disappearance_precision = 'DAY'
            OR date_of_death_precision = 'DAY'
        )
        AND (
            date_of_disappearance_precision = 'MONTH'
            OR date_of_death_precision = 'MONTH'
        )
    ) AS month_precision_only,

    -- Немає DAY або MONTH, але є YEAR
    COUNT(*) FILTER (
        WHERE NOT (
            date_of_disappearance_precision IN ('DAY', 'MONTH')
            OR date_of_death_precision IN ('DAY', 'MONTH')
        )
        AND (
            date_of_disappearance_precision = 'YEAR'
            OR date_of_death_precision = 'YEAR'
        )
    ) AS year_precision_only

FROM soldiers;