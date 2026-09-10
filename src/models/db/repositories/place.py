from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from .base import BaseRepository
from src.models.db.models import Place

class PlaceRepository(BaseRepository[Place]):

    def __init__(self, session: Session):
        super().__init__(Place, session)

    def get_by_name_and_url(
        self,
        name: str,
        url: str | None,
    ) -> Place | None:
        statement = (
            select(Place)
            .where(
                Place.name == name,
                Place.url == url,
            )
        )
        return self.session.execute(statement).scalar_one_or_none()


    def get_by_url(self, url: str) -> Place | None:
        statement = (
            select(Place)
            .where(
                Place.url == url
            )
        )
        return self.session.execute(statement).scalar_one_or_none()