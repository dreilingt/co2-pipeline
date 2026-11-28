"""How far has the EU come since 1990?

Prompt:
    Write a script that reports how the CO2 emissions of the EU have
    developed since 1990: in total, per person, as a share of the world,
    emissions embedded in imports, and which member states cut the most.
    Make a chart.

Data: Our World in Data, CO2 and Greenhouse Gas Emissions,
      https://github.com/owid/co2-data (CC BY 4.0)
Run:  python eu_report.py
"""

import matplotlib.pyplot as plt
import pandas as pd

DATA = "data/raw/owid-co2-data.csv"
BASE_YEAR = 1990  # base year of the EU climate targets

# The 27 member states and the year they joined
MEMBERS = pd.DataFrame(
    [
        ("Austria", 1995), ("Belgium", 1958), ("Bulgaria", 2007),
        ("Croatia", 2013), ("Cyprus", 2004), ("Czechia", 2004),
        ("Denmark", 1973), ("Estonia", 2004), ("Finland", 1995),
        ("France", 1958), ("Germany", 1958), ("Greece", 1981),
        ("Hungary", 2004), ("Ireland", 1973), ("Italy", 1958),
        ("Latvia", 2004), ("Lithuania", 2004), ("Luxembourg", 1958),
        ("Malta", 2004), ("Netherlands", 1958), ("Poland", 2004),
        ("Portugal", 1986), ("Romania", 2007), ("Slovakia", 2004),
        ("Slovenia", 2004), ("Spain", 1986), ("Sweden", 1995),
    ],
    columns=["country", "joined"],
)


def load(path=DATA):
    return pd.read_csv(path)


def eu_members(df):
    """Rows of the EU member states, with the year each one joined."""
    eu = df.merge(MEMBERS, on="country")
    return eu


def eu_totals(eu):
    """Territorial and consumption-based CO2 of the EU per year, in Mt."""
    return eu.groupby("year")[["co2", "consumption_co2"]].sum(min_count=1)


def per_person(eu):
    """CO2 per person in the EU per year, in tonnes."""
    totals = eu.groupby("year")[["co2", "population"]].sum()
    return 1e6 * totals["co2"] / totals["population"]  # co2 is in Mt


def world_share(df, eu):
    """Share of the EU in global CO2 emissions per year, in percent."""
    world = df.groupby("year")["co2"].sum()
    return (100 * eu_totals(eu)["co2"] / world).dropna()


def embedded_imports(totals):
    """Consumption-based minus territorial CO2 per year, in Mt; only years with data."""
    return (totals["consumption_co2"] - totals["co2"]).dropna()


def biggest_cuts(eu, since=BASE_YEAR):
    """Change in CO2 per person of each member state since a given year."""
    period = eu[eu["year"] > since].sort_values("year")
    first = period.groupby("country")["co2_per_capita"].first()
    last = period.groupby("country")["co2_per_capita"].last()
    cuts = pd.DataFrame({"tonnes": last - first, "percent": 100 * (last / first - 1)})
    return cuts.round(1)


def chart(totals, first, latest, path="eu_report.png"):
    """Bar chart: territorial and consumption-based CO2, first vs. latest year."""
    data = totals.loc[[first, latest]].rename(
        columns={"co2": "Territorial", "consumption_co2": "Consumption-based"}
    )
    ax = data.plot.bar(rot=0, color=["#3D6BA8", "#C25A43"])
    ax.set_ylim(2000, None)  # zoom in, so the change is easy to see
    ax.set_xlabel("")
    ax.set_ylabel("CO2 emissions (t)")
    ax.set_title(f"EU-27: CO2 emissions, {first} vs. {latest}")
    plt.tight_layout()
    plt.savefig(path, dpi=150)


def main():
    df = load()
    eu = eu_members(df)
    first, latest = BASE_YEAR, eu["year"].max()

    totals = eu_totals(eu)
    pp = per_person(eu)
    share = world_share(df, eu)

    print(f"EU report: {len(MEMBERS)} member states, {first} to {latest}\n")

    t0, t1 = totals.loc[first, "co2"], totals.loc[latest, "co2"]
    print("CO2 emissions (territorial)")
    print(f"  {first}: {t0:,.0f} Mt   {latest}: {t1:,.0f} Mt   change: {100 * (t1 / t0 - 1):+.1f} %")

    print("CO2 per person")
    print(f"  {first}: {pp[first]:.1f} t   {latest}: {pp[latest]:.1f} t   "
          f"change: {100 * (pp[latest] / pp[first] - 1):+.1f} %")

    print("Share of world emissions")
    print(f"  {first}: {share[first]:.1f} %   {latest}: {share[latest]:.1f} %")

    imports = embedded_imports(totals)
    last_imports = imports.index.max()
    print("Emissions embedded in imports (consumption-based minus territorial)")
    print(f"  {first}: {imports[first]:,.0f} Mt   {last_imports}: {imports[last_imports]:,.0f} Mt")

    cuts = biggest_cuts(eu)
    print(f"\nBiggest cuts in CO2 per person since {first}, in tonnes")
    print(cuts.nsmallest(3, "tonnes").to_string())
    print(f"\nBiggest cuts in CO2 per person since {first}, in percent")
    print(cuts.nsmallest(3, "percent").to_string())

    chart(totals, first, latest)


if __name__ == "__main__":
    main()