## Project
The aim of the project is to find out, which EU country has reduced its CO₂ emissions per person the most since 2000.

## Setup and commands
- Activate the environment (Windows, Git Bash): `source .venv/Scripts/activate`
- Install packages: `python -m pip install -r requirements.txt`
- Download data: `python src/download.py`
- Clean data: `python src/clean_co2.py`
- Analyse: `python src/analyse.py`
- Tests: `python -m pytest`

## Data
- Source: Our World in Data, CO₂ and Greenhouse Gas Emissions, https://github.com/owid/co2-data, licence CC BY 4.0.
- Pinned version of 2 June 2026: commit `382ee6c662b0ece26e111f263b44c029afad7787`.
- Files: `data/raw/owid-co2-data.csv`, codebook: `data/raw/owid-co2-codebook.csv`.
- Units: `co2` in million tonnes, `population` in persons,
`co2_per_capita` in tonnes per person.
- Not countries: 36 of the 254 entries in `country` have an empty `iso_code`(World, continents, income groups, regions, the European Union (27), International aviation and shipping).
- Exception: Kosovo is a country without `iso_code`, do not drop it silently.
- Years: `co2`, `co2_per_capita` and `population` run until 2024; but not all columns cover the same years

## Rules
- `data/raw/` is read-only: never modify or delete files there.
- No new packages without asking; use only `requirements.txt`.
- Do not change or delete tests to make them pass.
- Print row counts after every filter.
- No silent filling of missing values.
- Never invent URLs; ask instead.
- Do not commit or push. The user reviews the diff and commits.