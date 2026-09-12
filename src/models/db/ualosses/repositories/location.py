from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.db.ualosses import Location

from .base import BaseRepository


class LocationRepository(BaseRepository[Location]):

    def __init__(self, session: Session):
        super().__init__(Location, session)

    def get_by_places(
        self,
        settlement_id: UUID | None,
        community_id: UUID | None,
        district_id: UUID | None,
        oblast_id: UUID | None,
    ) -> Location | None:
        statement = (
            select(Location)
            .where(
                Location.settlement_id == settlement_id,
                Location.community_id == community_id,
                Location.district_id == district_id,
                Location.oblast_id == oblast_id,
            )
        )

        return self.session.execute(statement).scalar_one_or_none()