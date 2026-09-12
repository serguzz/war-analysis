"""
    Run for prefix crawl:
    ```bash
    docker compose run --rm app \
    python scripts/ualosses_crawl.py --prefixes "ni,f',z,-"
    ```

    Full crawl:
    ```bash
    docker compose run --rm app \
    python scripts/ualosses_crawl.py --all
    ```

"""

import argparse

from src.services.ualosses import UALossesParser, UALossesCrawler


def process_soldiers(urls: list[str]):
    parser = UALossesParser()
    for url in urls:
        soldier = parser.get_soldier(url)
        print(soldier)
        # write soldier to DB
    pass


def main():
    parser = argparse.ArgumentParser(
        description="Crawl soldier records from UA Losses."
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--prefixes",
        type=str,
        help="Comma-separated prefixes to crawl, e.g. ni,f',z,-",
    )

    group.add_argument(
        "--all",
        action="store_true",
        help="Run full adaptive crawl.",
    )

    args = parser.parse_args()

    parser_service = UALossesParser()

    crawler = UALossesCrawler(
        parser_service,
        delay_sec=0.2,
    )

    if args.all:
        urls = crawler.root_crawl()

    else:
        prefixes = [
            prefix.strip()
            for prefix in args.prefixes.split(",")
            if prefix.strip()
        ]

        urls = set()

        for prefix in prefixes:
            print(f"\n{'=' * 60}")
            print(f"PREFIX: {prefix}")

            count = parser_service.get_found_count(
                last_name=prefix,
            )

            print(f"Found by server: {count}")
            print(f"{'=' * 60}")

            prefix_urls = crawler.crawl_prefix(prefix)

            print(f"Found URLs: {len(prefix_urls)}")

            urls.update(prefix_urls)

    print(f"\n{'=' * 60}")
    print(f"TOTAL UNIQUE URLs: {len(urls)}")
    print(f"{'=' * 60}")

    sorted_urls = sorted(urls)

    """for url in sorted_urls[:50]:
        print(url)
    for url in sorted_urls[-50:]:
        print(url)"""

    print(f"{'=' * 60}")
    print(f"Getting soldiers and saving to DB ...\n")

    process_soldiers(sorted_urls)




if __name__ == "__main__":
    main()