from datetime import date
from pathlib import Path

from src.services.ualosses_parser import UALossesParser
from src.services.ualosses_parser import UALossesClient

BASE_DIR = Path(__file__).resolve().parents[1]

client = UALossesClient()
parser = UALossesParser()

page_number = 1000

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

def demo_soldiers_page(page_number: int):
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


def demo_soldier_page(links: list):
    for index, link in enumerate(links):
        html = client.get_soldier_page(link)
        with open(f"data/raw/html/soldier_{index}.html", "w", encoding="utf-8") as f:
            f.write(html)

        soldier = parser.get_soldier(link)
        print(soldier)


links = [
    "https://ualosses.org/en/soldier/andryeyev-oleksij-oleksandrovych-1996-06-30-25-novomoskovsk-25th-separate-airborne-brigade-senior-sergeant/",
    "https://ualosses.org/en/soldier/derjahin-roman-jurijovych-1972-06-29-50-rubizhne-92nd-separate-mechanized-brigade-senior-soldier/"
    # urls[0],
]

demo_soldier_page(links)