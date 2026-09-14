"""
Groups failed URLs by the error response: 429, 500, other
"""
from pathlib import Path


LOGS_DIR = Path("data/logs")

FAILED_URLS_FILE = LOGS_DIR / "failed_urls.log"

FAILED_URLS_500_FILE = LOGS_DIR / "failed_urls_500_error.log"
FAILED_URLS_429_FILE = LOGS_DIR / "failed_urls_429_error.log"
FAILED_URLS_OTHER_FILE = LOGS_DIR / "failed_urls_other.log"


def main() -> None:
    lines = FAILED_URLS_FILE.read_text(
        encoding="utf-8",
    ).splitlines(keepends=True)

    errors_500: list[str] = []
    errors_429: list[str] = []
    errors_other: list[str] = []

    for line in lines:
        if "too many 500 error responses" in line:
            errors_500.append(line)

        elif "too many 429 error responses" in line:
            errors_429.append(line)

        else:
            errors_other.append(line)

    FAILED_URLS_500_FILE.write_text(
        "".join(errors_500),
        encoding="utf-8",
    )

    FAILED_URLS_429_FILE.write_text(
        "".join(errors_429),
        encoding="utf-8",
    )

    FAILED_URLS_OTHER_FILE.write_text(
        "".join(errors_other),
        encoding="utf-8",
    )

    print(
        f"[DONE] "
        f"total={len(lines)}, "
        f"500={len(errors_500)}, "
        f"429={len(errors_429)}, "
        f"other={len(errors_other)}"
    )


if __name__ == "__main__":
    main()