from datetime import date

import pytest

from src.services.osint_sources.ualosses.models import (
    DatePrecision, SoldierListItem, MilitaryUnit
)
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
    (
        "url",
        "full_name",
        "last_name",
        "date_of_birth",
        "country",
        "military_unit_name",
        "rank",
        "age",
    ),
[
    (
        "https://ualosses.org/en/soldier/testname-one-1981-04-17-66-colombia/",
        "Testname One",
        "Testname",
        date(1981, 4, 17),
        "Colombia",
        None,
        None,
        66,
    ),

    (
        "https://ualosses.org/en/soldier/example-novak-1974-11-03-35-colombia/",
        "Example Novak",
        "Example",
        date(1974, 11, 3),
        "Colombia",
        None,
        None,
        35,
    ),

    (
        "https://ualosses.org/en/soldier/alex-demo-person-azerbaijan/",
        "Alex Demo Person",
        "Alex",
        None,
        "Azerbaijan",
        None,
        None,
        None,
    ),

    (
        "https://ualosses.org/en/soldier/tester-ivan-example-colombia/",
        "Tester Ivan Example",
        "Tester",
        None,
        "Colombia",
        None,
        None,
        None,
    ),

    (
        "https://ualosses.org/en/soldier/demo-markus-1989-02-21-33-united-kingdom-soldier/",
        "Demo Markus",
        "Demo",
        date(1989, 2, 21),
        "United Kingdom",
        None,
        "Soldier",
        33,
    ),

    (
        "https://ualosses.org/en/soldier/example-andrew-33-sri-lanka-4th-international-legion-junior-sergeant/",
        "Example Andrew",
        "Example",
        None,
        "Sri Lanka",
        "4th International Legion",
        "Junior sergeant",
        33,
    ),

    (
        "https://ualosses.org/en/soldier/demo-michael-example-1970-06-09-56-united-kingdom-3rd-separate-assault-brigade-azov/",
        "Demo Michael Example",
        "Demo",
        date(1970, 6, 9),
        "United Kingdom",
        "3rd Separate Assault Brigade Azov",
        None,
        56,
    ),

    (
        "https://ualosses.org/en/soldier/test-nika-example-1987-03-26-39-georgia/",
        "Test Nika Example",
        "Test",
        date(1987, 3, 26),
        "Georgia",
        None,
        None,
        39,
    ),
    # Regression: date present but NO age and NO country. Previously this
    # crashed with UnboundLocalError since `age`/`country` were only
    # assigned inside the (skipped) `if age_value` / `if country_value`
    # branches.
    (
        "https://ualosses.org/en/soldier/john-demo-doe-1990-01-15/",
        "John Demo Doe",
        "John",
        date(1990, 1, 15),
        None,
        None,
        None,
        None,
    ),
 
    # Regression: no date, no age, multi-word country. Previously the
    # no-marker branch only checked the single last word against COUNTRIES,
    # so "united-kingdom" was never recognized without a date/age anchor.
    (
        "https://ualosses.org/en/soldier/jane-demo-smith-united-kingdom/",
        "Jane Demo Smith",
        "Jane",
        None,
        "United Kingdom",
        None,
        None,
        None,
    ),
 
    # Regression: no date, no age, no country at all. Previously this
    # crashed with UnboundLocalError since `country` was never initialized
    # before the "last word isn't a country" fallthrough.
    (
        "https://ualosses.org/en/soldier/nameless-demo-person/",
        "Nameless Demo Person",
        "Nameless",
        None,
        None,
        None,
        None,
        None,
    ),
    # Дата + вік, БЕЗ країни (нічого не йде після віку в URL).
    (
        "https://ualosses.org/en/soldier/taras-demo-shevchenko-1985-07-12-40/",
        "Taras Demo Shevchenko",
        "Taras",
        date(1985, 7, 12),
        None,
        None,
        None,
        40,
    ),

    # Дата, БЕЗ віку, країна є.
    (
        "https://ualosses.org/en/soldier/olena-demo-kovalenko-1992-03-05-poland/",
        "Olena Demo Kovalenko",
        "Olena",
        date(1992, 3, 5),
        "Poland",
        None,
        None,
        None,
    ),

    # Дата + вік + багатослівна країна.
    (
        "https://ualosses.org/en/soldier/dmytro-demo-bondar-1988-11-23-45-south-africa/",
        "Dmytro Demo Bondar",
        "Dmytro",
        date(1988, 11, 23),
        "South Africa",
        None,
        None,
        45,
    ),

    # Без дати, вік + багатослівна країна.
    (
        "https://ualosses.org/en/soldier/oleh-demo-marchenko-52-czech-republic/",
        "Oleh Demo Marchenko",
        "Oleh",
        None,
        "Czechia",
        None,
        None,
        52,
    ),

    # Без дати, без віку, лише однослівна країна в кінці (найпростіша форма 3).
    (
        "https://ualosses.org/en/soldier/ihor-demo-taras-brazil/",
        "Ihor Demo Taras",
        "Ihor",
        None,
        "Brazil",
        None,
        None,
        None,
    ),

    # Вік є, а "країна" в кінці — вигадана, не резолвиться в жодну реальну
    # країну. Раніше це падало з UnboundLocalError; тепер country=None,
    # а нерозпізнаний хвіст просто відкидається (не мерджиться назад в ім'я).
    (
        "https://ualosses.org/en/soldier/vasyl-demo-taras-29-narniya/",
        "Vasyl Demo Taras",
        "Vasyl",
        None,
        None,
        None,
        None,
        29,
    ),

    # Повна комбінація: юніт + звання + дата + вік + країна.
    (
        "https://ualosses.org/en/soldier/yurii-demo-petrenko-1979-05-30-46-georgia-4th-international-legion-soldier/",
        "Yurii Demo Petrenko",
        "Yurii",
        date(1979, 5, 30),
        "Georgia",
        "4th International Legion",
        "Soldier",
        46,
    ),
],
)
def test_parse_soldier_url(
    url: str,
    full_name: str,
    last_name: str | None,
    date_of_birth: date | None,
    country: str | None,
    military_unit_name: str | None,
    rank: str | None,
    age: int | None,
) -> None:
    MILITARY_RANKS = [
        "Soldier",
        "Junior sergeant",
    ]
    MILITARY_UNITS = [
        MilitaryUnit("3rd Separate Assault Brigade Azov"),
        MilitaryUnit("4th International Legion"),
    ]
    assert parse_soldier_url(
        url,
        military_units=MILITARY_UNITS,
        military_ranks=MILITARY_RANKS,
    ) == SoldierListItem(
        url=url,
        full_name=full_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        country=country,
        military_unit_name=military_unit_name,
        rank=rank,
        age=age,
    )