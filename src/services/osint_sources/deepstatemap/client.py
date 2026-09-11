from datetime import date
from typing import Any

import requests

from src.services.osint_sources.deepstatemap.config import (
    BASE_URL,
    FILE_NAME_TEMPLATE,
    REQUEST_TIMEOUT,
)

from .exceptions import (
    DeepStateMapClientError,
    DeepStateMapNotFound,
)

class DeepStateMapClient:

    def get_geojson(
        self,
        snapshot_date: date,
    ) -> dict[str, Any]:

        url = self._build_url(snapshot_date)

        try:
            response = requests.get(
                url,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()

        except requests.HTTPError as exc:
            if response.status_code == 404:
                raise DeepStateMapNotFound(
                    f"Snapshot not found for date {snapshot_date}"
                ) from exc

            raise DeepStateMapClientError(
                f"HTTP {response.status_code} for {url}"
            ) from exc

        except requests.RequestException as exc:
            raise DeepStateMapClientError(
                f"Request failed for {url}: {exc}"
            ) from exc

        try:
            return response.json()
        except ValueError as exc:
            raise DeepStateMapClientError(
                f"Invalid JSON received from {url}"
            ) from exc


    @staticmethod
    def _build_url(
        snapshot_date: date,
    ) -> str:

        filename = FILE_NAME_TEMPLATE.format(date=snapshot_date)
        return f"{BASE_URL}/{filename}"