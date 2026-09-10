from src.models.db.database import SessionLocal
from src.services.ualosses.service import UALossesService
from src.services.ualosses_parser.crawler import UALossesCrawler
from src.services.ualosses_parser.parser import UALossesParser


BATCH_SIZE = 100


def main():
    crawler = UALossesCrawler(...)
    parser = UALossesParser(...)

    with SessionLocal() as session:
        service = UALossesService(session)

        processed = 0
        saved = 0
        errors = 0

        for url in crawler.crawl():
            processed += 1

            try:
                with session.begin_nested():
                    parsed_soldier = parser.parse_soldier(url)
                    service.save_soldier(parsed_soldier)

                saved += 1

                print(
                    f"[OK] {processed} "
                    f"{url}"
                )

            except Exception as exc:
                errors += 1

                print(
                    f"[ERROR] {processed} "
                    f"{url}: "
                    f"{type(exc).__name__}: {exc}"
                )

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
                    f"saved={saved}, "
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
            f"saved={saved}, "
            f"errors={errors}"
        )


if __name__ == "__main__":
    main()