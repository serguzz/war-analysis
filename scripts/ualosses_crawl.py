from pathlib import Path

from src.services.ualosses_parser import UALossesParser, UALossesClient, UALossesCrawler

BASE_DIR = Path(__file__).resolve().parents[1]

client = UALossesClient()
parser = UALossesParser()
crawler = UALossesCrawler(
    parser,
    delay_sec=0.2,
)

page_html_base = (
    BASE_DIR
    / "data"
    / "raw"
    / "html"
)


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


names = [
    "z",
    # "ni",
    # "f'",
    # "-",
    # "g"
]

# for name in names:
#     demo_listing_by_lastname_page(name, 226)

demo_crawler()