from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class UALossesClient:
    BASE_URL = "https://ualosses.org/en/soldiers/"

    def __init__(self) -> None:
        self.session = Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get_soldiers_page(
        self,
        page: int = 1,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> str:
        params = {
            "page": page,
        }

        if date_from is not None:
            params["dod_start"] = date_from

        if date_to is not None:
            params["dod_end"] = date_to

        response = self.session.get(
            self.BASE_URL,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        return response.text

    def get_soldier_page(
        self,
        url: str,
    ) -> str:
        response = self.session.get(
            url,
            timeout=30,
        )

        response.raise_for_status()

        return response.text

    def get_soldiers_date_range(
        self,
        date_from: str,
        date_to: str,
    ) -> str:
        params = {
            "dod_start": date_from,
            "dod_end": date_to,
        }

        response = self.session.get(
            self.BASE_URL,
            params=params,
            timeout=30,
        )
        response.raise_for_status()

        return response.text