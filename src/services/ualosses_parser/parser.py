import re
from datetime import date
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

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        return self._parse_soldier(soup)

    def _parse_soldier(
        self,
        soup: BeautifulSoup,
    ) -> Soldier:
        raise NotImplementedError

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