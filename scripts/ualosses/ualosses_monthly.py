from calendar import monthrange
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt

from src.services.ualosses import UALossesParser


BASE_DIR = Path(__file__).resolve().parents[2]

# Analysis period
DATE_START = date(2022, 2, 24)
DATE_END = date(2026, 9, 4)

OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / f"ualosses_monthly_{DATE_START:%Y-%m-%d}_{DATE_END:%Y-%m-%d}.png"
)


def get_month_ranges(
    date_from: date,
    date_to: date,
) -> list[tuple[date, date]]:
    months = []

    current_year = date_from.year
    current_month = date_from.month

    while (current_year, current_month) <= (
        date_to.year,
        date_to.month,
    ):
        month_start = date(
            current_year,
            current_month,
            1,
        )

        last_day = monthrange(
            current_year,
            current_month,
        )[1]

        month_end = date(
            current_year,
            current_month,
            last_day,
        )

        # Trim first month to date_from.
        if month_start < date_from:
            month_start = date_from

        # Trim last month to date_to.
        if month_end > date_to:
            month_end = date_to

        months.append(
            (
                month_start,
                month_end,
            )
        )

        if current_month == 12:
            current_year += 1
            current_month = 1
        else:
            current_month += 1

    return months


def main() -> None:
    parser = UALossesParser()

    monthly_data = []

    for month_start, month_end in get_month_ranges(
        date_from=DATE_START,
        date_to=DATE_END,
    ):
        count = parser.get_people_count(
            date_from=month_start,
            date_to=month_end,
        )

        monthly_data.append(
            {
                "date_from": month_start,
                "date_to": month_end,
                "count": count,
            }
        )

        print(
            f"{month_start:%Y-%m}: "
            f"{month_start:%d.%m.%Y} - "
            f"{month_end:%d.%m.%Y}: "
            f"{count}"
        )

    # Prepare chart data
    month_labels = [
        item["date_from"].strftime("%Y-%m")
        for item in monthly_data
    ]

    counts = [
        item["count"]
        for item in monthly_data
    ]

    # Create chart
    fig, ax = plt.subplots(
        figsize=(16, 7),
    )

    bars = ax.bar(
        month_labels,
        counts,
    )

    ax.set_title(
        f"UA Losses — People by month: "
        f"{DATE_START} — {DATE_END}"
    )

    ax.set_xlabel("Month")
    ax.set_ylabel("Number of people")

    ax.tick_params(
        axis="x",
        rotation=45,
    )

    # Show values above bars
    for bar, value in zip(
        bars,
        counts,
    ):
        if value > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value,
                str(value),
                ha="center",
                va="bottom",
            )

    plt.tight_layout()

    # Save chart
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.savefig(
        OUTPUT_PATH,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f"\nChart saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()