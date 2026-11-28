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