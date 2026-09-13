select count(*) as PLACES_COUNT from places;

select count(*) as LOCATIONS_COUNT from locations;

select count(*) as OBLAST_COUNT from places where id in (select oblast_id from locations);

select count(*) as SETTLEMENTS_COUNT from places where id in (select settlement_id from locations);

select count(*) as COMMUNITIES_COUNT from places where id in (select community_id from locations);

select count(*) as DISTRICTS_COUNT from places where id in (select district_id from locations);
