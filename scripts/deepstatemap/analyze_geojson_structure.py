import random
from datetime import date, timedelta

from src.services.osint_sources.deepstatemap.client import DeepStateMapClient
from src.services.osint_sources.deepstatemap.config import (
    FILE_NAME_TEMPLATE,
    FIRST_AVAILABLE_DATE,
)
from src.services.osint_sources.deepstatemap.exceptions import (
    DeepStateMapNotFound,
)


SAMPLE_SIZE = 15


def get_random_dates(
    date_from: date,
    date_to: date,
    sample_size: int,
) -> list[date]:
    total_days = (date_to - date_from).days + 1

    if sample_size > total_days:
        raise ValueError(
            "Sample size cannot be larger than the date range"
        )

    offsets = random.sample(
        range(total_days),
        sample_size,
    )

    return sorted(
        date_from + timedelta(days=offset)
        for offset in offsets
    )


def main():
    client = DeepStateMapClient()

    dates = get_random_dates(
        date_from=FIRST_AVAILABLE_DATE,
        date_to=date.today(),
        sample_size=SAMPLE_SIZE,
    )

    snapshots = []

    print(f"Selected dates: {len(dates)}")
    print()

    for snapshot_date in dates:
        try:
            data = client.get_geojson(snapshot_date)

            snapshots.append(
                (
                    snapshot_date,
                    data,
                )
            )

            print(
                f"{snapshot_date} - loaded"
            )

        except DeepStateMapNotFound:
            print(
                f"{snapshot_date} - not found"
            )

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)

    analyze_snapshots(snapshots)


def analyze_snapshots(snapshots):
    if not snapshots:
        print("No snapshots loaded")
        return

    analyze_root_fields(snapshots)
    analyze_names(snapshots)
    analyze_crs(snapshots)
    analyze_features(snapshots)


def analyze_root_fields(snapshots):
    print()
    print("ROOT FIELDS")
    print("-" * 60)

    all_keys = set()

    for _, data in snapshots:
        all_keys.update(data.keys())

    for key in sorted(all_keys):
        values = []
        present_count = 0

        for _, data in snapshots:
            if key in data:
                present_count += 1

                if key != "features":
                    values.append(
                        repr(data[key])
                    )

        print()
        print(f"Field: {key}")
        print(
            f"Present: "
            f"{present_count}/{len(snapshots)}"
        )

        if key == "features":
            print(
                "Value: analyzed separately"
            )
            continue

        unique_values = set(values)

        print(
            f"Unique values: "
            f"{len(unique_values)}"
        )

        if len(unique_values) <= 5:
            for value in unique_values:
                print(f"  {value}")


def analyze_names(snapshots):
    print()
    print("=" * 60)
    print("NAME")
    print("-" * 60)

    mismatches = 0

    for snapshot_date, data in snapshots:
        expected_name = FILE_NAME_TEMPLATE.format(
            date=snapshot_date,
        ).removesuffix(".geojson")

        actual_name = data.get("name")

        matches = actual_name == expected_name

        if not matches:
            mismatches += 1

        print(
            f"{snapshot_date} | "
            f"expected={expected_name} | "
            f"actual={actual_name} | "
            f"match={matches}"
        )

    print()
    print(
        f"Name mismatches: "
        f"{mismatches}/{len(snapshots)}"
    )


def analyze_crs(snapshots):
    print()
    print("=" * 60)
    print("CRS")
    print("-" * 60)

    values = []
    missing_count = 0

    for _, data in snapshots:
        crs = data.get("crs")

        if crs is None:
            missing_count += 1
            continue

        values.append(
            repr(crs)
        )

    unique_values = set(values)

    print(
        f"Present: "
        f"{len(values)}/{len(snapshots)}"
    )

    print(
        f"Missing: {missing_count}"
    )

    print(
        f"Unique CRS values: "
        f"{len(unique_values)}"
    )

    for value in unique_values:
        print(value)


def analyze_features(snapshots):
    print()
    print("=" * 60)
    print("FEATURES")
    print("-" * 60)

    feature_counts = []
    feature_types = set()
    properties_values = set()
    geometry_types = set()

    for _, data in snapshots:
        features = data.get(
            "features",
            [],
        )

        feature_counts.append(
            len(features)
        )

        for feature in features:
            feature_types.add(
                feature.get("type")
            )

            properties_values.add(
                repr(
                    feature.get("properties")
                )
            )

            geometry = feature.get(
                "geometry"
            )

            if geometry is not None:
                geometry_types.add(
                    geometry.get("type")
                )

    print(
        f"Feature counts: "
        f"{sorted(set(feature_counts))}"
    )

    print(
        f"Feature types: "
        f"{feature_types}"
    )

    print(
        f"Unique properties values: "
        f"{len(properties_values)}"
    )

    for value in properties_values:
        print(f"  {value}")

    print(
        f"Geometry types: "
        f"{geometry_types}"
    )


if __name__ == "__main__":
    main()