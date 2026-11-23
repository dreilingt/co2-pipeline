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