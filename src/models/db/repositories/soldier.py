from sqlalchemy.orm import Session
from sqlalchemy import select

from src.models.db.models import Soldier

from .base import BaseRepository


class SoldierRepository(BaseRepository[Soldier]):

    def __init__(self, session: Session):
        super().__init__(Soldier, session)

    def get_by_source_url(self, url: str) -> Soldier | None:
        statement = (
            select(Soldier)
            .where(
                Soldier.source_url == url
            )
        )
        return self.session.execute(statement).scalar_one_or_none()