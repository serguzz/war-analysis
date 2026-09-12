from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.db.ualosses import Source
from .base import BaseRepository


class SourceRepository(BaseRepository[Source]):

    def __init__(self, session: Session):
        super().__init__(Source, session)

    def get_by_url(self, url: str) -> Source | None:
        statement = (
            select(Source)
            .where(Source.url == url)
        )

        return self.session.execute(statement).scalar_one_or_none()