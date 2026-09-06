from datetime import date
from pathlib import Path

from src.services.ualosses_parser import UALossesParser
from src.services.ualosses_parser import UALossesClient

BASE_DIR = Path(__file__).resolve().parents[1]

client = UALossesClient()
parser = UALossesParser()

page_number = 300

page_html_dir = (
    BASE_DIR
    / "data"
    / "raw"
    / "html"
    / f"page_{page_number}"
)

page_soldiers_dir = (
    BASE_DIR
    / "data"
    / "processed"
    / "soldiers"
    / f"page_{page_number}"
)

page_html_dir.mkdir(
    parents=True,
    exist_ok=True,
)

page_soldiers_dir.mkdir(
    parents=True,
    exist_ok=True,
)

# print(page_html_dir)
# exit(0)

urls = parser.get_soldier_urls(page=page_number)

print(len(urls))

for index, url in enumerate(urls[:5]):
    print(index, ". ",  url)
    html = client.get_soldier_page(url)
    page_html_path = page_html_dir / f"soldier_{index}.html"
    with open(page_html_path, "w", encoding="utf-8") as f:
        f.write(html)

    soldier = parser.get_soldier(url)
    soldier_path = page_soldiers_dir / f"soldier_{index}.txt"
    with open(soldier_path, "w", encoding="utf-8") as f:
        f.write(str(soldier))
    # print(soldier)    


# ================

"""
links = [
    urls[0],
    "https://ualosses.org/en/soldier/abramchuk-nazar-serhijovych-1999-01-20-24-novomalyn-117th-separate-mechanized-brigade-soldier/",
    "https://ualosses.org/en/soldier/abashyn-ivan-serhijovych-1990-06-09-kyiv/"
]

for index, link in enumerate(links):
    html = client.get_soldier_page(link)
    with open(f"data/raw/html/soldier_{index}.html", "w", encoding="utf-8") as f:
        f.write(html)

    soldier = parser.get_soldier(link)
    print(soldier)
"""