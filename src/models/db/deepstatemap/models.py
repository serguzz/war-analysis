from datetime import date, datetime
import uuid
from uuid import UUID

from geoalchemy2 import Geometry
from sqlalchemy import Date, DateTime, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.db import Base


class DeepStateMapGeoData(Base):
    __tablename__ = "deepstatemap_geo_data"

    __table_args__ = (
        UniqueConstraint(
            "snapshot_date",
            name="uq_deepstatemap_geo_data_snapshot_date",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    snapshot_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    geometry: Mapped[object] = mapped_column(
        Geometry(
            geometry_type="MULTIPOLYGON",
            srid=4326,
        ),
        nullable=False,
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