WITH weekly_snapshots AS (
    SELECT DISTINCT ON (
        DATE_TRUNC('week', snapshot_date)
    )
        snapshot_date,
        geometry
    FROM deepstatemap_geo_data
    ORDER BY
        DATE_TRUNC('week', snapshot_date),
        snapshot_date
),
weekly_with_previous AS (
    SELECT
        snapshot_date,
        geometry,
        LAG(snapshot_date) OVER (
            ORDER BY snapshot_date
        ) AS previous_snapshot_date,
        LAG(geometry) OVER (
            ORDER BY snapshot_date
        ) AS previous_geometry
    FROM weekly_snapshots
),
last_N_weeks AS (
    SELECT *
    FROM weekly_with_previous
    ORDER BY snapshot_date DESC
    LIMIT 15
)
SELECT
    snapshot_date,

    ROUND(
        (ST_Area(geometry::geography) / 1000000)::numeric,
        2
    ) AS area_km2,

    ROUND(
        (
            ST_Area(
                ST_Difference(
                    previous_geometry,
                    geometry
                )::geography
            ) / 1000000
        )::numeric,
        2
    ) AS deoccupied_km2,

    ROUND(
        (
            ST_Area(
                ST_Difference(
                    geometry,
                    previous_geometry
                )::geography
            ) / 1000000
        )::numeric,
        2
    ) AS occupied_km2,

    ROUND(
        (
            (
                ST_Area(geometry::geography)
                -
                ST_Area(previous_geometry::geography)
            ) / 1000000
        )::numeric,
        2
    ) AS change_km2

FROM last_N_weeks
ORDER BY snapshot_date;