import re
from datetime import date

from bs4 import BeautifulSoup

from .client import UALossesClient


class UALossesParser:
    def __init__(self, client: UALossesClient | None = None) -> None:
        self.client = client or UALossesClient()

    def get_people_count(
        self,
        date_from: date,
        date_to: date,
    ) -> int:
        html = self.client.get_soldiers_page(
            date_from=date_from.strftime("%d.%m.%Y"),
            date_to=date_to.strftime("%d.%m.%Y"),
        )

        soup = BeautifulSoup(html, "html.parser")

        return self._parse_people_count(soup)

    @staticmethod
    def _parse_people_count(soup: BeautifulSoup) -> int:
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