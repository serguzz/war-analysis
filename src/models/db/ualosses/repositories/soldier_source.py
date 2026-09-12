from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.db.ualosses import SoldierSource

from .base import BaseRepository


class SoldierSourceRepository(BaseRepository[SoldierSource]):

    def __init__(self, session: Session):
        super().__init__(SoldierSource, session)

    def get_by_soldier_and_source(
        self,
        soldier_id: UUID,
        source_id: UUID,
    ) -> SoldierSource | None:
        statement = (
            select(SoldierSource)
            .where(
                SoldierSource.soldier_id == soldier_id,
                SoldierSource.source_id == source_id,
            )
        )

        return self.session.execute(statement).scalar_one_or_none()

    # gets all sources for a soldier
    def get_by_soldier(
        self,
        soldier_id: UUID,
    ) -> list[SoldierSource]:
        statement = (
            select(SoldierSource)
            .where(
                SoldierSource.soldier_id == soldier_id
            )
        )
        return list(
            self.session.execute(statement)
            .scalars()
            .all()
        )