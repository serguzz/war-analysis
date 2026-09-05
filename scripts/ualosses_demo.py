from datetime import date

from src.services.ualosses_parser import UALossesParser
from src.services.ualosses_parser import UALossesClient

client = UALossesClient()
parser = UALossesParser()

urls = parser.get_soldier_urls(page=2)

print(len(urls))

for url in urls[:5]:
    print(url)

html = client.get_soldier_page(urls[0])
with open("data/raw/html/soldier.html", "w", encoding="utf-8") as f:
    f.write(html)

soldier = parser.get_soldier(urls[0])
print(soldier)

# ================

html = client.get_soldier_page("https://ualosses.org/en/soldier/abramchuk-nazar-serhijovych-1999-01-20-24-novomalyn-117th-separate-mechanized-brigade-soldier/")
with open("data/raw/html/soldier_2.html", "w", encoding="utf-8") as f:
    f.write(html)

soldier = parser.get_soldier("https://ualosses.org/en/soldier/abramchuk-nazar-serhijovych-1999-01-20-24-novomalyn-117th-separate-mechanized-brigade-soldier/")
print(soldier)

