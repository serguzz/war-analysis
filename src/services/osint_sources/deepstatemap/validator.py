from datetime import date
from typing import Any

from src.services.osint_sources.deepstatemap.config import (
    FILE_NAME_TEMPLATE,
)
from src.services.osint_sources.deepstatemap.exceptions import (
    DeepStateMapParseError,
)


class DeepStateMapValidator:
    EXPECTED_GEOJSON_TYPE = "FeatureCollection"
    EXPECTED_FEATURE_TYPE = "Feature"
    EXPECTED_GEOMETRY_TYPE = "MultiPolygon"

    EXPECTED_CRS = {
        "type": "name",
        "properties": {
            "name": "urn:ogc:def:crs:OGC:1.3:CRS84",
        },
    }

    def validate(
        self,
        snapshot_date: date,
        data: dict[str, Any],
    ) -> None:
        self._validate_root(data)
        self._validate_name(snapshot_date, data)
        self._validate_crs(data)
        self._validate_features(data)

    def _validate_root(
        self,
        data: dict[str, Any],
    ) -> None:
        if not isinstance(data, dict):
            raise DeepStateMapParseError(
                "Expected GeoJSON data to be a dictionary"
            )

        if data.get("type") != self.EXPECTED_GEOJSON_TYPE:
            raise DeepStateMapParseError(
                f"Unexpected GeoJSON type: "
                f"{data.get('type')!r}"
            )

    def _validate_name(
        self,
        snapshot_date: date,
        data: dict[str, Any],
    ) -> None:
        expected_name = FILE_NAME_TEMPLATE.format(
            date=snapshot_date,
        ).removesuffix(".geojson")

        actual_name = data.get("name")

        if actual_name != expected_name:
            raise DeepStateMapParseError(
                f"Unexpected GeoJSON name: "
                f"expected {expected_name!r}, "
                f"got {actual_name!r}"
            )

    def _validate_crs(
        self,
        data: dict[str, Any],
    ) -> None:
        if data.get("crs") != self.EXPECTED_CRS:
            raise DeepStateMapParseError(
                "Unexpected CRS"
            )

    def _validate_features(
        self,
        data: dict[str, Any],
    ) -> None:
        features = data.get("features")

        if not isinstance(features, list):
            raise DeepStateMapParseError(
                "Expected 'features' to be a list"
            )

        if len(features) != 1:
            raise DeepStateMapParseError(
                f"Expected exactly one feature, "
                f"got {len(features)}"
            )

        feature = features[0]

        if not isinstance(feature, dict):
            raise DeepStateMapParseError(
                "Expected feature to be a dictionary"
            )

        if feature.get("type") != self.EXPECTED_FEATURE_TYPE:
            raise DeepStateMapParseError(
                f"Unexpected feature type: "
                f"{feature.get('type')!r}"
            )

        geometry = feature.get("geometry")

        if not isinstance(geometry, dict):
            raise DeepStateMapParseError(
                "Expected 'geometry' to be a dictionary"
            )

        if geometry.get("type") != self.EXPECTED_GEOMETRY_TYPE:
            raise DeepStateMapParseError(
                f"Unexpected geometry type: "
                f"{geometry.get('type')!r}"
            )

        if "coordinates" not in geometry:
            raise DeepStateMapParseError(
                "Geometry does not contain coordinates"
            )