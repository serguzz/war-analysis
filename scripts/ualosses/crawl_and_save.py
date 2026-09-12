import sys
from pathlib import Path

from src.models.db import SessionLocal
from src.services.ualosses import (
    UALossesCrawler,
    UALossesParser,
)
from src.services.ualosses.service import UALossesService

BATCH_SIZE = 100
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 1

FAILED_URLS_FILE = Path("data/logs/failed_urls.log")
FAILED_URLS_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

def log_failed_url(exc: Exception, url: str) -> None:
    with FAILED_URLS_FILE.open("a", encoding="utf-8") as file:
        file.write(f"{type(exc).__name__}: {exc}\t{url}\n")

def main():
    parser = UALossesParser()
    crawler = UALossesCrawler(parser)

    with SessionLocal() as session:
        service = UALossesService(session)

        processed = 0
        saved = 0
        created = 0
        updated = 0
        errors = 0

        #urls = crawler.root_crawl(LIMIT)
        urls = crawler.crawl_prefix("d")
        
        """urls = set()
        for symbol in "nopqrstuvwxyz":
        # for symbol in "m":
            prefix = 'a' + symbol
            symbol_urls = crawler.crawl_prefix(prefix)
            urls.update(symbol_urls)"""

        for url in sorted(urls):

            if processed >= LIMIT:
                break

            try:
                with session.begin_nested():
                    parsed_soldier = parser.get_soldier(url)
                    result = service.save_soldier(parsed_soldier)

                if result.created:
                    created += 1
                else:
                    updated += 1

                """print(
                    f"[OK] {processed} "
                    f"{url}"
                )"""

            except Exception as exc:
                errors += 1

                print(
                    f"[ERROR] {processed} "
                    f"{url}: "
                    f"{type(exc).__name__}: {exc}"
                )
                log_failed_url(exc, url)

            finally:
                processed += 1

            if processed % BATCH_SIZE == 0:
                try:
                    session.commit()

                    print(
                        f"[BATCH] committed {processed} soldiers "
                        f"(created={created}, updated={updated}, saved={created + updated}, errors={errors})"
                    )

                except Exception as exc:
                    session.rollback()

                    print(
                        f"[BATCH ERROR] "
                        f"after {processed} soldiers: "
                        f"{type(exc).__name__}: {exc}"
                    )

        # Commit remaining soldiers if the last batch
        # was smaller than BATCH_SIZE.
        if processed % BATCH_SIZE != 0:
            try:
                session.commit()

                print(
                    f"[BATCH] committed final batch "
                    f"(processed={processed}, "
                    f"created={created}, "
                    f"updated={updated}, "
                    f"saved={created + updated}, "
                    f"errors={errors})"
                )

            except Exception as exc:
                session.rollback()

                print(
                    f"[BATCH ERROR] final batch: "
                    f"{type(exc).__name__}: {exc}"
                )

        print(
            f"[DONE] "
            f"processed={processed}, "
            f"saved={created + updated}, "
            f"errors={errors}"
        )


if __name__ == "__main__":
    main()