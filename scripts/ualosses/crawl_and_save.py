from src.services.ualosses_parser import UALossesCrawler, UALossesParser
from src.services.ualosses import UALossesService



def main():
    crawler = UALossesCrawler(...)
    parser = UALossesParser(...)
    service = UALossesService(...)


    # TODO: Commit this after every 100 (adjustable) soldiers
    with SessionLocal() as session:
        try:
            for url in crawler:
                soldier = parser.parse_soldier(url)
                service.save_soldier(session, soldier)

            session.commit()
        except:
            session.rollback()
            raise