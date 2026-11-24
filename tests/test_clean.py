import hashlib  # for checksum checking
import pandas as pd
import pytest

# The 27 member states, spelled as in the Our World in Data file
EU27 = [
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czechia",
    "Denmark", "Estonia", "Finland", "France", "Germany", "Greece",
    "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg",
    "Malta", "Netherlands", "Poland", "Portugal", "Romania", "Slovakia",
    "Slovenia", "Spain", "Sweden",
]


@pytest.fixture(scope="module")
def df():
    return pd.read_csv("data/processed/co2_eu.csv")


def test_only_eu27_countries(df):
    assert set(df["country"]) == set(EU27)  # no World, no UK

# Test 1: one row per country and year, exactly the years 2000 to 2024
def test_one_row_per_country_and_year(df):
    # No (country, year) pair may appear twice
    assert not df.duplicated(["country", "year"]).any()

    # The years must be exactly 2000, 2001, ..., 2024 (range excludes the end)
    assert set(df["year"]) == set(range(2000, 2025))

    # 27 countries x 25 years = 675 rows: no missing or extra combinations
    assert len(df) == 27 * 25

# Test 2: no missing values in the three key columns
def test_no_missing_values(df):
    columns = ["population", "co2", "co2_per_capita"]
    # isna() marks every missing cell, sum() counts them per column
    missing = df[columns].isna().sum()
    # If the test fails, the message shows which column has how many gaps
    assert missing.sum() == 0, f"Missing values:\n{missing}"

# Test 3: units fit together
# co2 is in million tonnes, population in persons,
# co2_per_capita in tonnes per person
def test_units_fit_together(df):
    # Recompute tonnes per person: million tonnes * 1,000,000 / persons
    expected = df["co2"] * 1_000_000 / df["population"]
    # approx compares with a tolerance of 0.1 % instead of exact equality
    # (floating point numbers and rounding in the source data)
    assert df["co2_per_capita"].to_numpy() == pytest.approx(
        expected.to_numpy(), rel=0.001
    )

# Test 4: the raw data file is unchanged (checked by its SHA-256 checksum)
# This test does not need df: it does not read co2_eu.csv
def test_raw_file_unchanged():
    path = "data/raw/owid-co2-data.csv"
    # Read the whole file as bytes and compute its hash
    with open(path, "rb") as f:
        checksum = hashlib.sha256(f.read()).hexdigest()
    # Expected hash of the pinned version
    assert checksum == "7f78e2b218ce4bb8c538bbec04fdc9a7982e8d40bff972e650df603899edd5f6"