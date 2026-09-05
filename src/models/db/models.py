# Example model only
# Edit this before running migrations

from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Record(Base):
    __tablename__ = "records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
"""
    date_died: Mapped[date | None] = mapped_column(Date)
    place_died: Mapped[str | None] = mapped_column(String)
    reason_died: Mapped[str | None] = mapped_column(String)
    name: Mapped[str | None] = mapped_column(String)
    date_birth: Mapped[date | None] = mapped_column(Date)
    date_conscripted: Mapped[date | None] = mapped_column(Date)
    date_retired: Mapped[date | None] = mapped_column(Date)
    brigade: Mapped[str | None] = mapped_column(String)
    brigade_name: Mapped[str | None] = mapped_column(String)
    rank: Mapped[str | None] = mapped_column(String)
"""