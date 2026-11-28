## Bug Hunt
Manual review of the script `eu_report.py`, based on the slide *Review checklist for data code*.

| # | Function | Row of the checklist | What goes wrong | Evidence |
| --- | --- | --- | --- | --- |
| 1 | `eu_members` | Joins and merges | Data in rows with `Czechia` is missed, because in `MEMBERS` it is `Czech Republic` instead of `Czechia`. The report keeps saying "27 EU member states" | `cut -d, -f1 data/raw/owid-co2-data.csv \| sort -u \| grep -i czech` gives `Czechia` |
| 2 | `eu_members` | Missing values | `dropna(subset=["consumption_co2"])` drops every row without consumption-based CO2 for all sections, although only the imports section needs it. `consumption_co2` starts in 1990 and ends in 2023, so the report ends in 2023 although territorial CO2 exists for 2024. | `awk -F, '$1=="European Union (27)" && $8!="" {y=$2} END{print y}' data/raw/owid-co2-data.csv` gives 2024, the same with `$22` gives 2023 |
| 3 | `per_person` | Aggregation | `.mean()` calculates an unweighted average of the countries' per-capita values (a mean of ratios), so each country contributes equally regardless of its population: Luxembourg counts as much as Germany. The correct EU value is total CO2 divided by total population. | `awk -F, '$1=="European Union (27)" && ($2==1990 \|\| $2==2023) {print $2, $8*1000000/$4}' data/raw/owid-co2-data.csv` gives 9.21 and 5.51 t, the script reports 9.9 and 5.4 t |
| 4 | `world_share` | Filters / Aggregates | `world = df.groupby("year")["co2"].sum()` sums all rows in the dataset instead of selecting the World row. This results in an incorrect denominator and underestimates the EU's share of global emissions. | `awk -F, '$2==1990 {s+=$8} END{print s}' data/raw/owid-co2-data.csv` gives 154667; `grep "^World,1990," data/raw/owid-co2-data.csv \| cut -d, -f1,2,8` gives `World,1990,22732.145` |
| 5 | `biggest_cuts` | Filters | `eu["year"] > since` excludes 1990 (BASE_YEAR), so the comparison starts in 1991 although the report says "since 1990". It should be `>=`. | `period = eu[eu["year"] > since]` with `since = BASE_YEAR = 1990` |
| 6 | `chart` | Units and scales | The y-axis label says "CO₂ emissions (t)", but the values are expressed in million tonnes (Mt). Additionally, the y-axis starts at 2000 rather than 0. | `ax.set_ylabel("CO₂ emissions (Mt)")`, `ax.set_ylim(0, None)` |

## Agent's Review

| # | Error | Manual Review | Agent's Review | Evidence given by the agent |
| --- | --- | --- | --- | --- |
| 1 | `Czech Republic` instead of `Czechia` | found | found | 26 of 27 members included, because Member name uses "Czech Republic", while the raw data uses "Czechia" |
| 2 | 2024 data is discarded | found | found | `consumption_co2` is unavailable in 2024, so the report ends in 2023 |
| 3 | unweighted `.mean()` in `per_person` | found | found | 1990: mean 9.870 t, weighted 9.046 t (26 countries), OWID EU-27 9.215 t |
| 4 | incorrect `world_share` denominator | found | found | 1990: script reports 2.40%, correct 26-country share is 16.30%; 2023: script reports 0.99%; correct 26-country share is 6.30% |
| 5 | `>` instead of `>=` | found | found | This changes the ranking: for example, Denmark appears in the 1991-based top three for tonnes, but Germany or Lithuania rank differently against 1990. |
| 6 | misleading chart | yes | yes | Y-axis label says `t` (tonnes) but values are `Mt` (milliom tonnes); the 2000 baseline exaggerates differences |

Agent's statement, which was not in our list: *"Emissions embedded in imports" is only a net difference. The calculation prints `consumption_co2` - `co2`. According to the `codebook`, this is consumption-based minus territorial emissions, i.e. net imported-minus-exported emissions—not gross import emissions.*

#### Checked number

The agent reports that the "correct 26-country share" of the EU in 1990 is 16.30%.

The agent's arithmetic is right: 3,706 Mt (EU sum of the script, 26 countries) / 22,732 Mt (`World`) = 0.1630, i.e. 16.30%. However, 3,706 Mt does not include Czechia, because the script drops it (bug #1) => 16.30% is the share of 26 countries, not of 27.

OWID gives the share of the whole EU-27 in the column `share_global_co2`: 17.025% in 1990. The difference is 17.025 - 16.30 = ca. 0.72. The same column gives the share of Czechia alone: 0.723% in 1990. The difference (about 0.72) equals the share of Czechia (0.723) => the missing part is Czechia.

The same holds for 2023: 6.523% (EU-27) - 6.30% (agent) is about 0.22, and Czechia's share is 0.218%.

Conclusion: the agent's number is not wrong arithmetically, but it inherits bug #1 (Czechia is missing). The correct share of the EU-27 is 17.025% (1990) and 6.523% (2023).

Command for the OWID numbers: `grep -E "^(Czechia|European Union \(27\)),(1990|2023)," data/raw/owid-co2-data.csv | cut -d, -f1,2,54`