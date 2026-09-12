import argparse
from datetime import date, timedelta

from geoalchemy2.shape import from_shape
from shapely.geometry import shape

from src.models.db.database import SessionLocal
from src.models.db.deepstatemap.repository import DeepStateMapGeoDataRepository
from src.services.osint_sources.deepstatemap.exceptions import DeepStateMapNotFound
from src.services.osint_sources.deepstatemap.service import DeepStateMapService


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
) -> None:
    print(f"Importing DeepStateMap snapshot: {snapshot_date}")

    try:
        snapshot = service.get_snapshot(snapshot_date)
    except DeepStateMapNotFound:
        print(f"Snapshot not found: {snapshot_date}")
        return

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
    else:
        repository.create(
            snapshot_date=snapshot_date,
            geometry=geometry_db,
        )
        print(f"Imported successfully: {snapshot_date}")


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

    service = DeepStateMapService()

    with SessionLocal() as session:
        repository = DeepStateMapGeoDataRepository(session)

        try:
            if args.date is not None:
                import_snapshot(
                    snapshot_date=args.date,
                    service=service,
                    repository=repository,
                )

            else:
                current_date = args.date_from

                while current_date <= args.date_to:
                    import_snapshot(
                        snapshot_date=current_date,
                        service=service,
                        repository=repository,
                    )

                    current_date += timedelta(days=1)

            session.commit()

        except Exception:
            session.rollback()
            raise


if __name__ == "__main__":
    main()