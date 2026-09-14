from datetime import date

import pytest

from src.services.osint_sources.ualosses.models import DatePrecision, SoldierListItem
from src.utils.parser_utils import parse_optional_date
from src.services.osint_sources.ualosses.parser import parse_soldier_url


@pytest.mark.parametrize(
    ("text", "expected_date", "expected_precision"),
    [
        # Unknown date.
        ("?", None, None),

        # Full month name.
        (
            "March 4, 2000",
            date(2000, 3, 4),
            DatePrecision.DAY,
        ),

        # Abbreviated month.
        (
            "Jan. 23, 1999",
            date(1999, 1, 23),
            DatePrecision.DAY,
        ),
        (
            "Dec. 2, 1989",
            date(1989, 12, 2),
            DatePrecision.DAY,
        ),

        # UA Losses uses "Sept.".
        (
            "Sept. 8, 2024",
            date(2024, 9, 8),
            DatePrecision.DAY,
        ),

        # Parentheses.
        (
            "(March 6, 2025)",
            date(2025, 3, 6),
            DatePrecision.DAY,
        ),
        (
            "(April 16, 2026)",
            date(2026, 4, 16),
            DatePrecision.DAY,
        ),

        # Whitespace.
        (
            "  July 19, 2025  ",
            date(2025, 7, 19),
            DatePrecision.DAY,
        ),

        # Year only.
        (
            "2025",
            date(2025, 1, 1),
            DatePrecision.YEAR,
        ),
    ],
)
def test_parse_optional_date(
    text: str,
    expected_date: date | None,
    expected_precision: DatePrecision | None,
) -> None:
    assert parse_optional_date(text) == (
        expected_date,
        expected_precision,
    )


@pytest.mark.parametrize(
    ("url", "full_name", "last_name", "date_of_birth", "country"),
    [
        (
            "https://ualosses.org/en/soldier/ankhel-armando-isko-andrade-liam-1998-06-26-26-colombia/",
            "Ankhel Armando Isko Andrade Liam",
            "Ankhel",
            date(1998, 6, 26),
            "Colombia",
        ),

        (
            "https://ualosses.org/en/soldier/alvarez-ariza-alvaro-antonio-1988-05-03-35-colombia/",
            "Alvarez Ariza Alvaro Antonio",
            "Alvarez",
            date(1988, 5, 3),
            "Colombia",
        ),

        (
            "https://ualosses.org/en/soldier/askerov-faik-takhir-azerbaijan/",
            "Askerov Faik Takhir",
            "Askerov",
            None,
            "Azerbaijan",
        ),
    ],
)
def test_parse_soldier_url(
    url: str,
    full_name: str,
    last_name: str | None,
    date_of_birth: date | None,
    country: str | None,
) -> None:
    assert parse_soldier_url(url) == SoldierListItem(
        url=url,
        full_name=full_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        country=country,
    )