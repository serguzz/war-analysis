import re
from datetime import date, datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .client import UALossesClient
from .models import Location, Place, Soldier, MilitaryUnit


class UALossesParser:
    BASE_URL = "https://ualosses.org"
    
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
                self.BASE_URL,
                href,
            )

            if url not in urls:
                urls.append(url)

        return urls

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
        return self._parse_soldier(soup)

    def _parse_soldier(self, soup: BeautifulSoup) -> Soldier:
        name = self._parse_name(soup)

        return Soldier(
            name=name,
            date_of_birth=self._parse_date_field(
                soup,
                "Date of birth",
            ),
            date_of_death=self._parse_date_field(
                soup,
                "Date of death",
            ),
            date_of_disappearance=self._parse_date_field(
                soup,
                "Date of disappearance",
            ),
            date_of_burial=self._parse_date_field(
                soup,
                "Date of burial",
            ),
            conscription=self._parse_text_field(
                soup,
                "Conscription",
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
            rank=self._parse_text_field(
                soup,
                "Rank",
            ),
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

        if not text or text == "?":
            return None

        return text

    def _parse_date_field(
        self,
        soup: BeautifulSoup,
        field_name: str,
    ) -> date | None:
        value = self._parse_text_field(soup, field_name)

        if value is None:
            return None

        return self._parse_date(value)

    def _parse_date(self, value: str) -> date:
        value = value.strip()
        
        # UA Losses uses "Sept." instead of the standard "Sep."
        if value.startswith("Sept."):
            value = value.replace("Sept.", "Sep.", 1)        
        
        formats = (
            "%B %d, %Y",
            "%b. %d, %Y",
            "%b %d, %Y",
        )

        for fmt in formats:
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue

        raise ValueError(f"Unknown date format: {value}")

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
                    self.BASE_URL,
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
                self.BASE_URL,
                link["href"],
            ),
        )

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
                self.BASE_URL,
                link["href"],
            )
            for link in section.select("a[href]")
        ]
