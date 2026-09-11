from datetime import date
from typing import Any

from .models import (
    DeepStateMapSnapshot,
)

from .exceptions import (
    DeepStateMapParseError,
)

class DeepStateMapParser:

    def parse(
        self,
        snapshot_date: date,
        data: dict[str, Any],
    ) -> DeepStateMapSnapshot:

        if not isinstance(data, dict):
            raise DeepStateMapParseError(
                "Expected GeoJSON data to be a dictionary"
            )

        return DeepStateMapSnapshot(
            date=snapshot_date,
            geojson=data,
        )