import matplotlib

matplotlib.use("Agg")  # draw charts without opening a window

import pandas as pd
import pytest

import eu_report as r


@pytest.fixture(scope="module")
def df():
    return r.load()


@pytest.fixture(scope="module")
def owid_eu(df):
    """Our World in Data's own row for the 27 member states."""
    return df[df["country"] == "European Union (27)"].set_index("year")


def test_report_runs():
    r.main()

# Bug 1: Missing Czechia
def test_eu_members_keeps_czechia():
    toy = pd.DataFrame({
        "country": ["Czechia"],
        "year": [1990],
        "consumption_co2": [150.0],
    })
    assert len(r.eu_members(toy)) == 1

# Bug 2: dropna in eu_members
def test_eu_members_keeps_latest_year_without_consumption():
    toy = pd.DataFrame({
        "country": ["Austria", "Austria"],
        "year": [1990, 2024],
        "co2": [60.0, 56.0],
        "consumption_co2": [88.0, None],
    })
    eu = r.eu_members(toy)
    assert eu["year"].max() == 2024

def test_missing_consumption_is_not_summed_to_zero():
    toy = pd.DataFrame({
        "country": ["Austria", "Belgium"],
        "year": [2024, 2024],
        "co2": [56.0, 90.0],
        "consumption_co2": [float("nan"), float("nan")],
    })
    totals = r.eu_totals(toy)
    assert pd.isna(totals.loc[2024, "consumption_co2"])

def test_imports_use_last_year_with_data():
    totals = pd.DataFrame(
        {"co2": [100.0, 90.0, 80.0], "consumption_co2": [120.0, 110.0, None]},
        index=pd.Index([1990, 2023, 2024], name="year"),
    )
    imports = r.embedded_imports(totals)
    assert imports.index.max() == 2023   # 2024 has no consumption data
    assert imports.loc[2023] == 20.0     # 110 - 90


def test_imports_match_owid_trade_co2(df, owid_eu):
    imports = r.embedded_imports(r.eu_totals(r.eu_members(df)))
    assert imports.loc[2023] == pytest.approx(owid_eu.loc[2023, "trade_co2"], abs=0.1)

# Bug 3: unweighted mean in per_person
def test_per_person_is_weighted_by_population():
    toy = pd.DataFrame({
        "country": ["A", "B"],
        "year": [1990, 1990],
        "co2": [90.0, 1.0],                  # Mt
        "population": [9_000_000, 1_000_000],
        "co2_per_capita": [10.0, 1.0],       # t per person
    })
    assert r.per_person(toy).loc[1990] == pytest.approx(9.1)


def test_per_person_matches_owid(df, owid_eu):
    pp = r.per_person(r.eu_members(df))
    assert pp.loc[1990] == pytest.approx(owid_eu.loc[1990, "co2_per_capita"], abs=0.01)
    assert pp.loc[2024] == pytest.approx(owid_eu.loc[2024, "co2_per_capita"], abs=0.01)

# Bug 4: world_share divides by the sum of all rows
def test_world_share_matches_owid(df, owid_eu):
    share = r.world_share(df, r.eu_members(df))
    assert share.loc[1990] == pytest.approx(owid_eu.loc[1990, "share_global_co2"], abs=0.01)
    assert share.loc[2024] == pytest.approx(owid_eu.loc[2024, "share_global_co2"], abs=0.01)