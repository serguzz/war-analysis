from datetime import date

from src.services.ualosses_parser import UALossesParser


parser = UALossesParser()

count = parser.get_people_count(
    date_from=date(2022, 2, 24),
    date_to=date(2022, 2, 28),
)

print(count)