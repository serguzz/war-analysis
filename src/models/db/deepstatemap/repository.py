from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    DeepStateMapGeoData,
)


class DeepStateMapGeoDataRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_by_date(
        self,
        snapshot_date: date,
    ) -> DeepStateMapGeoData | None:
        stmt = select(DeepStateMapGeoData).where(
            DeepStateMapGeoData.snapshot_date == snapshot_date
        )

        return self.session.scalar(stmt)

    def create(
        self,
        snapshot_date: date,
        geometry: Any,
    ) -> DeepStateMapGeoData:

        geo_data = DeepStateMapGeoData(
            snapshot_date=snapshot_date,
            geometry=geometry,
        )

        self.session.add(geo_data)
        self.session.flush()

        return geo_data