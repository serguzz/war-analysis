import sys

from src.models.db.database import SessionLocal
from src.services.ualosses.service import UALossesService
from src.services.ualosses_parser.crawler import UALossesCrawler
from src.services.ualosses_parser.parser import UALossesParser

BATCH_SIZE = 100
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 1

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

        # urls = crawler.root_crawl()
        urls = crawler.crawl_prefix("abab")

        for url in urls:

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

            finally:
                processed += 1

            if processed % BATCH_SIZE == 0:
                try:
                    session.commit()

                    print(
                        f"[BATCH] committed {processed} soldiers "
                        f"(saved={saved}, errors={errors})"
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