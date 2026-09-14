import re
from datetime import date, datetime
from src.services.osint_sources.ualosses.models import DatePrecision

# Covers the case when date is "?"
def parse_optional_date(value: str) -> tuple[date | None, DatePrecision | None]:
    value = value.strip()
    value = value.strip("()")

    if value == "?":
        return None, None

    return parse_date(value)


def parse_date(value: str) -> tuple[date, DatePrecision]:
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
            parsed_date = datetime.strptime(value, fmt).date()
            return (parsed_date, DatePrecision.DAY)

        except ValueError:
            continue

    if re.fullmatch(r"\d{4}", value):
        year = int(value)
        return (date(year, 1, 1), DatePrecision.YEAR)

    raise ValueError(f"Unknown date format: {value}")
