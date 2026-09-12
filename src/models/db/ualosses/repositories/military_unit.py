from sqlalchemy import select
from sqlalchemy.orm import Session

from .base import BaseRepository
from src.models.db.ualosses import MilitaryUnit

class MilitaryUnitRepository(BaseRepository[MilitaryUnit]):

    def __init__(self, session: Session):
        super().__init__(MilitaryUnit, session)

    def get_by_name_and_url(
        self,
        name: str,
        url: str | None,
    ) -> MilitaryUnit | None:
        statement = (
            select(MilitaryUnit)
            .where(
                MilitaryUnit.name == name,
                MilitaryUnit.url == url,
            )
        )
        return self.session.execute(statement).scalar_one_or_none()

    def get_by_url(self, url: str) -> MilitaryUnit | None:
        statement = (
            select(MilitaryUnit)
            .where(MilitaryUnit.url == url)
        )

        return self.session.execute(statement).scalar_one_or_none()