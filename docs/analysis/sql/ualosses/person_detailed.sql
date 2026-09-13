SELECT
    -- Soldier
    s.name,
    s.source_url,
    s.date_of_birth,
    s.date_of_disappearance,

    -- Military unit
    mu.name AS military_unit_name,
    mu.url AS military_unit_url,


    -- FROM LOCATION

    from_settlement.name AS from_settlement_name,
    from_settlement.url AS from_settlement_url,

    from_community.name AS from_community_name,
    from_community.url AS from_community_url,

    from_district.name AS from_district_name,
    from_district.url AS from_district_url,

    from_oblast.name AS from_oblast_name,
    from_oblast.url AS from_oblast_url,


    -- DISAPPEARED IN LOCATION

    disappeared_settlement.name AS disappeared_settlement_name,
    disappeared_settlement.url AS disappeared_settlement_url,

    disappeared_community.name AS disappeared_community_name,
    disappeared_community.url AS disappeared_community_url,

    disappeared_district.name AS disappeared_district_name,
    disappeared_district.url AS disappeared_district_url,

    disappeared_oblast.name AS disappeared_oblast_name,
    disappeared_oblast.url AS disappeared_oblast_url


FROM soldiers s


-- Military unit
LEFT JOIN military_units mu
    ON mu.id = s.military_unit_id


-- FROM LOCATION
LEFT JOIN locations from_location
    ON from_location.id = s.from_location_id

LEFT JOIN places from_settlement
    ON from_settlement.id = from_location.settlement_id

LEFT JOIN places from_community
    ON from_community.id = from_location.community_id

LEFT JOIN places from_district
    ON from_district.id = from_location.district_id

LEFT JOIN places from_oblast
    ON from_oblast.id = from_location.oblast_id


-- DISAPPEARED IN LOCATION
LEFT JOIN locations disappeared_location
    ON disappeared_location.id = s.disappeared_in_id

LEFT JOIN places disappeared_settlement
    ON disappeared_settlement.id = disappeared_location.settlement_id

LEFT JOIN places disappeared_community
    ON disappeared_community.id = disappeared_location.community_id

LEFT JOIN places disappeared_district
    ON disappeared_district.id = disappeared_location.district_id

LEFT JOIN places disappeared_oblast
    ON disappeared_oblast.id = disappeared_location.oblast_id


WHERE s.name LIKE 'Shevchenko Taras%';