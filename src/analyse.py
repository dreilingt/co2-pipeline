"""Rank EU countries by their per-person CO2 reductions from 2000 to 2024."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = REPOSITORY_ROOT / "data" / "processed" / "co2_eu.csv"
OUTPUT_FILE = REPOSITORY_ROOT / "figures" / "co2_reductions_2000_2024.png"
START_YEAR = 2000
END_YEAR = 2024
COUNTRY_COUNT = 27


def load_comparison_data() -> pd.DataFrame:
    data = pd.read_csv(
        INPUT_FILE,
        usecols=["country", "year", "co2_per_capita"],
    )
    period = data[data["year"].isin([START_YEAR, END_YEAR])].copy()
    print(
        "Rows after filtering to years "
        f"{START_YEAR} and {END_YEAR}: {len(period)}"
    )

    missing_values = period[["country", "year", "co2_per_capita"]].isna().sum()
    missing_values = missing_values[missing_values > 0]
    if not missing_values.empty:
        counts = ", ".join(
            f"{column}={count}" for column, count in missing_values.items()
        )
        raise ValueError(f"Missing values in the comparison data: {counts}.")

    duplicate_rows = period.duplicated(["country", "year"])
    if duplicate_rows.any():
        count = int(duplicate_rows.sum())
        raise ValueError(f"Found {count} duplicate country-year rows.")

    if period["country"].nunique() != COUNTRY_COUNT:
        raise ValueError(
            f"Expected {COUNTRY_COUNT} countries in the comparison data; "
            f"found {period['country'].nunique()}."
        )

    values = period.pivot(
        index="country",
        columns="year",
        values="co2_per_capita",
    )
    if values[[START_YEAR, END_YEAR]].isna().any().any():
        raise ValueError(
            f"Each country must have a {START_YEAR} and {END_YEAR} value."
        )
    if (values[START_YEAR] <= 0).any():
        raise ValueError(
            f"All {START_YEAR} per-person values must be positive "
            "to calculate percentage cuts."
        )

    comparison = values[[START_YEAR, END_YEAR]].copy()
    comparison["tonnes_cut"] = (
        comparison[START_YEAR] - comparison[END_YEAR]
    )
    comparison["percent_cut"] = (
        comparison["tonnes_cut"] / comparison[START_YEAR] * 100
    )
    return comparison


def print_top_three(comparison: pd.DataFrame, column: str, unit: str) -> None:
    ranked = comparison.nlargest(3, column)
    print(f"\nTop three cuts by {unit}:")
    for country, row in ranked.iterrows():
        print(
            f"{country}: {START_YEAR}={row[START_YEAR]:.3f} tonnes/person, "
            f"{END_YEAR}={row[END_YEAR]:.3f} tonnes/person, "
            f"cut={row[column]:.2f} {unit}"
        )


def save_chart(comparison: pd.DataFrame) -> None:
    top_tonnes = comparison.nlargest(3, "tonnes_cut").sort_values("tonnes_cut")
    top_percent = comparison.nlargest(3, "percent_cut").sort_values("percent_cut")

    figure, (tonnes_axis, percent_axis) = plt.subplots(
        1, 2, figsize=(13, 6)
    )
    tonnes_bars = tonnes_axis.barh(
        top_tonnes.index,
        top_tonnes["tonnes_cut"],
        color="violet",
    )
    tonnes_axis.set_title("Largest reductions in absolute terms")
    tonnes_axis.set_xlabel("Reduction (tonnes CO₂ per person)")
    tonnes_axis.set_ylabel("Country")
    tonnes_max = float(top_tonnes["tonnes_cut"].max())
    tonnes_padding = tonnes_max * 0.02
    for bar in tonnes_bars:
        value = bar.get_width()
        tonnes_axis.text(
            value + tonnes_padding,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.2f}",
            va="center",
        )
    tonnes_axis.set_xlim(0, tonnes_max * 1.2)
    tonnes_axis.set_xticks([])

    percent_bars = percent_axis.barh(
        top_percent.index,
        top_percent["percent_cut"],
        color="orange",
    )
    percent_axis.set_title("Largest percentage reductions")
    percent_axis.set_xlabel("Reduction (%)")
    percent_axis.set_ylabel("Country")
    percent_max = float(top_percent["percent_cut"].max())
    percent_padding = percent_max * 0.02
    for bar in percent_bars:
        value = bar.get_width()
        percent_axis.text(
            value + percent_padding,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1f}",
            va="center",
        )
    percent_axis.set_xlim(0, percent_max * 1.2)
    percent_axis.set_xticks([])

    figure.suptitle(
        "EU-27: Reduction in CO₂ emissions per capita, 2000–2024"
    )
    figure.tight_layout(rect=(0, 0, 1, 0.94))
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT_FILE, dpi=150)
    plt.close(figure)
    print(f"\nWrote chart to {OUTPUT_FILE}.")


def run() -> None:
    comparison = load_comparison_data()
    print_top_three(comparison, "tonnes_cut", "tonnes/person")
    print_top_three(comparison, "percent_cut", "%")
    save_chart(comparison)


def main() -> int:
    try:
        run()
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
