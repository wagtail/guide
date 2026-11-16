# Reading production snapshot results

Each folder here is one run of [`agent-readiness-snapshot.yaml`](../agent-readiness-snapshot.yaml), named after the day it ran. This page explains what the numbers in each folder mean, how much they move between runs, and the patterns worth looking for. Examples come from [20261115](20261115/README.md).

## What's in a folder

- `README.md`: when the run happened, what the site was at, the headline table and findings. Written by hand.
- `summary.md`: the output of `summarize.py`, unedited apart from formatting. Every table is described below.
- `runs.csv`: one row per run, for your own analysis.

The raw promptfoo output, with every answer and tool call, is too large for the repository and stays with whoever ran the snapshot.

## Words used

- **Arm**: one harness and model, like `claude-code/opus-5.5`. The name comes from the other agent readiness configs, where arms are variants of one experiment.
- **Case**: one question from [`tests.yaml`](../tests.yaml), like `troubleshoot-locked-page`. There are 33.
- **Run**: one arm answering one case once. Every case runs five times per arm, so each arm has 165 runs, and a snapshot of eight arms has 1,320.
- **Repeat**: one pass through all 33 cases. `repeat` 0 to 4 in `runs.csv`.

Cases are grouped two ways, and the groups are not the same size:

| Task            | Cases | What it asks                                                       |
| --------------- | ----: | ------------------------------------------------------------------ |
| information     |    15 | How to do something, or what something is                          |
| troubleshooting |     8 | Why something doesn't work as expected                             |
| releases        |     6 | What changed in Wagtail 7.3 to 8.0, which models know little about |
| negative        |     3 | Developer questions the developer docs answer, not the guide       |
| bridge          |     1 | A developer question the guide answers, linking to developer docs  |

| Framing        | Cases | The prompt                                                |
| -------------- | ----: | --------------------------------------------------------- |
| site-named     |    19 | Points the agent at the guide                             |
| site-not-named |     9 | Doesn't mention the guide, so the agent has to find it    |
| site-start     |     5 | Sends the agent to guide.wagtail.org to look something up |

## When a run passes

A run passes when its answer passes every check. Each case has:

- **Facts**: words any correct answer uses, matched as text. For example, "go-live" for scheduling a page.
- **Citation**: the URL of the guide page that answers the question. Versioned guide URLs like `/en-latest/` count, as they redirect to the right page.
- **Judge**: a rubric for the nuance, graded by Claude Sonnet 5.5 with no tools. When it can't tell, it passes the answer and says `UNKNOWN:`.

Every answer also has to be non-empty, and must not link to the old editor manual on docs.wagtail.org or to guide `.html` pages, which don't exist. So a run can pass all three of facts, citation and judge and still fail.

The trace columns never fail a run: they record what the agent did, not whether it was right.

## The tables in summary.md

### Results per arm

One row per arm, over all 165 runs.

- **Pass**: share of runs that passed. The `± n` is the standard deviation across the five repeats: how much the pass rate moved from one pass through all cases to the next. One case is 3 points of a repeat's pass rate.
- **Facts, Citation, Judge**: share of runs that passed each kind of check. A gap between them says why an arm fails. Haiku's facts are at 98% but its citations at 89%: it knows the answers, but often cites the wrong page.
- **Cost/answer**: mean cost of a run, at API list prices, without the judge. For Claude Code, this includes the Haiku calls `WebFetch` makes to summarise pages, and search fees. It's what the tokens would cost through the API, even when the run used a subscription login. `0.0¢` means OpenCode has no price for the model, not that it was free.
- **Duration**: mean time per run. It depends on the provider's load as much as the model, so compare it within a run, not between snapshots.
- **Tool calls**: mean tool calls per run, as each harness reports them. Codex's searches and page opens happen on OpenAI's servers, so it looks like it does less than it does.

### Median of 5 runs per case

The headline numbers. Each case gets the result of its middle run.

- **Cases passed**: cases where at least three of five runs passed. This ignores the odd unlucky run, but it's coarse. A case whose answers are right 60% of the time passes the median 68% of the time, so it can flip between snapshots without anything changing. One or two cases between arms or snapshots is noise.
- **Median duration, Median cost**: each case's middle run, then the middle case. These ignore the occasional very long or expensive run, so they're lower than the means in the first table.
- **Suite duration, Suite cost**: the cases' medians added up, what one typical pass through all 33 cases takes. Arms ran in parallel, so the suite durations don't add up to the run's wall clock time.

### Pass rate by task, and by framing

Share of runs passed, per group. Check the group size before reading anything into a number: `bridge` is one case, so 60% is 3 of 5 runs, and `negative` is three cases. `information` and `site-named` are large enough to compare.

Most arms are good at everything when the prompt names the guide. The gaps show up when it doesn't, and on troubleshooting, where the answer isn't in a page's title.

### Surfaces reached

What each run's trace shows the agent doing. Most rows are the share of runs that reached a surface at least once. The counts (`citations_not_fetched`, `fetch_errors`, `curl_calls`, `permission_denials`) are means per run.

Surfaces are classified from the URLs the agent fetched, by [`graders/trace_columns.py`](../graders/trace_columns.py):

| Column                              | Counts runs that…                                                                             |
| ----------------------------------- | --------------------------------------------------------------------------------------------- |
| `web_search_used`                   | used a search tool: Claude Code's `WebSearch`, Codex's built-in search, OpenCode's Exa search |
| `homepage_reached`                  | fetched `guide.wagtail.org/` or `/en/`                                                        |
| `docs_reached`                      | fetched any guide page, as HTML or Markdown                                                   |
| `markdown_page_reached`             | fetched a page's Markdown URL, ending `/markdown/` or `.md`                                   |
| `llms_txt_reached`                  | fetched `/llms.txt`                                                                           |
| `llms_full_reached`                 | fetched `/llms-full.txt`                                                                      |
| `skill_reached`                     | fetched the agent skill under `/.well-known/agent-skills/`                                    |
| `mcp_used`                          | called a tool of the guide's MCP server                                                       |
| `sitemap_reached`                   | fetched `/sitemap.xml`                                                                        |
| `robots_txt_reached`                | fetched `/robots.txt`                                                                         |
| `well_known_reached`                | fetched anything else under `/.well-known/`                                                   |
| `openapi_reached`                   | fetched `/openapi.json` or the API                                                            |
| `dev_docs_reached`                  | fetched a page on docs.wagtail.org                                                            |
| `github_copy_reached`               | read the guide's content from GitHub instead of the site                                      |
| `external_reached`                  | fetched any other site                                                                        |
| `answer_cites_guide`                | gave an answer with at least one guide URL                                                    |
| `answer_grounded`                   | cited a guide URL the agent was seen to fetch                                                 |
| `citations_not_fetched`             | (mean) guide URLs cited but not seen fetched: from search results, memory, or guesses         |
| `versioned_url_reached`             | fetched a versioned guide URL like `/en-latest/` or `/en-6.3.x/`, which redirects             |
| `answer_cites_versioned_url`        | cited one                                                                                     |
| `legacy_editor_manual_reached`      | fetched an old editor manual page on docs.wagtail.org                                         |
| `answer_cites_legacy_editor_manual` | cited one, which fails the run                                                                |
| `fetch_errors`                      | (mean) fetches that failed                                                                    |
| `curl_calls`                        | (mean) shell commands that use `curl`                                                         |
| `permission_denials`                | (mean) tool calls the harness refused, as Claude Code reports them                            |

Things the table can't show:

- **Markdown served by content negotiation counts as `docs_reached`, not `markdown_page_reached`.** Claude Code's and OpenCode's fetch tools ask for Markdown, and the guide serves it from the page's usual URL. In 20261115, OpenCode got Markdown this way for 122 of its 231 fetches of usual page URLs. `markdown_page_reached` only counts agents that used the explicit Markdown URL, which they mostly find in llms.txt.
- **Server-side reads are invisible.** Codex searches and opens pages on OpenAI's servers, and Claude Code's `WebSearch` runs on Anthropic's. Codex's 0% for llms.txt and Markdown means it never fetched them by URL, not that its search didn't use them. That's also why Codex's `answer_grounded` is low (5–23%) while its `answer_cites_guide` is as high as the others, and why its `citations_not_fetched` is above 1.
- **Claude Code's `WebFetch` returns a summary of the page**, written by Haiku, not the page. Links on the page are often lost, so an agent can't always follow them.

### Judge couldn't tell

Runs the judge passed with `UNKNOWN:`. They count as passes, so read them in the raw output: if an answer is wrong, the pass rate is too high. A case that keeps turning up here probably needs a clearer rubric.

### Failed runs per case

Failed runs out of five, per case and arm. Blank means all five passed. Read across a row to tell a hard case from a weak arm:

- A row with failures in most columns is a problem with the case or the site, not the models. In 20261115, `troubleshoot-recover-deleted-document` fails for six of eight arms: search results lead to the old editor manual, not the guide.
- A column with failures in many rows is a weaker arm: Haiku and DeepSeek in 20261115.
- `5/5` for one arm on a case the others pass is that arm's blind spot, like Luna on `troubleshoot-locked-page`. The transcripts usually show one wrong page it always goes to.

The heading says "outside the baseline" because `summarize.py` is shared with configs that have a no-tools baseline arm. Snapshots don't have one, so every arm is listed.

## runs.csv

One row per run, with the same values as `summary.md`, so you can slice the data your own way, for example by case and arm together.

| Column                                     | Value                                                                                    |
| ------------------------------------------ | ---------------------------------------------------------------------------------------- |
| `arm`, `case`, `task`, `framing`, `repeat` | Which run this is                                                                        |
| `success`                                  | 1 if the run passed every check                                                          |
| `error`                                    | 1 if the harness failed to produce an answer, like a timeout. These are also `success` 0 |
| `facts`, `citation`, `judge`               | Score for each kind of check, from 0 to 1                                                |
| `duration_s`, `cost_usd`                   | Time and cost of the run. `cost_usd` is 0 when the harness has no price for the model    |
| `prompt_tokens`, `completion_tokens`       | Tokens, as the harness reports them                                                      |
| `tool_calls`                               | Tool calls in the trace                                                                  |
| `web_search_used` to `permission_denials`  | The trace columns above, as 0 or 1, or a count                                           |

To open it in a spreadsheet, or with `uv run python`:

```python
import csv
from collections import Counter

rows = list(csv.DictReader(open("runs.csv")))
fails = Counter((r["case"], r["arm"]) for r in rows if r["success"] == "0")
```

## Patterns to look for

### Each harness has a signature

The trace columns separate harnesses more clearly than models. In 20261115:

- **Claude Code** with Fable, Opus and Sonnet goes straight to the guide: `web_search_used` is 0–8%, `docs_reached` 76–84%, and `answer_grounded` close to `answer_cites_guide`. Haiku behaves more like the other harnesses, searching in 75% of runs.
- **Codex** searches in almost every run and rarely fetches anything itself.
- **OpenCode** mixes Exa search with fetches. Its fetch tool returns whole pages, where Claude Code's returns a summary.

A change in an arm's signature between snapshots usually means the harness or model changed, not the site. Check the versions in each folder's README before blaming or crediting the site.

### Guessed URLs

`versioned_url_reached` is high for Fable and Opus (80–84%): they guess `guide.wagtail.org/en-latest/…` URLs, following the developer docs' URL pattern, and they work because the guide redirects them. If those redirects broke, these arms would lose correct answers, and nothing else in the table would warn you.

### Answers that are right but don't cite the guide

When `facts` is high and `citation` is lower, the agent knows the answer but cited another page: the developer docs, an old editor manual page, or a blog post. Check `dev_docs_reached` and `answer_cites_legacy_editor_manual` for the same arm. These are the failures the site can fix, by making the right guide page easier to find than the alternatives.

### Framing gaps

The difference between `site-named` and `site-not-named` is how much an arm depends on being told where to look. In 20261115, every arm passes at least 87% of runs that name the guide, but Haiku, Luna and DeepSeek pass 60–73% of the ones that don't. That's discoverability: search results, and pages from other sites that link to the guide.

### Agent readiness features in use

`llms_txt_reached`, `markdown_page_reached`, `mcp_used` and `skill_reached` show which of the guide's agent readiness features agents find on their own. Read them with the content negotiation caveat above: agents can read Markdown without any of these columns moving.

## Comparing snapshots

Each snapshot is a sample. Before reading a difference as a change:

- **Is it bigger than the noise?** With 165 runs per arm, an arm's pass rate moves by up to about 3 points at 96%, and up to about 6 points at 82%, from chance alone (95% of the time). A trace column at 30% moves by up to about 7 points. Cases passed moves by one or two cases.
- **Does it have a cause?** List what changed between the snapshots: site commits, harness versions, models. A difference that lines up with one of them, and shows up in the trace columns that change would affect, is worth reporting. A pass rate that moves on its own usually isn't.
- **Look at the mechanism, not just the score.** Site changes tend to show up first in how agents navigate, and only sometimes in whether they're right. Compare the trace columns per arm, then read a few transcripts from each snapshot for the same case and arm.

To compare two snapshots side by side, pass both runs' raw output to `summarize.py` after relabelling one of them, as described in [Running one arm, or testing a site change](../README.md#running-one-arm-or-testing-a-site-change).
