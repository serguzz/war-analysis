import logging

from math import ceil
from time import sleep

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

LETTERS = "abcdefghijklmnopqrstuvwxyz"
SYMBOLS = "'-"
ALPHABET = SYMBOLS + LETTERS

SOLDIERS_PER_PAGE = 100
MAX_PAGE = 499

def normalize_last_name(name: str) -> str:
    return name.lower()


def last_name_starts_with(
    name: str,
    prefix: str,
) -> bool:
    return normalize_last_name(name).startswith(
        normalize_last_name(prefix)
    )


def next_prefix(prefix: str) -> str:
    """
    Return the next lexicographic prefix.

    Returns an empty string when no upper bound exists.
    """
    prefix = normalize_last_name(prefix)

    if not prefix:
        return ""

    chars = list(prefix)

    for i in range(len(chars) - 1, -1, -1):
        char = chars[i]

        if char not in ALPHABET:
            return ""

        index = ALPHABET.index(char)

        if index < len(ALPHABET) - 1:
            chars[i] = ALPHABET[index + 1]

            return "".join(chars[: i + 1])

    return ""


def estimate_max_page(found_count: int) -> int:
    """
    Estimate the last listing page for the given result count.

    The website exposes at most 499 listing pages.
    """
    return min(MAX_PAGE, ceil(found_count / SOLDIERS_PER_PAGE))


def needs_subdivide(found_count: int) -> bool:
    """
    Return True when a prefix contains more records
    than can be reached within the 499-page limit.
    """
    return ceil(found_count / SOLDIERS_PER_PAGE) > MAX_PAGE


def expand_prefix(parent: str) -> list[str]:
    """
    Expand a prefix by one symbol.
    """
    return [parent + symbol for symbol in ALPHABET]


class UALossesCrawler:

    def __init__(
        self,
        parser,
        *,
        delay_sec: float = 0.5,
    ):
        self.parser = parser
        self.delay_sec = delay_sec

    def crawl_prefixes(
        self,
        prefixes: list[str] | None = None,
    ) -> list[str]:
        """
        Crawl the given prefixes.

        If prefixes is None, start from the root alphabet
        and adaptively subdivide prefixes that exceed the
        499-page limit.

        Returns:
            Sorted list of unique soldier URLs.
        """
        urls: set[str] = set()

        if prefixes is None:
            prefixes = ALPHABET

        for prefix in prefixes:
            urls.update(
                self.crawl_prefix(prefix)
            )

        return sorted(urls)

    def crawl_prefix(
        self,
        prefix: str,
    ) -> set[str]:
        """
        Crawl one last-name prefix.

        If the prefix contains more than 499 pages,
        recursively subdivide it into child prefixes.
        """
        logger.info(f"Crawling for prefix: {prefix}")
        found_count = self.parser.get_found_count(
            last_name=prefix,
        )
        logger.info(f"Found {found_count} records for prefix: {prefix}")

        if found_count == 0:
            return set()

        if needs_subdivide(found_count):
            logger.info(f"Needs subdivide, because too many found: {found_count}")
            urls: set[str] = set()

            for child_prefix in expand_prefix(prefix):
                urls.update(
                    self.crawl_prefix(child_prefix)
                )

            return urls

        max_page = estimate_max_page(found_count)
        logger.info(f"Max page estimated to: {max_page}")

        first_page = self._find_first_page(
            prefix,
            max_page,
        )

        if first_page is None:
            logger.info(f"First page not found! No names starting with \"{prefix}\"")
            return set()

        logger.info(f"First page is: {first_page}")

        return self._collect_pages(
            prefix,
            first_page,
            max_page,
        )

    def _find_first_page(
        self,
        prefix: str,
        max_page: int,
    ) -> int | None:
        """
        Find the first listing page containing a record
        whose last name starts with the given prefix.
        """
        lo = 1
        hi = max_page
        first_page: int | None = None

        normalized_prefix = normalize_last_name(prefix)

        while lo <= hi:
            mid = (lo + hi) // 2

            records = self.parser.get_soldiers_listing(
                page=mid,
                last_name=prefix,
            )

            self._delay()

            if not records:
                hi = mid - 1
                continue

            if any(
                last_name_starts_with(record.last_name,normalized_prefix)
                for record in records
            ):
                first_page = mid
                hi = mid - 1
                continue

            last_name = normalize_last_name(records[-1].last_name)

            if last_name < normalized_prefix:
                lo = mid + 1
            else:
                hi = mid - 1

        return first_page

    def _collect_pages(
        self,
        prefix: str,
        first_page: int,
        max_page: int,
    ) -> set[str]:
        """
        Sequentially collect soldier URLs belonging
        to the given prefix.
        """
        urls: set[str] = set()

        normalized_prefix = normalize_last_name(prefix)
        upper_bound = next_prefix(prefix)
        logger.info(f"Next prefix is: {upper_bound}")

        for page in range(first_page, max_page + 1):
            records = self.parser.get_soldiers_listing(
                page=page,
                last_name=prefix,
            )

            self._delay()

            if not records:
                break

            first_last_name = normalize_last_name(
                records[0].last_name
            )

            if (
                upper_bound
                and first_last_name >= upper_bound
            ):
                break

            for record in records:
                if last_name_starts_with(
                    record.last_name,
                    normalized_prefix,
                ):
                    urls.add(record.url)

        return urls

    def _delay(self) -> None:
        if self.delay_sec > 0:
            sleep(self.delay_sec)