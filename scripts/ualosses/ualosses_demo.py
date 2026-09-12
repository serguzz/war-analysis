from pathlib import Path

from src.services.ualosses import UALossesParser, UALossesClient, UALossesCrawler

BASE_DIR = Path(__file__).resolve().parents[2]

client = UALossesClient()
parser = UALossesParser()
crawler = UALossesCrawler(
    parser,
    delay_sec=0.2,
)

page_number = 1000

page_html_dir = (
    BASE_DIR
    / "data"
    / "raw"
    / "html"
    / f"page_{page_number}"
)

page_html_base = (
    BASE_DIR
    / "data"
    / "raw"
    / "html"
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

def demo_soldiers_name_filtering(last_name: str):
    html = client.get_soldiers_page(last_name=last_name)
    page_html_path = page_html_base / f"name={last_name}_page_1.html"
    with open(page_html_path, "w", encoding="utf-8") as f:
        f.write(html)

def demo_soldier_page(links: list):
    for index, link in enumerate(links):
        html = client.get_soldier_page(link)
        with open(f"data/raw/html/soldier_{index}.html", "w", encoding="utf-8") as f:
            f.write(html)

        soldier = parser.get_soldier(link)
        print(soldier)


def demo_listing_by_lastname_page(lastname: str, page: int = 1):
    count = parser.get_found_count(lastname)
    print(count)

    items = parser.get_soldiers_listing(
        page=page,
        last_name=lastname,
    )

    for item in items[:5]:
        print(item)    


def demo_crawler():
    prefixes = [
        "ab",
        # "ni",
        # "'"
    ]
    for prefix in prefixes:
        print(f"\n{'=' * 60}")

        print(f"PREFIX: {prefix}")
        count = parser.get_found_count(last_name=prefix)
        print(f"Found by server: {count}")

        print(f"{'=' * 60}")

        urls = crawler.crawl_prefix(prefix)
        print(f"Found URLs: {len(urls)}")

        sorted_urls = sorted(urls)

        for url in sorted_urls[:50]:
            print(url)
        for url in sorted_urls[-50:]:
            print(url)



links = [
    # "https://ualosses.org/en/soldier/andryeyev-oleksij-oleksandrovych-1996-06-30-25-novomoskovsk-25th-separate-airborne-brigade-senior-sergeant/",
    # "https://ualosses.org/en/soldier/derjahin-roman-jurijovych-1972-06-29-50-rubizhne-92nd-separate-mechanized-brigade-senior-soldier/"
    # urls[0],
    "https://ualosses.org/en/soldier/aleksandrov-bohdan-oleksandrovych-23-chernjakhiv-captain/",
]

demo_soldier_page(links)

names = [
    "z",
    # "ni",
    # "f'",
    # "-",
    # "g"
]

# for name in names:
#     demo_listing_by_lastname_page(name, 226)

# demo_crawler()