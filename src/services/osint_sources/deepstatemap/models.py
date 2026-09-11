from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass
class DeepStateMapSnapshot:
    date: date
    geojson: dict[str, Any]