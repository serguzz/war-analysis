# Data models for UA Losses parser will be added here

from dataclasses import dataclass
from datetime import date


@dataclass
class Place:
    name: str
    url: str | None = None

@dataclass
class MilitaryUnit:
    name: str # e.g., 25th separate airborne brigade
    url: str | None = None # e.g., https://ualosses.org/en/military_unit/25th-separate-airborne-brigade-a1126/
    # the url also contains unit numeric name: A1126 (a1126)

@dataclass
class Location:
    settlement: Place | None = None
    community: Place | None = None
    district: Place | None = None
    oblast: Place | None = None


@dataclass
class SoldierListItem:
    last_name: str
    url: str


@dataclass
class Soldier:
    name: str

    date_of_birth: date | None = None
    date_of_disappearance: date | None = None
    date_of_death: date | None = None
    date_of_burial: date | None = None
    date_of_release_from_captivity: date | None = None
    conscription: str | None = None

    posthumous_award_date: date | None = None
    posthumous_award_url: str | None = None

    cause_of_death: str | None = None

    from_location: Location | None = None
    disappeared_in: Location | None = None
    died_in: Location | None = None
    buried_in: Location | None = None

    rank: str | None = None
    position: str | None = None
    military_unit: MilitaryUnit | None = None

    sources: list[str] | None = None
    additional_sources: list[str] | None = None