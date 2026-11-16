# Production snapshot: 20261117

The same snapshot as [20261116](../20261116/README.md), rerun after page Markdown gained a site map: same config, cases, versions and judge. See [Reading production snapshot results](../README.md) for what the tables and columns mean.

- **Runs:** 1,320: eight models, 33 cases, five repeats each. Every run produced an answer, except two DeepSeek V4.1 Flash runs that ended after five seconds with no output and no tool calls.
- **When:** 16 November 2026, 18:29 to 19:49 GMT, against the live site.
- **Site:** `main` at `e7d502b`. Since 20261116, one change to the site: `e7d502b` appends a site map to page Markdown. Every page now ends with a nested list of the whole guide, with each page's description and its Markdown URL, as llms.txt has. It's 11 KB, against 14 KB for llms.txt. Nothing else changed for agents.
- **Versions:** promptfoo 0.124.1, Claude Agent SDK 0.3.325 (Claude Code 2.1.325), Codex SDK and CLI 0.169.0, OpenCode 1.19.5. Judge: Claude Sonnet 5.5.

## Results

A case passes when at least three of its five runs pass. Costs are at API list prices, without the judge: $72.56 for all runs, against $73.39 for 20261116.

| Harness / model                | Cases passed | Runs passed | Median duration | Median cost |
| ------------------------------ | -----------: | ----------: | --------------: | ----------: |
| Claude Code / Fable 5.2        |   33/33 (32) |   99% (96%) |             25s |       20.4¢ |
| Claude Code / Opus 5.5         |   32/33 (33) |   96% (95%) |             25s |        9.7¢ |
| Claude Code / Sonnet 5.5       |   32/33 (31) |   95% (95%) |             22s |        4.8¢ |
| Claude Code / Haiku 5.5        |   27/33 (30) |   81% (82%) |             28s |        1.7¢ |
| Codex / Sol 6.1                |   33/33 (32) |   99% (98%) |              9s |        4.8¢ |
| Codex / Luna 6                 |   31/33 (31) |   91% (92%) |              9s |        0.3¢ |
| OpenCode / Qwen 3.8 27B        |   33/33 (32) |   95% (94%) |             34s |        0.9¢ |
| OpenCode / DeepSeek V4.1 Flash |   30/33 (28) |   86% (87%) |              9s |           — |

20261116 results in brackets. [summary.md](summary.md) has the full tables, and [runs.csv](runs.csv) one row per run.

## Findings

**Answers are as good as before.** Every arm's pass rate is within 3 points of 20261116, well within run-to-run variation. Haiku's cases passed went back from 30 to 27, the same threshold flips as last time in the other direction: `troubleshoot-locked-page` went from four passes out of five to one, `info-snippets-vs-pages` from three to one, and `troubleshoot-image-upload-rejected` from three to two.

**Agents no longer read llms.txt, because every page now has its contents.** Before, agents mostly read llms.txt from the homepage or a section page, whose callout points to it. Now each page they read ends with the same list, so they pick the next page from it:

| Arm        | llms.txt reached | Markdown URL reached | Pages fetched from llms.txt |
| ---------- | ---------------: | -------------------: | --------------------------: |
| Fable 5.2  |          8% → 0% |              3% → 0% |                      18 → 0 |
| Opus 5.5   |          9% → 0% |              2% → 1% |                      14 → 0 |
| Sonnet 5.5 |         27% → 1% |             21% → 4% |                      62 → 0 |
| Haiku 5.5  |         12% → 1% |              8% → 3% |                      21 → 0 |
| DeepSeek   |         13% → 2% |            11% → 10% |                      19 → 1 |
| Qwen       |          2% → 1% |              3% → 2% |                       6 → 0 |

Agents don't follow the site map's Markdown URLs, though. 1,272 of Claude Code's 1,406 fetches of guide pages returned `/markdown/` links, and 19 fetches were of a `/markdown/` URL. They fetch the usual page URL, and get Markdown from it through content negotiation. Claude Code fetched 12% fewer guide pages than in 20261116 (1,406 against 1,592), and Fable, Opus and Sonnet made 14–15% fewer tool calls per run.

**Descriptions in the site map brought back the answers section lists had cost.** `releases-7-4-incomplete-blocks` asks which release first allowed drafts with empty required fields inside StreamField blocks. Fable, Opus and Sonnet failed 1 of 15 runs in 20261115, when they went to the 7.4 notes from llms.txt, 7 of 15 in 20261116, when the releases page only listed titles, and none of 15 now. The releases page now ends with the site map, where the 7.4 notes are described as covering "draft‑saving incomplete blocks". In 14 of the 15 runs, the agent opened 7.4 before 7.3, or without opening 7.3, out of version order. In 20261116, the failing runs read the releases around 7.0, in or near version order, and stopped before 7.4. Three snapshots of one case is still a small sample, but each moved with the descriptions.

**Cloudflare also serves cached HTML for the homepage itself.** As well as `/en/?target_version=latest`, where `/en-latest/` redirects, Cloudflare caches HTML copies of `/en/`, which it returns to requests for Markdown. This also happened in 20261116, but [its README](../20261116/README.md) only mentions `/en-latest/`. 128 of Claude Code's 140 fetches of `/en-latest/` got HTML (104 of 142 in 20261116), and 100 of 135 fetches of `guide.wagtail.org` itself, which redirects to `/en/` (64 of 145). 208 of Fable's, Opus's and Sonnet's 495 runs got at least one HTML page from the guide, against 149 in 20261116. Those runs don't get the site map from the homepage, but the HTML menu links to every page, so they still find their way: 205 of those 208 runs passed (99%), against 273 of 287 runs that only got Markdown (95%). Most of them are Fable's and Opus's, which pass more often anyway.

**Pages are bigger, but costs didn't change.** The site map is 11 KB of a 16 KB page like "Manage documents". Total cost was $73.20, $73.39 and $72.56 across the three snapshots, and each model's total moved by 3% or less, except Haiku's (4%) and Luna's (7%), which are a few dollars or less. Claude Code's `WebFetch` summarizes pages with a small model before the main model sees them, so the main model never reads the site map in full. OpenCode gives the model the whole page, but its agents fetch fewer pages: among runs that read guide pages, Qwen's median prompt tokens went from 42,900 to 47,000, and DeepSeek's stayed at 37,000. DeepSeek isn't priced on TensorX, so its cost doesn't show in the totals.

**Unchanged from 20261116:**

- The old editor manual still costs answers: `troubleshoot-recover-deleted-document` fails 20 of 40 runs (22 before), and `troubleshoot-locked-page` 15 of 40 (15).
- Fable and Opus still guess `/en-latest/` URLs in 80–84% of runs.
- No model used the MCP server or the agent skill.
- Smaller models still struggle when the prompt doesn't name the guide: Haiku passes 69% of those runs, Luna 76%, DeepSeek 64%.

## What to try next

- Stop Cloudflare from serving cached HTML to requests for Markdown: leave pages out of the cache when the request asks for Markdown, or add `Accept` to the cache key. Then purge `/en/` and `/en/?target_version=latest`.

## Reading these results

- **Same caveats as [20261115](../20261115/README.md#reading-these-results).** Five repeats per case, Claude Code on a subscription login, and trace columns that can't see server-side reads.
- **The judge passed four answers as `UNKNOWN:`**, listed in [summary.md](summary.md) for review by hand.
- **Navigation counts come from the raw output**, not `summary.md`: which page or file each fetched URL last appeared in before it was fetched, and the content type in Claude Code's `WebFetch` output. They use a slightly different method from [20261116](../20261116/README.md), so the 20261116 figures here are recomputed. The raw promptfoo output isn't in the repository (110 MB).
