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
        description="Import DeepStateMap snapshots into PostgreSQL."
    )

    parser.add_argument(
        "--date",
        type=parse_date,
        help="Import one snapshot.",
    )

    parser.add_argument(
        "--date-from",
        type=parse_date,
        help="Start date for import.",
    )

    parser.add_argument(
        "--date-to",
        type=parse_date,
        help="End date for import.",
    )

    parser.add_argument(
        "--update",
        action="store_true",
        help=(
            "Import snapshots from the day after the latest "
            "snapshot in the database up to today."
        ),
    )

    args = parser.parse_args()

    # ---------------------------------------------------------
    # Validate argument combinations
    # ---------------------------------------------------------

    has_single_date = args.date is not None

    has_date_from = args.date_from is not None
    has_date_to = args.date_to is not None

    has_date_range = (
        has_date_from
        or has_date_to
    )

    has_update = args.update

    # --date-from and --date-to must be used together
    if has_date_from and not has_date_to:
        parser.error(
            "--date-to is required with --date-from"
        )

    if has_date_to and not has_date_from:
        parser.error(
            "--date-from is required with --date-to"
        )

    # --date cannot be combined with range
    if has_single_date and has_date_range:
        parser.error(
            "--date cannot be used with "
            "--date-from or --date-to"
        )

    # --update cannot be combined with any other mode
    if has_update and has_single_date:
        parser.error(
            "--update cannot be used with --date"
        )

    if has_update and has_date_range:
        parser.error(
            "--update cannot be used with "
            "--date-from or --date-to"
        )

    # One import mode is required
    if (
        not has_single_date
        and not has_date_range
        and not has_update
    ):
        parser.error(
            "One of the following modes is required: "
            "--date, --date-from with --date-to, or --update"
        )

    # Validate date range
    if (
        has_date_from
        and has_date_to
        and args.date_from > args.date_to
    ):
        parser.error(
            "--date-from must be before or equal to --date-to"
        )

    service = DeepStateMapService()
    stats = ImportStats()

    with SessionLocal() as session:
        repository = DeepStateMapGeoDataRepository(
            session
        )

        # -----------------------------------------------------
        # Determine dates to import
        # -----------------------------------------------------

        if has_single_date:
            dates = [args.date]

        elif has_date_range:
            dates = (
                args.date_from + timedelta(days=i)
                for i in range(
                    (
                        args.date_to
                        - args.date_from
                    ).days
                    + 1
                )
            )

        else:
            today = date.today()

            latest_snapshot_date = (
                repository.get_latest_date()
            )

            if latest_snapshot_date is None:
                print(
                    "No DeepStateMap data found "
                    "in the database."
                )
                return

            print(
                "Latest snapshot date in database: "
                f"{latest_snapshot_date}"
            )

            if latest_snapshot_date >= today:
                print(
                    "DeepStateMap data is already "
                    "up to date."
                )
                return

            date_from = (
                latest_snapshot_date
                + timedelta(days=1)
            )

            date_to = today

            print(
                f"Importing snapshots from "
                f"{date_from} to {date_to}"
            )

            dates = (
                date_from + timedelta(days=i)
                for i in range(
                    (date_to - date_from).days + 1
                )
            )

        # -----------------------------------------------------
        # Import snapshots
        # -----------------------------------------------------

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
