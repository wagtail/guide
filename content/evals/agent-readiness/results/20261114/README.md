# Production snapshot: 20261114

The same snapshot as [20261117](../20261117/README.md), rerun with page Markdown turned off, so agents only get HTML pages: same config, cases, versions and judge. Despite its name, it ran after 20261117: "14" marks the HTML-only run. See [Reading production snapshot results](../README.md) for what the tables and columns mean.

- **Runs:** 1,320: eight models, 33 cases, five repeats each. Every run produced an answer.
- **When:** 16 November 2026, 23:55 GMT, to 17 November, 01:07 GMT, against the live site.
- **Site:** `main` at `ca2b54f`, which turns off page Markdown behind a setting. Requests for Markdown get the HTML page, `/markdown/` URLs return 404, and llms.txt links to the HTML pages. llms.txt and llms-full.txt are still served, and HTML pages still link to them. Before the run, llms.txt was cleared from the server cache and purged from Cloudflare, which still had copies with `/markdown/` links.
- **DeepSeek:** DeepSeek V4.1 Flash 1017 (`deepseek/deepseek-v4.1-flash-1017` on TensorX), with thinking off: it reports 0 reasoning tokens. That's TensorX's default, and the config doesn't change it.
- **Versions:** promptfoo 0.124.1, Claude Agent SDK 0.3.325 (Claude Code 2.1.325), Codex SDK and CLI 0.169.0, OpenCode 1.19.5. Judge: Claude Sonnet 5.5.

## Results

A case passes when at least three of its five runs pass. Costs are at API list prices, without the judge: $72.72 for all runs, against $72.56 for 20261117, plus an estimated $0.85 to $3.03 for DeepSeek ($1.07 to $3.82).

| Harness / model                     | Cases passed | Runs passed | Median duration | Median cost |
| ----------------------------------- | -----------: | ----------: | --------------: | ----------: |
| Claude Code / Fable 5.2             |   32/33 (33) |   96% (99%) |             23s |       20.4¢ |
| Claude Code / Opus 5.5              |   32/33 (32) |   98% (96%) |             23s |        9.7¢ |
| Claude Code / Sonnet 5.5            |   32/33 (32) |   93% (95%) |             20s |        4.7¢ |
| Claude Code / Haiku 5.5             |   30/33 (27) |   84% (81%) |             22s |        1.6¢ |
| Codex / Sol 6.1                     |   33/33 (33) |   99% (99%) |              8s |        4.7¢ |
| Codex / Luna 6                      |   31/33 (31) |   92% (91%) |             10s |        0.3¢ |
| OpenCode / Qwen 3.8 27B             |   32/33 (33) |   96% (95%) |             39s |        0.9¢ |
| OpenCode / DeepSeek V4.1 Flash 1017 |   30/33 (30) |   89% (86%) |             10s |    0.4–1.6¢ |

20261117 results in brackets. DeepSeek's costs are estimates, as in [20261115](../20261115/README.md#results). [summary.md](summary.md) has the full tables, and [runs.csv](runs.csv) one row per run.

## Findings

**Answers are as good without page Markdown.** Every arm's pass rate is within 3 points of 20261117, well within run-to-run variation, and Haiku's cases passed went back up from 27 to 30, as its cases near the threshold flipped again. No case moved in a way that points to HTML: `info-keyboard-shortcuts` failed 5 of Fable's, Opus's and Sonnet's 15 runs (3 to 4 in the earlier snapshots), and `releases-7-4-incomplete-blocks` 2 (1, 7 and 0). `troubleshoot-locked-page` failed 8 of 40 runs, against 15 or 16 in every earlier snapshot, mostly because Haiku passed all five.

**The harnesses convert HTML to Markdown themselves.** Claude Code's `WebFetch` converts each page to Markdown before Haiku summarizes it, and OpenCode's `webfetch` returns Markdown by default: none of its 385 fetches of guide pages returned HTML tags. So models still read Markdown, just the harness's conversion of the whole page, menu included, instead of the guide's. Codex doesn't fetch pages itself: its web search reads them on OpenAI's servers, so it can't tell the difference, and its results didn't move.

**Costs didn't change.** Each model's total moved by 2% or less, except Haiku's (4%) and Qwen's (9%), which are 16 cents or less. Pages without the site map are smaller for OpenCode: among runs that read guide pages, DeepSeek's median prompt tokens went from 37,100 to 32,500, and Qwen's from 47,000 to 43,100, back to 20261116's 42,900.

**Navigation is closer to 20261116.** Agents pick the next page from the HTML menu, which links to every page, as the site map did. Claude Code fetched 1,525 guide pages, against 1,406 in 20261117, and Fable, Opus and Sonnet made 0.3 to 0.4 more tool calls per run. Agents read llms.txt in at most 2% of runs, as in 20261117.

**Claude Code cites `/en-latest/` URLs more often.** Page Markdown starts with a `Page URL`, the page's canonical `/en/` URL, and llms.txt tells agents to cite it. Without it, agents cite the URL they fetched, which for Fable and Opus is usually a guessed `/en-latest/` one. Among Claude Code answers that cite the guide, Fable cited a versioned URL in 89 of 143 (60 of 145 in 20261117), Opus 97 of 149 (61 of 146), Sonnet 38 of 144 (23 of 144) and Haiku 38 of 138 (28 of 133). Those URLs work, but redirect.

**Unchanged from 20261117:**

- The old editor manual still costs answers: `troubleshoot-recover-deleted-document` fails 20 of 40 runs (20 before).
- Fable and Opus still guess `/en-latest/` URLs in 78–84% of runs.
- No model used the MCP server or the agent skill.
- Smaller models still struggle when the prompt doesn't name the guide: Haiku passes 82% of those runs, Luna 73%, DeepSeek 73%.

## What to try next

- Decide whether page Markdown is worth keeping on its merits other than answer quality, like the `Page URL` that agents cite, since this snapshot can't tell it apart from HTML.
- If it stays off, update llms.txt's instructions, which still tell agents to fetch each page's Markdown and cite its `Page URL`, and the "Documentation formats" page, which llms-full.txt also includes.

## Reading these results

- **Same caveats as [20261115](../20261115/README.md#reading-these-results).** Five repeats per case, Claude Code on a subscription login, Claude Code's token counts including Haiku summarizing pages, and trace columns that can't see server-side reads.
- **Cloudflare served the homepage from before the change for part of the run.** 184 fetches of the homepage, mostly through `/en-latest/`, got a copy cached before the change, still linking to its `/markdown/` URL. 4 runs fetched a `/markdown/` URL and got a 404.
- **The judge passed three answers as `UNKNOWN:`**, listed in [summary.md](summary.md) for review by hand.
- **Navigation counts come from the raw output**, not `summary.md`, with the same method as [20261117](../20261117/README.md). The raw promptfoo output isn't in the repository (97 MB).
