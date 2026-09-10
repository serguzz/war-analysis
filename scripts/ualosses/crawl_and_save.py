from src.models.db.database import SessionLocal
from src.services.ualosses.service import UALossesService
from src.services.ualosses_parser.crawler import UALossesCrawler
from src.services.ualosses_parser.parser import UALossesParser


def main():
    crawler = UALossesCrawler(...)
    parser = UALossesParser(...)

    with SessionLocal() as session:
        service = UALossesService(session)

        try:
            for url in crawler.crawl():
                parsed_soldier = parser.parse_soldier(url)

                service.save_soldier(parsed_soldier)

            session.commit()

        except Exception:
            session.rollback()
            raise


if __name__ == "__main__":
    main()