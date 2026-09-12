import argparse
from dataclasses import dataclass
from datetime import date, timedelta

from geoalchemy2.shape import from_shape
from shapely.geometry import shape

from src.models.db.database import SessionLocal
from src.models.db.deepstatemap.repository import DeepStateMapGeoDataRepository
from src.services.osint_sources.deepstatemap.exceptions import DeepStateMapNotFound
from src.services.osint_sources.deepstatemap.service import DeepStateMapService

@dataclass
class ImportStats:
    processed: int = 0
    created: int = 0
    updated: int = 0
    not_found: int = 0
    errors: int = 0


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date: {value}. Expected YYYY-MM-DD."
        ) from exc


def import_snapshot(
    snapshot_date: date,
    service: DeepStateMapService,
    repository: DeepStateMapGeoDataRepository,
) -> str:
    print(f"Importing DeepStateMap snapshot: {snapshot_date}")

    try:
        snapshot = service.get_snapshot(snapshot_date)
    except DeepStateMapNotFound:
        print(f"Not found: {snapshot_date}")
        return "not_found"

    geometry = shape(snapshot.geometry)

    if geometry.geom_type != "MultiPolygon":
        raise ValueError(
            f"Expected MultiPolygon, got {geometry.geom_type}"
        )

    geometry_db = from_shape(geometry, srid=4326)

    existing = repository.get_by_date(snapshot_date)

    if existing is not None:
        repository.update(
            geo_data=existing,
            geometry=geometry_db,
        )

        print(f"Updated successfully: {snapshot_date}")
        return "updated"

    repository.create(
        snapshot_date=snapshot_date,
        geometry=geometry_db,
    )

    print(f"Imported successfully: {snapshot_date}")
    return "created"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import historical DeepStateMap snapshots into PostgreSQL."
    )

    date_group = parser.add_mutually_exclusive_group(required=True)

    date_group.add_argument(
        "--date",
        type=parse_date,
        help="Import one snapshot, e.g. 2024-07-08.",
    )

    date_group.add_argument(
        "--date-from",
        type=parse_date,
        help="Start date for historical import.",
    )

    parser.add_argument(
        "--date-to",
        type=parse_date,
        help="End date for historical import.",
    )

    args = parser.parse_args()

    if args.date_from is not None and args.date_to is None:
        parser.error("--date-to is required with --date-from")

    if args.date_to is not None and args.date_from is None:
        parser.error("--date-from is required with --date-to")

    if (
        args.date_from is not None
        and args.date_to is not None
        and args.date_from > args.date_to
    ):
        parser.error("--date-from must be before or equal to --date-to")

    if args.date is not None:
        dates = [args.date]
    else:
        dates = (
            args.date_from + timedelta(days=i)
            for i in range(
                (args.date_to - args.date_from).days + 1
            )
        )

    service = DeepStateMapService()
    stats = ImportStats()

    with SessionLocal() as session:
        repository = DeepStateMapGeoDataRepository(session)

        for snapshot_date in dates:
            stats.processed += 1

            try:
                result = import_snapshot(
                    snapshot_date=snapshot_date,
                    service=service,
                    repository=repository,
                )

                if result == "created":
                    stats.created += 1

                elif result == "updated":
                    stats.updated += 1

                elif result == "not_found":
                    stats.not_found += 1

                session.commit()

            except Exception as exc:
                session.rollback()

                stats.errors += 1

                print(
                    f"ERROR: {snapshot_date}: "
                    f"{type(exc).__name__}: {exc}"
                )

    print()
    print("Import completed.")
    print(f"Processed:  {stats.processed}")
    print(f"Created:    {stats.created}")
    print(f"Updated:    {stats.updated}")
    print(f"Not found:  {stats.not_found}")
    print(f"Errors:     {stats.errors}")


if __name__ == "__main__":
    main()
