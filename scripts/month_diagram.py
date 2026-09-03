from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

ODS_PATH = BASE_DIR / "data" / "raw" / "sad.ods"


# Analysis period
DATE_START = "2022-01-01"
DATE_END = "2026-08-31"


def main() -> None:
    if not ODS_PATH.exists():
        raise FileNotFoundError(
            f"ODS file not found: {ODS_PATH}"
        )

    # Read ODS
    df = pd.read_excel(
        ODS_PATH,
        engine="odf",
    )

    # Convert date_died to datetime
    df["date_died"] = pd.to_datetime(
        df["date_died"],
        errors="coerce",
    )

    # Remove records without death date
    df = df.dropna(subset=["date_died"])

    # Convert analysis dates to datetime
    date_start = pd.Timestamp(DATE_START)
    date_end = pd.Timestamp(DATE_END)

    # Filter by date range
    df = df[
        (df["date_died"] >= date_start)
        & (df["date_died"] <= date_end)
    ].copy()

    # Group by month
    monthly_counts = (
        df.groupby(
            df["date_died"].dt.to_period("M")
        )
        .size()
    )

    # Create complete range of months.
    # This ensures that months with zero deaths are also displayed.
    all_months = pd.period_range(
        start=date_start.to_period("M"),
        end=date_end.to_period("M"),
        freq="M",
    )

    monthly_counts = monthly_counts.reindex(
        all_months,
        fill_value=0,
    )

    # Convert PeriodIndex to text labels
    month_labels = [
        month.strftime("%Y-%m")
        for month in monthly_counts.index
    ]

    # Create chart
    fig, ax = plt.subplots(figsize=(12, 6))

    bars = ax.bar(
        month_labels,
        monthly_counts.values,
    )

    ax.set_title(
        f"Deaths by month: "
        f"{DATE_START} — {DATE_END}"
    )

    ax.set_xlabel("Month")
    ax.set_ylabel("Number of deaths")

    ax.tick_params(
        axis="x",
        rotation=45,
    )

    # Show values above bars
    for bar, value in zip(
        bars,
        monthly_counts.values,
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
    
    output_path = BASE_DIR / "data" / "processed" / "month_diagram.png"

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight",
    )
    
if __name__ == "__main__":
    main()