# AI usage log
## 23.11.2026 · Task 2 · Explore before you code
- Tool and model: GitHub Copilot in VS Code (Interactive mode, Manual permissions)
- Prompts: taken from the lab.
- Accepted: its answers, after checking them. For prompt 3 it asked to run a Python script in the terminal, which only read the columns `country` and `iso_code`. I read it and approved it with *Allow Once*.
- Changed/rejected: none.
- Checked: with my own commands from Hint section after this task.

## 23.11.2026 · Task 3 · AGENTS.md and the fence for the raw data
- Tool and model: GitHub Copilot in VS Code (Interactive mode, Manual permissions)
- Prompts: taken from the lab.
- Output: `AGENTS.draft.md` (82 lines), which was based on my own `AGENTS.md`, because the agent read it. For prompt 2, the agent proposed a Python script that would filter the raw file and overwrite it.
- Accepted: from the draft, the rule not to read the whole data file and the handoff checks (run the tests, check `data/raw/`, read `git diff`). I moved them into my `AGENTS.md` and deleted the draft.
- Changed: I shortened the agent's ideas and wrote them in my own words.
- Rejected: the script of prompt 2, because it would have overwritten `data/raw/`. Also the draft's project details (course name, lab number) and its layout section, which the agent does not need.
- Checked: `sha256sum -c` of `owid-co2-data.csv` was `OK` after the test, and `git status` was clean. `echo "test" >> data/raw/owid-co2-codebook.csv` failed with `Permission denied` after `chmod -R a-w data/raw`.

## 23.11.2026 - 25.11.2026 · Task 4 · Plan, then build in small steps
- Tool and model: GitHub Copilot in VS Code (Interactive mode, Manual permissions); Claude (Anthropic), Claude Sonnet 5.5.
- Prompts: 
  - GitHub Copilot: Three five-part prompts (Goal, Context, Constraints, Done when, First), one per step of the task, each in a fresh session: (1) `src/download.py`, (2) `src/clean_co2.py`, (3) `src/analyse.py`, plus a second prompt for chart styling and a short direct request for new panel titles and axis labels. 
  - Claude: Work through Task 4 step by step with explanations; check my prompt texts for Copilot and the Markdown files, improve where necessary.
- Output: `src/download.py`, `src/clean_co2.py`, `src/analyse.py`,
  `figures/co2_reductions_2000_2024.png` and texts.
- Accepted: The plans for all three steps, created texts and scripts after their check.
- Changed: 
  - GitHub Copilot: In step 3 told the agent not to read `workflow.md` and to restyle the chart.
  - Claude: I shortened the texts to avoid repetitions.
- Rejected: 
  - GitHub Copilot: Creating `tests/test_download.py` (asked twice).
- Checked: ran every script and command manually.

## 26.11.2026 - 27.11.2026 · Task 5 · Verify, then answer
- Tool and model: GitHub Copilot in VS Code (Interactive mode, Manual permissions); Claude (Anthropic), Claude Sonnet 5.5.
- Prompts:
  - GitHub Copilot: taken from the lab
  - Claude: guidance through Task 5 step by step; help with reading the IDEA source (French); proofreading of `workflow.md` and `README.md`
- Output: the final version of *Verify* section in `workflow.md` and the `README.md`.
- Accepted: the structure of the texts, the shortened README answer. I did not ask Claude to check the Credits section, as I had verified the links myself.
- Changed:
  - GitHub Copilot: nothing, I only checked its answer.
  - Claude: I shortened the texts, and rewrote the final versions in my own words.
- Rejected:
  - Claude: its first comparison of the 2.55 million tonnes with our `co2` column (the IDEA figure is CO₂eq, our column is CO₂, so the bases differ).
- Checked: ran the pipeline in a fresh clone and compared the numbers; recalculated Luxembourg's emissions per person by hand from the raw file; read the IDEA analysis myself and compared it with the agent's number (2.55 million tonnes, found).

## 28.11.2026 · Task 6 · Find the silent errors
### Tool and model: Claude (Anthropic), Claude Sonnet 5.5.
- Prompts (summarised): check my explanations of 3 found bugs and help with other ones, explain how to carry out step 2 with the commands from lab 2 where necessary, not with pandas; check my wording of the rows.
- Output: `grep`, `cut` and `awk` commands to compare the report with the OWID rows `European Union (27)` and `World`; explanations of `dropna(subset=["consumption_co2"])`, `.mean()` and of `world_share` and commands to check them; drafts and wording of rows 2-4 of the table.
- Accepted: the command line checks, the wording of rows 2-4
- Changed/rejected: Python scripts.
- Checked: ran all commands on my own `data/raw/owid-co2-data.csv`: `Czechia` vs. `Czech Republic` (26 of 27 countries), last year with `co2` (2024) and with `consumption_co2` (2023), EU-27 per person 9.215 t (`co2 * 1000000 / population`), sum of all rows 154,667 Mt vs. row `World` 22,732 Mt, Denmark 10.402 / 12.437 / 4.847 t (1990 / 1991 / 2023).

### Tool and model: GitHub Copilot in VS Code (Interactive mode, Manual permissions)
- Prompt: taken from the lab.
- Output: a list of 7 points (Czechia missing, 2024 discarded by `dropna`, unweighted per-person mean, wrong world-share denominator, `>` instead of `>=`, "imports" is a net difference, chart unit and axis). No file was changed.
- Accepted: points 1-5 and 7 as matching my own list; its evidence is documented in the second table of `bug-hunt.md`.
- Changed: nothing was taken over as code.
- Rejected: point 6 (imports) is not counted as one of the errors. `consumption_co2 - co2` equals the OWID column `trade_co2` for EU-27 (1990: 489.914 Mt, 2023: 817.2 Mt), so the number is correct. The codebook defines `trade_co2` as "annual net carbon dioxide (CO₂) emissions embedded in trade", so only the label "embedded in imports" is imprecise (it is a net value). Checked with `grep -E "^European Union \(27\),(1990|2023)," data/raw/owid-co2-data.csv | cut -d, -f1,2,8,22,78` and `grep -i "^trade_co2," data/raw/owid-co2-codebook.csv`.
- Checked: its share numbers 16.30% (1990) and 6.30% (2023) are for 26 countries. OWID's `share_global_co2` of `European Union (27)` is 17.025% and 6.523%, the difference equals the share of Czechia (0.723% and 0.218%).