"""Create a complete EU27 CO2 dataset for 2000-2024."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = REPOSITORY_ROOT / "data" / "raw" / "owid-co2-data.csv"
OUTPUT_FILE = REPOSITORY_ROOT / "data" / "processed" / "co2_eu.csv"

EU27 = [
    "Austria",
    "Belgium",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czechia",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Ireland",
    "Italy",
    "Latvia",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Netherlands",
    "Poland",
    "Portugal",
    "Romania",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden",
]
YEARS = range(2000, 2025)
OUTPUT_COLUMNS = [
    "country",
    "iso_code",
    "year",
    "population",
    "co2",
    "co2_per_capita",
]


def run() -> None:
    data = pd.read_csv(RAW_FILE, usecols=OUTPUT_COLUMNS)

    eu_rows = data[data["country"].isin(EU27)]
    print(f"Rows after filtering to EU27 country names: {len(eu_rows)}")

    period = eu_rows[eu_rows["year"].between(2000, 2024)]
    print(f"Rows after filtering to years 2000-2024: {len(period)}")

    missing_values = period[OUTPUT_COLUMNS].isna().sum()
    missing_values = missing_values[missing_values > 0]
    if not missing_values.empty:
        counts = ", ".join(
            f"{column}={count}" for column, count in missing_values.items()
        )
        raise ValueError(f"Missing values in the selected data: {counts}.")

    duplicate_rows = period.duplicated(["country", "year"])
    if duplicate_rows.any():
        count = int(duplicate_rows.sum())
        raise ValueError(f"Found {count} duplicate country-year rows.")

    expected = {(country, year) for country in EU27 for year in YEARS}
    observed = set(zip(period["country"], period["year"]))
    missing_rows = sorted(expected - observed)
    if missing_rows:
        examples = ", ".join(
            f"{country} ({year})" for country, year in missing_rows[:5]
        )
        raise ValueError(
            f"Missing {len(missing_rows)} expected country-year rows"
            f" (for example: {examples})."
        )

    result = (
        period[OUTPUT_COLUMNS]
        .sort_values(["country", "year"])
        .reset_index(drop=True)
    )
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_FILE, index=False)
    print(f"Wrote {len(result)} rows to {OUTPUT_FILE}.")


def main() -> int:
    try:
        run()
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
