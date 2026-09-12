import uuid
from uuid import UUID
from datetime import date, datetime

from sqlalchemy import (
    ForeignKey, Date, Boolean, String, Text, Uuid,
    UniqueConstraint, 
    DateTime, func,
    Enum,
    )
from sqlalchemy.orm import Mapped, mapped_column

from src.services.ualosses.models import DatePrecision

from src.models.db import Base


DATE_PRECISION_ENUM = Enum(
    DatePrecision,
    name="date_precision",
)

class Place(Base):
    __tablename__ = "places"

    __table_args__ = (
        UniqueConstraint(
            "name",
            "url",
            name="uq_places_name_url",
            postgresql_nulls_not_distinct=True,
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    url: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


# Location consist of up to 4 Places 
class Location(Base):
    __tablename__ = "locations"

    __table_args__ = (
        UniqueConstraint(
            "settlement_id",
            "community_id",
            "district_id",
            "oblast_id",
            name="uq_locations_places",
            postgresql_nulls_not_distinct=True,
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    settlement_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("places.id"),
        nullable=True,
        index=True,
    )

    community_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("places.id"),
        nullable=True,
        index=True,
    )

    district_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("places.id"),
        nullable=True,
        index=True,
    )

    oblast_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("places.id"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class MilitaryUnit(Base):
    __tablename__ = "military_units"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    __table_args__ = (
        UniqueConstraint(
            "name",
            "url",
            name="uq_military_units_name_url",
            postgresql_nulls_not_distinct=True,
        ),
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    url: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


# Sources (url links) to publication, information, etc.
class Source(Base):
    __tablename__ = "sources"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    url: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


# Relation N <---> N between Soldiers and Sources
class SoldierSource(Base):
    __tablename__ = "soldier_sources"

    __table_args__ = (
        UniqueConstraint(
            "soldier_id",
            "source_id",
            name="uq_soldier_sources_soldier_source",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    soldier_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("soldiers.id"),
        nullable=False,
        index=True,
    )

    source_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("sources.id"),
        nullable=False,
        index=True,
    )

    # Primary or Addictional Source
    is_primary_source: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Soldier(Base):
    __tablename__ = "soldiers"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    source_url: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )

    date_of_birth: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    date_of_birth_precision: Mapped[DatePrecision | None] = mapped_column(
        DATE_PRECISION_ENUM,
        nullable=True,
    )

    date_of_disappearance: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    date_of_disappearance_precision: Mapped[DatePrecision | None] = mapped_column(
        DATE_PRECISION_ENUM,
        nullable=True,
    )

    date_of_death: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    date_of_death_precision: Mapped[DatePrecision | None] = mapped_column(
        DATE_PRECISION_ENUM,
        nullable=True,
    )

    date_of_burial: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    date_of_burial_precision: Mapped[DatePrecision | None] = mapped_column(
        DATE_PRECISION_ENUM,
        nullable=True,
    )

    date_of_release_from_captivity: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    date_of_release_from_captivity_precision: Mapped[DatePrecision | None] = mapped_column(
        DATE_PRECISION_ENUM,
        nullable=True,
    )

    conscription: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    posthumous_award_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    posthumous_award_date_precision: Mapped[DatePrecision | None] = mapped_column(
        DATE_PRECISION_ENUM,
        nullable=True,
    )

    posthumous_award_url: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    cause_of_death: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    rank: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    position: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    from_location_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("locations.id"),
        nullable=True,
        index=True,
    )

    disappeared_in_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("locations.id"),
        nullable=True,
        index=True,
    )

    died_in_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("locations.id"),
        nullable=True,
        index=True,
    )

    buried_in_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("locations.id"),
        nullable=True,
        index=True,
    )

    military_unit_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("military_units.id"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
