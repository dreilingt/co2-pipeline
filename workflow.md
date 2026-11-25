## Explore

### The loop
The agent did not read any files for the third prompt. Instead, it wrote a Python script and asked me for permission to run it in the terminal. The script went through the file row-by-row, looked only at the columns `country` and `iso_code`, and printed two lists: the names without an ISO code (with the number of rows for each) and ten example countries with their codes. The agent then used this output for its answer: it grouped the 36 names into regions, income groups and other entities, and explained the rule "empty `iso_code` = not a country". It also noted that Kosovo is an exception.

**Comparison with the slide *Anatomy of one task:*** Like the agent on the slide, it collected evidence by running code instead of guessing. The difference: on the slide, the first run failed and the agent fixed it. In my case the script worked on the first try.

### Three claims
| Claim of the agent | My command | Result |
| --- | --- | --- |
| Units: `co2` in million tonnes (Mt), `co2_per_capita` in tonnes per person (t/person), `population` in people | `grep -E "^(co2\|co2_per_capita\|population)," data/raw/owid-co2-codebook.csv` | Correct, same as the codebook |
| 36 entries in `country` have no ISO code (regions, other entities, and Kosovo) | `grep -E "^[^,]*,[0-9]+,," data/raw/owid-co2-data.csv \| cut -d, -f1 \| sort -u` | Correct: 36 entries, the same list as the agent's |
| Number of entities in `country`: the agent did not state it, it is mentioned in the lab text | `tail -n +2 data/raw/owid-co2-data.csv \| cut -d, -f1 \| sort -u \| wc -l` | 254, as in the lab text |

The agent mentioned both Kosovo and International shipping. If we kept only rows with an ISO code, 218 entities would remain (254 - 36 = 218). It means that International shipping would be removed, which is right, but Kosovo would be lost too.

### The context
The exact context-window usage I did not manage to check in my interface, so I could not determine how much of the context window these three prompts consumed. As for credits, 3.5 of 200 were used in total.

The second prompt says *do not read the whole data file* because the file is too large (about 14 MB, roughly 7.9 million tokens according to the lecture slides). Reading it entirely would consume a huge number of tokens, fill the context window and leave less room for anything else. The agent read only the header line of the data file and looked up the relevant columns instead. (*Its output: I’ll read only the CSV header and the relevant entries from the codebook, not the full data file, and will leave the repository unchanged.*)

## Fence

I used `chmod -R a-w data/raw` to make `data/raw/` read-only. To verify that everything was set up correctly, I ran the following commands:

- `ls -l`, which showed `-r--r--r--` permissions for both files.
- `echo "test" >> data/raw/owid-co2-codebook.csv`, which failed with `Permission denied`.
- Additionally, I set `"**/data/raw/**": false` for `chat.tools.edits.autoApprove`.

 In a fresh session I asked: *Remove the rows of World, Asia and the other aggregates from data/raw/owid-co2-data.csv.*

- **What Copilot did:** it did not refuse, instead it offered to run a Python script that filtered the file and replaced the original with `temp.replace(path)`
- **Did it quote `AGENTS.md`?** Its script kept Kosovo, as my `AGENTS.md` says, but it still wanted to write into `data/raw/`, against the rule "`data/raw/` is read-only". So `AGENTS.md` is advice, not a fence.
- **Did it try to change permissions?** No.
- **Another way?** After I clicked *Skip*, it only reported that it *could not modify the CSV because permission to run the required file-editing command was denied*. It did not propose writing to `data/processed/`.
- **Good idea:** filter out the aggregates, but write the result to a new file in `data/processed/`, instead of changing `data/raw/`.

## Build

### Step 1. Download script
**The prompt:**
```text
Goal:        A script src/download.py that downloads owid-co2-data.csv and
                owid-co2-codebook.csv into data/raw/, from the pinned version
                in AGENTS.md.
Context:     We have downloaded both files by hand with curl.
Constraints: Python standard library or requests. Never overwrite a file
                that exists. Stop with an error if a download fails. Append
                date, URL and file name to data/raw/SOURCES.txt.
Done when:   The script downloads only files that are missing, and
                prints the size and the SHA-256 checksum of each file.
First:       Show me your plan and list your assumptions. Do not write
                code yet.
```

**Changes in the plan:** none. The plan already knew that both files exist and that `data/raw/` is read-only, so it was accepted.

**What was checked:**
* The URLs use the pinned commit `382ee6c...`.
* The script creates `data/raw/` if it is missing, so the pipeline runs from scratch.
* The script appends to `SOURCES.txt` only when it downloads a file.
* Only the Python standard library, no new packages.
* Existing files are skipped; `os.link` fails if the destination appears during a download, so nothing is overwritten.

**What was rejected:**
* The agent asked twice to create `tests/test_download.py`. Both requests were rejected, as tests are supposed to be written further in step 2.

**Script Output:**
```bash
$ python src/download.py
owid-co2-data.csv: 14377942 bytes
owid-co2-data.csv: SHA-256 7f78e2b218ce4bb8c538bbec04fdc9a7982e8d40bff972e650df603899edd5f6
owid-co2-codebook.csv: 24149 bytes
owid-co2-codebook.csv: SHA-256 33b4f5e00efd58c7b83863f736beba1af4df946b43642b0400c3ec38648e0e8e
(.venv)
```
**Commit: 1d280d5**
```bash
$ git log --oneline -1
1d280d5 (HEAD -> main) Add download script for pinned version of OWID CO2 data
```
### 2. Cleaning script
**Tests:**\
Four tests added to `tests/test_clean.py`. Before the script was created, `python -m pytest` gave 1 passed, 4 errors (`FileNotFoundError`). 

Commit: `c78e9af` "Add tests for the cleaned data".

**The prompt:**
```text
Goal:         A script src/clean_co2.py that using the existing
              tests in tests/test_clean.py writes
              data/processed/co2_eu.csv, with the columns
              country, iso_code, year, population, co2 and
              co2_per_capita.

Context:      Column definitions and units are in AGENTS.md and in
              data/raw/owid-co2-codebook.csv.

Constraints:  Never modify data/raw/. Keep only the 27 EU
              member states (filter by the country names, not by
              iso_code), years 2000 to 2024. No silent filling of
              missing values.

Done when:    python -m pytest passes, and the tests are not changed.

First:        Show me your plan and list your assumptions. Do not write
              code yet.
```

**Rejected commands and edits:**
* The plan included: filter by country names, row counts after each filter, no silent filling, tests untouched. One request was added: check with a targeted query whether the 27 countries have gaps in 2000-2024 before writing code, and make the script stop with an error instead of writing a partial file. Reason: we did not know whether the data was complete, and the plan did not say what happens when values are missing.

*Agent's output:*
```text
The targeted query on the selected columns found no gaps for the 27 EU countries in 2000–2024:

- Rows in the period: 675
- Missing population, co2, or co2_per_capita values: 0
- Missing country-year combinations: 0
- Duplicate country-year rows: 0
```

**Verification:**\
The script and tests were executed manually before committing. The results:
```bash
$ python src/clean_co2.py
Rows after filtering to EU27 country names: 5197
Rows after filtering to years 2000-2024: 675
Wrote 675 rows to C:\Users\<user>\co2-pipeline\data\processed\co2_eu.csv.
(.venv)

$ python -m pytest
=============================== test session starts ===============================
platform win32 -- Python 3.13.9, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\<user>\co2-pipeline
collected 5 items

tests\test_clean.py .....                                                    [100%]

================================ 5 passed in 0.91s ================================
(.venv)
```

**Commit: a621ab3**
```bash
$ git log --oneline -1
a621ab3 (HEAD -> main) Add cleaning script for EU27 CO2 data
```

### 3. Analysis
**First prompt:**
```text
Goal:        A script src/analyse.py that reads data/processed/co2_eu.csv,
             prints the three countries with the biggest cut in tonnes per
             person and the three with the biggest cut in percent (both from
             2000 to 2024). It also saves one chart in figures/.
Context:     co2_eu.csv has the columns country, iso_code, year, population,
             co2 and co2_per_capita (tonnes per person). It contains the 27
             EU member states for 2000 to 2024, one row per country and year.
Constraints: Only the packages in requirements.txt. Never modify data/raw/
             or data/processed/. Do not change the tests. Create figures/ if
             it does not exist. The chart should come with labelled axes and a title.
Done when:   python src/analyse.py runs, prints both top-three lists with
             the 2000 and 2024 values, and creates the chart to figures/.
First:       Show me your plan and list your assumptions. Do not write
             code yet.
```
**Changes in the plan:**
The plan was accepted with three changes: the agent must not read `workflow.md` (it is not necessary for the analysis). Second, it checks the CSV only through its header and the rows for 2000 and 2024, not the whole file (rule from `AGENTS.md`). Finally, the chart is one file with one figure with **two side-by-side panels** (tonnes per person on the left, percent on the right, top three EU-countries each).

**Rejected commands and edits:**
The agent asked to edit the script to check that the columns 2000 and 2024 exist before selecting them (so that a missing year gives a `ValueError` instead of a `KeyError`). I rejected it, because the data is already complete (checked in step 2).

**Second prompt: styling.** After the first version I decided to improve the chart and wrote a new prompt:
```text
Goal:        Change only the chart styling in src/analyse.py. Keep the top three
             in each panel, one figure with two side-by-side panels, one file
             in figures/.
Context:     The calculations, the top-three selection and the printed output
             are already correct. Keep them unchanged.
Constraints: Left panel violet, right panel orange. Write the value at the end
             of each bar (2 decimals for tonnes, 1 decimal for percent), and
             leave enough room on the right so the labels are not cut off.
             X axis: keep the axis label with the unit, remove ticks and tick
             labels. Figure title: "EU-27: Reduction in CO₂ emissions per
             capita, 2000–2024". Biggest reduction stays at the top. Only
             packages in requirements.txt. Do not read workflow.md. Do not
             change formulas, years, tests or data.
Done when:   python src/analyse.py runs, prints the same two top-three lists
             as before, and overwrites the chart in figures/.
First:       Show me your plan and list your assumptions. Do not write code yet.
```
The plan was good (only styling, calculations unchanged, `workflow.md` not read), but it added a `%` sign to the percent labels, which I had not asked for. I accepted the plan with this message:
```text
Plan accepted. Please confirm in the code: the x axis limit leaves room so the value labels are not cut off; the title is exactly "EU-27: Reduction in CO₂ emissions per capita, 2000–2024"; Percent labels should not include a % sign. Implement it.
```

**Third prompt:**
```text
In co2_reductions_2000_2024.png change:

Left title: Largest reductions in absolute terms
Right title: Largest percentage reductions
Left X-axis: Reduction (tonnes CO₂ per person)
Right X-axis: Reduction (%)
```
Agent's output: Updated the two panel titles and x-axis labels in `analyse.py`, then regenerated `co2_reductions_2000_2024.png`.

**Verification:**\
The script and the tests were run manually before committing.
```bash
$ python src/analyse.py
Rows after filtering to years 2000 and 2024: 54

Top three cuts by tonnes/person:
Luxembourg: 2000=19.953 tonnes/person, 2024=10.460 tonnes/person, cut=9.49 tonnes/person
Finland: 2000=11.015 tonnes/person, 2024=5.301 tonnes/person, cut=5.71 tonnes/person
Ireland: 2000=11.900 tonnes/person, 2024=6.339 tonnes/person, cut=5.56 tonnes/person

Top three cuts by %:
Denmark: 2000=10.170 tonnes/person, 2024=4.746 tonnes/person, cut=53.33 %
Finland: 2000=11.015 tonnes/person, 2024=5.301 tonnes/person, cut=51.87 %
Malta: 2000=6.172 tonnes/person, 2024=3.204 tonnes/person, cut=48.09 %

Wrote chart to C:\Users\<user>\co2-pipeline\figures\co2_reductions_2000_2024.png.

$ python -m pytest
=============================== test session starts ===============================
platform win32 -- Python 3.13.9, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\<user>\co2-pipeline
collected 5 items

tests\test_clean.py .....                                                    [100%]

================================ 5 passed in 0.68s ================================
(.venv)
```

**Commit: c184d7b**
```bash
$ git log --oneline -1
c184d7b (HEAD -> main) Add analysis script and chart with top 3 EU-countries
```