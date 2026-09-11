from datetime import date
from typing import Any

import requests

from src.services.osint_sources.deepstatemap.config import (
    BASE_URL,
    FILE_NAME_TEMPLATE,
    REQUEST_TIMEOUT,
)


class DeepStateMapClient:

    def get_geojson(
        self,
        snapshot_date: date,
    ) -> dict[str, Any]:

        url = self._build_url(snapshot_date)

        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        return response.json()

    @staticmethod
    def _build_url(
        snapshot_date: date,
    ) -> str:

        filename = FILE_NAME_TEMPLATE.format(
            date=snapshot_date,
        )

        return f"{BASE_URL}/{filename}"