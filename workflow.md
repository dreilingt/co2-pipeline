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

### Step 1. Download
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