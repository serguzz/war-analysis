from sqlalchemy.orm import Session

from src.models.db.models import (
    Location as DBLocation,
    MilitaryUnit as DBMilitaryUnit,
    Place as DBPlace,
    Soldier as DBSoldier,
    SoldierSource as DBSoldierSource,
    Source as DBSource,
)

from src.services.ualosses_parser.models import (
    Location,
    MilitaryUnit,
    Place,
    Soldier,
)

from src.models.db.repositories import (
    PlaceRepository,
    LocationRepository,
    MilitaryUnitRepository,
    SourceRepository,
    SoldierSourceRepository,
    SoldierRepository
)

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")

@dataclass
class SaveResult(Generic[T]):
    entity: T
    created: bool

    @property
    def updated(self) -> bool:
        return not self.created


class UALossesService:

    def __init__(self, session: Session):
        self.place_repo = PlaceRepository(session)
        self.location_repo = LocationRepository(session)
        self.military_unit_repo = MilitaryUnitRepository(session)
        self.soldier_repo = SoldierRepository(session)
        self.source_repo = SourceRepository(session)
        self.soldier_source_repo = SoldierSourceRepository(session)

        self.session = session


    def _get_or_create_place(
        self,
        place: Place | None,
    ) -> DBPlace | None:
        if place is None:
            return None

        db_place = self.place_repo.get_by_name_and_url(
            name=place.name,
            url=place.url,
        )

        if db_place is not None:
            return db_place

        db_place = self.place_repo.create({
            "name": place.name,
            "url": place.url,
        })

        self.session.flush()
        return db_place


    def _get_or_create_military_unit(
        self,
        unit: MilitaryUnit | None,
    ) -> DBMilitaryUnit | None:
        if unit is None:
            return None

        db_unit = self.military_unit_repo.get_by_name_and_url(
            name=unit.name,
            url=unit.url,
        )

        if db_unit is not None:
            return db_unit

        db_unit = self.military_unit_repo.create({
            "name": unit.name,
            "url": unit.url,
        })

        self.session.flush()
        return db_unit


    def _get_or_create_location(
        self,
        location: Location | None,
    ) -> DBLocation | None:
        if location is None:
            return None

        settlement = self._get_or_create_place(
            location.settlement
        )
        community = self._get_or_create_place(
            location.community
        )
        district = self._get_or_create_place(
            location.district
        )
        oblast = self._get_or_create_place(
            location.oblast
        )

        self.session.flush()

        db_location = self.location_repo.get_by_places(
            settlement_id=settlement.id if settlement else None,
            community_id=community.id if community else None,
            district_id=district.id if district else None,
            oblast_id=oblast.id if oblast else None,
        )

        if db_location is not None:
            return db_location

        db_location = self.location_repo.create({
            "settlement_id": settlement.id if settlement else None,
            "community_id": community.id if community else None,
            "district_id": district.id if district else None,
            "oblast_id": oblast.id if oblast else None,
        })

        return db_location


    def _get_or_create_source(
        self,
        url: str,
    ) -> DBSource:
        db_source = self.source_repo.get_by_url(url)

        if db_source is not None:
            return db_source

        db_source = self.source_repo.create({
            "url": url,
        })

        self.session.flush()
        return db_source


    def _save_sources(
        self,
        db_soldier: DBSoldier,
        soldier: Soldier,
    ) -> None:

        primary_urls = soldier.sources or []
        additional_urls = soldier.additional_sources or []

        sources: dict[str, bool] = {}

        for url in primary_urls:
            if url:
                sources[url] = True

        for url in additional_urls:
            if url and url not in sources:
                sources[url] = False

        current_source_ids = set()

        for url, is_primary in sources.items():
            db_source = self._get_or_create_source(url)

            current_source_ids.add(db_source.id)

            existing = (
                self.soldier_source_repo
                .get_by_soldier_and_source(
                    soldier_id=db_soldier.id,
                    source_id=db_source.id,
                )
            )

            if existing is None:
                self.soldier_source_repo.create({
                    "soldier_id": db_soldier.id,
                    "source_id": db_source.id,
                    "is_primary_source": is_primary,
                })
            else:
                self.soldier_source_repo.update(
                    existing.id,
                    {
                        "is_primary_source": is_primary,
                    },
                )

        existing_links = (
            self.soldier_source_repo
            .get_by_soldier(db_soldier.id)
        )

        for link in existing_links:
            if link.source_id not in current_source_ids:
                self.soldier_source_repo.delete(link.id)


    def save_soldier(self, soldier: Soldier) -> SaveResult[DBSoldier]:
        db_soldier = self.soldier_repo.get_by_source_url(
            soldier.source_url
        )
        is_new = db_soldier is None

        military_unit = self._get_or_create_military_unit(
            soldier.military_unit
        )

        from_location = self._get_or_create_location(
            soldier.from_location
        )

        disappeared_in = self._get_or_create_location(
            soldier.disappeared_in
        )

        died_in = self._get_or_create_location(
            soldier.died_in
        )

        buried_in = self._get_or_create_location(
            soldier.buried_in
        )

        data = {
            "name": soldier.name,
            "date_of_birth": soldier.date_of_birth,
            "date_of_disappearance": soldier.date_of_disappearance,
            "date_of_death": soldier.date_of_death,
            "date_of_burial": soldier.date_of_burial,
            "date_of_release_from_captivity": (
                soldier.date_of_release_from_captivity
            ),
            "conscription": soldier.conscription,
            "posthumous_award_date": soldier.posthumous_award_date,
            "posthumous_award_url": soldier.posthumous_award_url,
            "cause_of_death": soldier.cause_of_death,
            "rank": soldier.rank,
            "position": soldier.position,
            "military_unit_id": (
                military_unit.id if military_unit else None
            ),
            "from_location_id": (
                from_location.id if from_location else None
            ),
            "disappeared_in_id": (
                disappeared_in.id if disappeared_in else None
            ),
            "died_in_id": (
                died_in.id if died_in else None
            ),
            "buried_in_id": (
                buried_in.id if buried_in else None
            ),
        }

        if db_soldier is None:
            data["source_url"] = soldier.source_url

            db_soldier = self.soldier_repo.create(data)

        else:
            db_soldier = self.soldier_repo.update(
                db_soldier.id,
                data,
            )

        self.session.flush()

        self._save_sources(
            db_soldier,
            soldier,
        )

        return SaveResult(entity=db_soldier, created=is_new)


