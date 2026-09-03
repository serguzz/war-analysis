from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

ODS_PATH = BASE_DIR / "data" / "raw" / "sad.ods"
PARQUET_PATH = BASE_DIR / "data" / "processed" / "sad.parquet"


def main() -> None:
    if not ODS_PATH.exists():
        raise FileNotFoundError(
            f"ODS file not found: {ODS_PATH}"
        )

    # Read ODS into pandas DataFrame
    df = pd.read_excel(
        ODS_PATH,
        engine="odf",
    )

    print(f"File: {ODS_PATH}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumn names:")
    for column in df.columns:
        print(f"  - {column}")

    print("\nData:")
    print(df.to_string(index=False))

    # Convert textual columns to strings.
    # This prevents mixed types (str/int) from causing
    # ArrowTypeError when saving to Parquet.
    text_columns = [
        "place_died",
        "reason_died",
        "name",
        "brigade",
        "brigade_name",
        "rank",
    ]

    for column in text_columns:
        df[column] = df[column].astype("string")

    # Save DataFrame as Parquet
    PARQUET_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_parquet(
        PARQUET_PATH,
        index=False,
    )

    print(f"\nParquet saved to: {PARQUET_PATH}")


if __name__ == "__main__":
    main()