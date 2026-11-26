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