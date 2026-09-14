import re
from datetime import date, datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from src.config.countries import COUNTRIES

from .client import UALossesClient
from .models import (
    DatePrecision,
    Location,
    Place,
    Soldier,
    MilitaryUnit,
    SoldierListItem
)
from .config import BASE_URL
from src.utils.parser_utils import parse_date, parse_optional_date

class UALossesParser:
    
    def __init__(self, client: UALossesClient | None = None) -> None:
        self.client = client or UALossesClient()

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
            date_of_death=None
            country=None

            parent_item = link.find_parent("li")
            if parent_item is not None:
                for text in parent_item.stripped_strings:
                    if " - " in text:
                        date_of_birth, _, date_of_death, _ = self._parse_listing_dates(text)

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
                    date_of_death=date_of_death,
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
