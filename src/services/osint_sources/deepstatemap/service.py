from datetime import date, timedelta

from .client import DeepStateMapClient
from .models import DeepStateMapSnapshot
from .parser import DeepStateMapParser
from .exceptions import DeepStateMapNotFound

class DeepStateMapService:

    def __init__(self):
        self.client = DeepStateMapClient()
        self.parser = DeepStateMapParser()

    def get_snapshot(
        self,
        snapshot_date: date,
    ) -> DeepStateMapSnapshot:

        data = self.client.get_geojson(
            snapshot_date,
        )

        return self.parser.parse(
            snapshot_date=snapshot_date,
            data=data,
        )

    def get_snapshots(
        self,
        date_from: date,
        date_to: date,
    ) -> list[DeepStateMapSnapshot]:

        snapshots = []

        current_date = date_from

        while current_date <= date_to:
            try:
                snapshot = self.get_snapshot(current_date)
                snapshots.append(snapshot)

            except DeepStateMapNotFound:
                # No data for this date — skip it.
                pass

            current_date += timedelta(days=1)

        return snapshots