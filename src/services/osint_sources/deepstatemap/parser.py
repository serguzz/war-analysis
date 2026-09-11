from datetime import date
from typing import Any

from .models import DeepStateMapSnapshot
from .validator import DeepStateMapValidator

class DeepStateMapParser:
    def __init__(self):
        self.validator = DeepStateMapValidator()

    def parse(
        self,
        snapshot_date: date,
        data: dict[str, Any],
    ) -> DeepStateMapSnapshot:
        self.validator.validate(
            snapshot_date=snapshot_date,
            data=data,
        )

        geometry = data["features"][0]["geometry"]

        return DeepStateMapSnapshot(
            date=snapshot_date,
            geometry=geometry,
        )