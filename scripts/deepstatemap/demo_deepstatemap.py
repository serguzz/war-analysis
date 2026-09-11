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