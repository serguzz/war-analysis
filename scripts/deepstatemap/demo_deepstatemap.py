from datetime import date

from src.services.osint_sources.deepstatemap.service import (
    DeepStateMapService,
)


service = DeepStateMapService()


snapshot = service.get_snapshot(
    date(2024, 7, 8),
)


print(f"Date: {snapshot.date}")

print("\nGeoJSON keys:")

for key in snapshot.geojson:
    print(f"- {key}")

print("\nFull GeoJSON:")
print(snapshot.geojson)


snapshots = service.get_snapshots(
    date_from=date(2024, 7, 8),
    date_to=date(2024, 7, 10),
)

for snapshot in snapshots:

    print(
        f"{snapshot.date}: "
        f"{snapshot.geojson.get('type')}"
    )