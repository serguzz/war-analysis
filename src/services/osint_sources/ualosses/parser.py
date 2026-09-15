import re
from datetime import date
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from src.config.countries import COUNTRIES, COUNTRY_ALIASES, MAX_COUNTRY_WORDS

from .client import UALossesClient
from .models import (
    DatePrecision,
    Location,
    Place,
    Soldier,
    MilitaryUnit,
    SoldierListItem
)
from .config import BASE_URL, BASE_SOLDIER_URL
from src.utils.parser_utils import parse_date, parse_optional_date, to_slug


def resolve_country(value: str | None) -> str | None:
    """
    Resolve a hyphen- or space-separated slug fragment (e.g. "united-kingdom")
    to a known, canonically-cased country name, or None if it isn't one.

    Country matching is case-insensitive.    
    """
    if not value:
        return None
 
    normalized = value.replace("-", " ").strip().lower()
 
    # Check aliases case-insensitively.
    for alias, country in COUNTRY_ALIASES.items():
        if alias.lower() == normalized:
            return country

    # Check canonical country names case-insensitively.
    for country in COUNTRIES:
        if country.lower() == normalized:
            return country
 
    return None


def split_trailing_country(slug: str) -> tuple[str, str | None]:
    """
    Peel a known country off the end of a hyphenated slug that has no other
    structural marker to anchor the split (no date of birth, no age) - i.e.
    slugs shaped like "name-parts-country".
 
    Tries the last 1..N hyphen-separated tokens, longest first, so
    multi-word countries ("united-kingdom") are recognized before a
    shorter, incorrect single-word match would be considered.
 
    Returns (remaining_name_slug, country_or_None).
    """
    tokens = slug.split("-")
 
    max_words = min(MAX_COUNTRY_WORDS, len(tokens) - 1)
 
    for word_count in range(max_words, 0, -1):
        candidate = "-".join(tokens[-word_count:])
        country = resolve_country(candidate)
 
        if country:
            return "-".join(tokens[:-word_count]), country
 
    return slug, None


def find_military_unit(
    information: str,
    military_units: list[MilitaryUnit],
) -> MilitaryUnit | None:
    for military_unit in sorted(
        military_units,
        key=lambda unit: len(to_slug(unit.name)),
        reverse=True,
    ):
        unit_slug = to_slug(military_unit.name)

        if unit_slug in information:
            return military_unit

    return None


def find_military_rank(
    information: str,
    military_ranks: list[str],
) -> str | None:
    for military_rank in sorted(
        military_ranks,
        key=lambda rank: len(to_slug(rank)),
        reverse=True,
    ):
        rank_slug = to_slug(military_rank)

        if rank_slug in information:
            return military_rank

    return None


def parse_soldier_url(
    url: str,
    military_units: list[MilitaryUnit] | None = None,
    military_ranks: list[str] | None = None,
    ) -> SoldierListItem:
    """
    Parse available soldier information from a UA Losses
    soldier page URL.

    Example:
        https://ualosses.org/en/soldier/
        ankhel-armando-isko-andrade-liam-1998-06-26-26-colombia/

    Returns:
        SoldierListItem with information extracted from the URL.
    """
    if not url.startswith(BASE_SOLDIER_URL):
        raise ValueError(
            f"Unexpected soldier URL: {url}"
        )

    information = url.removeprefix(
        BASE_SOLDIER_URL
    ).strip("/")

    ## Try to parse military unit name
    military_unit_name = None

    if military_units:
        military_unit = find_military_unit(
            information,
            military_units,
        )

        if military_unit:
            military_unit_name = military_unit.name
            information = information.replace(
                to_slug(military_unit.name),
                "",
                1,
            ).strip("-")

    ## Try to parse military rank
    rank = None

    if military_ranks:
        rank = find_military_rank(
            information,
            military_ranks,
        )

        if rank:
            information = information.replace(
                to_slug(rank),
                "",
                1,
            ).strip("-")

    full_name: str
    date_of_birth: date | None = None
    age: int | None = None
    country: str | None = None
 
    # Shape 1: name-YYYY-MM-DD[-age][-country]
    # The date is an unambiguous anchor, so age/country can stay optiona
    match = re.search(
        r"^(?P<name>.+?)-"
        r"(?P<date>\d{4}-\d{2}-\d{2})"
        r"(?:-(?P<age>\d+))?"
        r"(?:-(?P<country>[^/]+))?$",
        information,
    )

    if match:
        full_name = match.group("name").replace("-", " ").title()
        date_of_birth = date.fromisoformat(match.group("date"))
        if match.group("age"):
            age = int(match.group("age"))

        country = resolve_country(match.group("country"))

    else:
        # Shape 2: name-age-country (no date of birth).
        # Age (a run of digits) is the anchor here, so it must be present -
        # otherwise there's nothing to unambiguously separate name from
        # country and we fall through to shape 3.
        match = re.search(
            r"^(?P<name>.+?)-"
            r"(?P<age>\d+)-"
            r"(?P<country>[^/]+)$",
            information,
        )

        if match:
            full_name = match.group("name").replace("-", " ").title()
            age = int(match.group("age"))
            country = resolve_country(match.group("country"))

        else:
            # Shape 3: no date, no age - just name[-country]. No structural
            # anchor exists, so we peel a known country off the end instead.
            name_slug, country = split_trailing_country(information)
            full_name = name_slug.replace("-", " ").title()

    last_name = (
        full_name.split(maxsplit=1)[0]
        if full_name
        else None
    )

    return SoldierListItem(
        url=url,
        full_name=full_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        country=country,
        military_unit_name=military_unit_name,
        rank=rank,
        age=age,
    )


class UALossesParser:
    
    def __init__(
        self,
        client: UALossesClient | None = None,
        military_units: list[MilitaryUnit] | None = None,  # list of military units
        military_ranks: list | None = None, # list of possible ranks
        ) -> None:
        self.client = client or UALossesClient()
        self.military_units = military_units or []
        self.military_ranks = military_ranks or []

    def get_people_count(
        self,
        date_from: date,
        date_to: date,
    ) -> int:
        """
        Get the number of people who died in the specified date range.
        Args:
            date_from: The start date to get the number of people from.
            date_to: The end date to get the number of people from.
        Returns:
            The number of people who died in the specified date range.
        """
        html = self.client.get_soldiers_date_range(
            date_from=date_from.strftime("%d.%m.%Y"),
            date_to=date_to.strftime("%d.%m.%Y"),
        )

        soup = BeautifulSoup(html, "html.parser")

        return self._parse_people_count(soup)

    def get_found_count(
        self,
        last_name: str | None = None,
    ) -> int:
        """
        Get the number of people found by the last name filter.
        Args:
            last_name: Substring filter for the last name.
        Returns:
            Number of people found.
        """
        html = self.client.get_soldiers_page(
            page=1,
            last_name=last_name,
            sort="last_name",
            direction="asc",
        )
        soup = BeautifulSoup(html, "html.parser")
        
        return self._parse_people_count(soup)


    @staticmethod
    def _parse_people_count(soup: BeautifulSoup) -> int:
        """
        Parse the number of people who died in the specified date range.
        Args:
            soup: The BeautifulSoup object to parse.
        Returns:
            The number of people who died in the specified date range.
        """
        text = soup.get_text(" ", strip=True)

        match = re.search(
            r"Found:\s*([\d,]+)\s+people",
            text,
            re.IGNORECASE,
        )

        if not match:
            raise ValueError(
                "Could not find people count on the UA Losses page."
            )

        return int(match.group(1).replace(",", ""))


    def get_soldiers_listing(
        self,
        page: int,
        last_name: str | None = None,
    ) -> list[SoldierListItem]:
        """
        Get soldiers from a listing page.

        Args:
            page: Listing page number.
            last_name: Substring filter for the last name.

        Returns:
            List of soldier listing items.
        """
        html = self.client.get_soldiers_page(
            page=page,
            last_name=last_name,
            sort="last_name",
            direction="asc",
        )

        soup = BeautifulSoup(html, "html.parser")

        return self.parse_soldiers_listing(soup)


    def get_soldier_urls(
        self,
        page: int = 1,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[str]:
        """
        Get the URLs of the soldiers who died in the specified date range.
        Args:
            page: The page number to get the URLs from.
            date_from: The start date to get the URLs from.
            date_to: The end date to get the URLs from.
        Returns:
            A list of URLs of the soldiers who died in the specified date range.
        """
        html = self.client.get_soldiers_page(
            page=page,
            date_from=(
                date_from.strftime("%d.%m.%Y")
                if date_from
                else None
            ),
            date_to=(
                date_to.strftime("%d.%m.%Y")
                if date_to
                else None
            ),
        )

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        urls = []

        for link in soup.select("a[href]"):
            href = link.get("href")

            if not href:
                continue

            if "/en/soldier/" not in href:
                continue

            url = urljoin(
                BASE_URL,
                href,
            )

            if url not in urls:
                urls.append(url)

        return urls


    def parse_soldiers_listing(
        self,
        soup: BeautifulSoup,
    ) -> list[SoldierListItem]:
        """
        Parse soldier items from a listing page.

        Args:
            soup: Listing page BeautifulSoup object.

        Returns:
            List of soldier listing items.
        """
        items: list[SoldierListItem] = []

        for link in soup.select('a[href*="/en/soldier/"]'):

            name_element = link.find("b")
            if name_element is None:
                continue

            full_name = name_element.get_text(
                " ",
                strip=True,
            )
            if not full_name:
                continue

            href = link.get("href")
            if not href:
                continue
            
            date_of_birth=None
            date_of_birth_precision=None
            date_of_death=None
            date_of_death_precision=None
            country=None

            parent_item = link.find_parent("li")
            if parent_item is not None:
                for text in parent_item.stripped_strings:
                    if " - " in text:
                        (
                            date_of_birth,
                            date_of_birth_precision,
                            date_of_death,
                            date_of_death_precision
                        ) = self._parse_listing_dates(text)

                    elif text in COUNTRIES:
                        country = text

            items.append(
                SoldierListItem(
                    full_name=full_name,
                    url=urljoin(
                        BASE_URL,
                        href,
                    ),
                    date_of_birth=date_of_birth,
                    date_of_birth_precision=date_of_birth_precision,
                    date_of_death=date_of_death,
                    date_of_death_precision=date_of_death_precision,
                    country=country,
                )
            )

        return items


    def get_soldier(
        self,
        url: str,
    ) -> Soldier:
        """
        Get the soldier's information from the specified URL.
        Args:
            url: The URL of the soldier to get the information from.
        Returns:
            The soldier's information.
        """
        html = self.client.get_soldier_page(url)
        soup = BeautifulSoup(html, "html.parser")
        return self._parse_soldier(url, soup)

    def _parse_soldier(self, url: str, soup: BeautifulSoup) -> Soldier:
        name = self._parse_name(soup)
        posthumous_award_date, posthumous_award_date_precision, posthumous_award_url = self._parse_posthumous_award_fields(
            soup,
            "Posthumous award",
        )

        date_of_birth, date_of_birth_precision = (
            self._parse_date_field(
                soup,
                "Date of birth",
            )
        )

        date_of_death, date_of_death_precision = (
            self._parse_date_field(
                soup,
                "Date of death",
            )
        )        

        date_of_disappearance, date_of_disappearance_precision = (
            self._parse_date_field(
                soup,
                "Date of disappearance",
            )
        )        

        date_of_release_from_captivity, date_of_release_from_captivity_precision = (
            self._parse_date_field(
                soup,
                "Date of release from captivity",
            )
        )

        date_of_burial, date_of_burial_precision = (
            self._parse_date_field(
                soup,
                "Date of burial",
            )
        )

        return Soldier(
            source_url=url,
            name=name,
            date_of_birth=date_of_birth,
            date_of_birth_precision=date_of_birth_precision,
            date_of_death=date_of_death,
            date_of_death_precision=date_of_death_precision,
            date_of_disappearance=date_of_disappearance,
            date_of_disappearance_precision=date_of_disappearance_precision,
            date_of_release_from_captivity=date_of_release_from_captivity,
            date_of_release_from_captivity_precision=date_of_release_from_captivity_precision,
            date_of_burial=date_of_burial,
            date_of_burial_precision=date_of_burial_precision,
            conscription=self._parse_text_field(
                soup,
                "Conscription",
            ),
            cause_of_death=self._parse_text_field(
                soup,
                "Cause of death",
            ),
            position=self._parse_text_field(
                soup,
                "Position",
            ),
            from_location=self._parse_location_field(
                soup,
                "From",
            ),
            died_in=self._parse_location_field(
                soup,
                "Died in the area of",
            ),
            disappeared_in=self._parse_location_field(
                soup,
                "Disappeared in the area of",
            ),
            buried_in=self._parse_location_field(
                soup,
                "Buried in",
            ),
            wounded_location=self._parse_location_field(
                soup,
                "Wounded",
            ),
            rank=self._parse_text_field(
                soup,
                "Rank",
            ),
            posthumous_award_date=posthumous_award_date,
            posthumous_award_date_precision=posthumous_award_date_precision,
            posthumous_award_url=posthumous_award_url,
            military_unit=self._parse_military_unit_field(
                soup,
                "Military Unit",
            ),
            sources=self._parse_sources(
                soup,
                ".soldier-sources",
            ),
            additional_sources=self._parse_sources(
                soup,
                ".additional-sources",
            ),
        )


    def fallback_for_failed_url(self, url: str) -> Soldier | None:
        soldier_item_from_url = parse_soldier_url(
            url,
            self.military_units,
            self.military_ranks
        )
        last_name = soldier_item_from_url.last_name

        if self.get_found_count(last_name) > 100:
            raise ValueError(
                f"More than 1 page found for: {last_name} listing. "
                f"Try narrowing the last_name search."
            )
        
        soldier_list_items = self.get_soldiers_listing(1, soldier_item_from_url.last_name)

        match_soldier = None

        for item in soldier_list_items:
            if item.url == soldier_item_from_url.url:
                match_soldier = item
                break

        if match_soldier is None:
            return None

        # Military Unit taken from URL, since page listings don't display unit
        # military_unit = MilitaryUnit(soldier_item_from_url.military_unit_name)

        military_unit = next(
            (
                unit
                for unit in self.military_units
                if unit.name == soldier_item_from_url.military_unit_name
            ),
            None,
        )

        return Soldier(
            name=match_soldier.full_name,
            source_url=url,
            date_of_birth=match_soldier.date_of_birth,
            date_of_birth_precision=match_soldier.date_of_birth_precision,
            date_of_death=match_soldier.date_of_death,
            date_of_death_precision=match_soldier.date_of_death_precision,
            country=match_soldier.country,
            military_unit=military_unit,
        )


    def _parse_name(self, soup: BeautifulSoup) -> str:
        title = soup.select_one(".soldier-title-block h1")

        if title is None:
            raise ValueError("Could not find soldier name")

        return title.get_text(" ", strip=True)

    def _find_fact_value(
        self,
        soup: BeautifulSoup,
        field_name: str,
    ) -> Tag | None:
        for row in soup.select(".soldier-fact-row"):
            label = row.find("dt")

            if label is None:
                continue

            label_text = label.get_text(" ", strip=True)

            if label_text == field_name:
                return row.find("dd")

        return None

    def _parse_text_field(
        self,
        soup: BeautifulSoup,
        field_name: str,
    ) -> str | None:
        value = self._find_fact_value(soup, field_name)

        if value is None:
            return None

        text = value.get_text(" ", strip=True)

        if not text or text in {"?", "Unknown", "unknown"}:
            return None

        return text

    def _parse_date_field(
        self,
        soup: BeautifulSoup,
        field_name: str,
    ) -> tuple[date | None, DatePrecision | None]:
        value = self._parse_text_field(soup, field_name)

        if value is None:
            return None, None

        return parse_date(value)


    # Parses dates from listing page. Formats include:
    # Jan. 23, 1999 - (Sept. 8, 2024)
    # ? - July 19, 2025
    # March 24, 1998 - ?
    # July 20, 1998 - (May 5, 2025)
    def _parse_listing_dates(
        self,
        value: str,
    ) -> tuple[
        date | None,
        DatePrecision | None,
        date | None,
        DatePrecision | None,
    ]:
        if " - " not in value:
            return None, None, None, None

        birth_value, death_value = value.split(
            " - ",
            maxsplit=1,
        )

        (
            date_of_birth,
            date_of_birth_precision,
        ) = parse_optional_date(birth_value)

        (
            date_of_death,
            date_of_death_precision,
        ) = parse_optional_date(death_value)

        return (
            date_of_birth,
            date_of_birth_precision,
            date_of_death,
            date_of_death_precision,
        )


    def _parse_location_field(
        self,
        soup: BeautifulSoup,
        field_name: str,
    ) -> Location | None:
        value = self._find_fact_value(soup, field_name)

        if value is None:
            return None

        links = value.find_all("a", href=True)

        if not links:
            return None

        places = [
            Place(
                name=link.get_text(" ", strip=True),
                url=urljoin(
                    BASE_URL,
                    link["href"],
                ),
            )
            for link in links
        ]

        location = Location()

        if len(places) > 0:
            location.settlement = places[0]

        if len(places) > 1:
            location.community = places[1]

        if len(places) > 2:
            location.district = places[2]

        if len(places) > 3:
            location.oblast = places[3]

        return location

    def _parse_military_unit_field(
        self,
        soup: BeautifulSoup,
        field_name: str,
    ) -> MilitaryUnit | None:
        value = self._find_fact_value(soup, field_name)

        if value is None:
            return None

        link = value.find("a", href=True)

        if link is None:
            return None

        name = link.get_text(" ", strip=True)

        if not name or name == "Unknown":
            return None

        return MilitaryUnit(
            name=name,
            url=urljoin(
                BASE_URL,
                link["href"],
            ),
        )

    def _parse_posthumous_award_fields(
        self,
        soup: BeautifulSoup,
        field_name: str,
    ) -> tuple[date | None, DatePrecision | None, str | None]:
        value = self._find_fact_value(soup, field_name)

        if value is None:
            return None, None, None

        link = value.find("a", href=True)

        if link is None:
            return None, None, None

        award_date, award_date_precision = parse_date(link.get_text(" ", strip=True))

        award_url = urljoin(
            BASE_URL,
            link["href"],
        )

        return (award_date, award_date_precision, award_url)

    def _parse_sources(
        self,
        soup: BeautifulSoup,
        selector: str,
    ) -> list[str]:
        section = soup.select_one(selector)

        if section is None:
            return []

        return [
            urljoin(
                BASE_URL,
                link["href"],
            )
            for link in section.select("a[href]")
        ]
