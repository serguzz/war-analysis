from datetime import date

import pytest

from src.services.osint_sources.ualosses.models import DatePrecision
from src.utils.parser_utils import parse_optional_date, parse_date


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
    parse_optional_date(text) == (
        expected_date,
        expected_precision,
    )