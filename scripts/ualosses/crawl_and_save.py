import sys
from pathlib import Path
import logging

from src.models.db import SessionLocal
from src.services.osint_sources.ualosses import (
    UALossesCrawler,
    UALossesParser,
)
from src.services.osint_sources.ualosses.service import UALossesService


logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

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
        created = 0
        updated = 0
        errors = 0

        #urls = crawler.root_crawl(LIMIT)
        # urls = crawler.crawl_prefix("h")   # "mnopqrstuvwxyz"
        
        urls = set()
        for symbol in "kl":
            symbol_urls = crawler.crawl_prefix(symbol)
            logger.info(f"Collected {len(symbol_urls)} URLs for symbol '{symbol}'")
            urls.update(symbol_urls)
            

        collected_count = len(urls)
        logger.info(f"Total collected {collected_count} URLs")

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
                        f"[BATCH] committed {processed} of {collected_count} soldiers "
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