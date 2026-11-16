# Production snapshot: 20261116

The same snapshot as [20261115](../20261115/README.md), rerun after page Markdown changed: same config, cases, versions and judge. [20261117](../20261117/README.md) is the rerun after the site map was added. See [Reading production snapshot results](../README.md) for what the tables and columns mean.

- **Runs:** 1,320: eight models, 33 cases, five repeats each. Every run produced an answer, except one OpenCode timeout (Qwen 3.8 27B, 300 seconds).
- **When:** 16 November 2026, 16:25 to 17:51 GMT, against the live site.
- **Site:** `main` at `7cecec9`. Since 20261115, two changes to the site: [#509](https://github.com/wagtail/guide/pull/509) converts page Markdown from the rendered HTML page, and `f97c2da` leaves the page tools out of it. Page Markdown now has what the HTML page has around the content: section pages list their pages, content pages have an "On this page" list, and links are absolute. Nothing else changed for agents.
- **Versions:** promptfoo 0.124.1, Claude Agent SDK 0.3.325 (Claude Code 2.1.325), Codex SDK and CLI 0.169.0, OpenCode 1.19.5. Judge: Claude Sonnet 5.5.

## Results

A case passes when at least three of its five runs pass. Costs are at API list prices, without the judge: $73.39 for all runs, against $73.20 for 20261115.

| Harness / model                | Cases passed | Runs passed | Median duration | Median cost |
| ------------------------------ | -----------: | ----------: | --------------: | ----------: |
| Claude Code / Fable 5.2        |   32/33 (33) |   96% (98%) |             26s |       20.6¢ |
| Claude Code / Opus 5.5         |   33/33 (33) |   95% (96%) |             25s |        9.7¢ |
| Claude Code / Sonnet 5.5       |   31/33 (32) |   95% (96%) |             23s |        4.9¢ |
| Claude Code / Haiku 5.5        |   30/33 (27) |   82% (83%) |             25s |        1.7¢ |
| Codex / Sol 6.1                |   32/33 (33) |   98% (99%) |             10s |        4.8¢ |
| Codex / Luna 6                 |   31/33 (31) |   92% (92%) |             10s |        0.3¢ |
| OpenCode / Qwen 3.8 27B        |   32/33 (33) |   94% (96%) |             33s |        0.8¢ |
| OpenCode / DeepSeek V4.1 Flash |   28/33 (28) |   87% (82%) |             12s |           — |

20261115 results in brackets. [summary.md](summary.md) has the full tables, and [runs.csv](runs.csv) one row per run.

## Findings

**Answers are as good as before.** Every arm's pass rate is within run-to-run variation of 20261115: the largest moves are DeepSeek's 5 points up, and Fable's and Qwen's 2 points down. Cases passed moved by one case at most, except for Haiku. Haiku's 27 to 30 is three cases that passed two of five runs in 20261115, and three or four now: they sit at the threshold, so they flip with little change.

**Agents read llms.txt far less, because section pages now lead somewhere.** In 20261115, the Markdown of section pages like `/en/how-to-guides/` or `/en/releases/` was only their title and introduction, with no links. The homepage linked to the four sections. From a section page, the only way on was the callout at the top, which says to use llms.txt "to discover all available pages". Most of Claude Code's visits to llms.txt came straight after the homepage or a section page, and 144 of the 225 pages read just before llms.txt had no guide links at all. Now section pages list their pages, with a median of 2 to 18 links, so agents go down the tree instead:

| Arm        | llms.txt reached | Markdown URL reached | Pages fetched from a link on another page | Pages fetched from llms.txt |
| ---------- | ---------------: | -------------------: | ----------------------------------------: | --------------------------: |
| Fable 5.2  |         44% → 8% |             19% → 3% |                                 112 → 172 |                    120 → 19 |
| Opus 5.5   |         36% → 9% |             19% → 2% |                                  78 → 110 |                     96 → 14 |
| Sonnet 5.5 |        56% → 27% |            40% → 21% |                                  93 → 163 |                    174 → 63 |
| DeepSeek   |        32% → 13% |            32% → 11% |                                   19 → 82 |                     73 → 19 |
| Qwen       |         16% → 2% |             15% → 3% |                                   27 → 48 |                      44 → 6 |

The callout didn't change, and agents saw it as often: 90% of Claude Code's page fetches returned it in both snapshots. They no longer need it: among Fable's, Opus's and Sonnet's runs that only ever got Markdown, 50% read llms.txt in 20261115, and 20% now. Part of the drop has another cause, an HTML homepage cached by Cloudflare (below). Codex doesn't fetch pages itself, and Haiku rarely read llms.txt before, so neither changed. Markdown URLs dropped with llms.txt, as llms.txt is where agents found them. Agents still get Markdown from the usual page URLs, through content negotiation.

**Section lists have titles, where llms.txt has descriptions, and that may cost answers.** `releases-7-4-incomplete-blocks` asks which release first allowed drafts with empty required fields inside StreamField blocks: 7.4, after 7.0 did it for other fields. Fable, Opus and Sonnet failed 1 of 15 runs in 20261115 and 7 of 15 now. Six of the seven failing runs read `/en/releases/`, which now lists every release, read the releases around 7.0 without opening 7.4, and answered 7.0. One Opus run read 7.3, 8.0 and 8.1, and skipped 7.4. In llms.txt, the 7.4 notes are described as covering "draft‑saving incomplete blocks", and in 20261115, 9 of the 14 passing runs went to the 7.4 notes from llms.txt. The section list only says "New in Wagtail 7.4". With 33 cases and eight arms, one case moving this much can happen by chance, so this needs a targeted rerun before acting on it.

**Cloudflare serves a cached HTML homepage to agents that ask for Markdown.** `/en-latest/` redirects to `/en/?target_version=latest`, and Cloudflare has an HTML copy of that URL cached, which it returns whatever the request's `Accept` header. The guide's responses vary on `Accept`, but Cloudflare ignores that, and only the HTML version can be cached: Markdown responses are `private`. In 20261115, all 163 of Claude Code's fetches of `/en-latest/` got Markdown. In 20261116, 104 of 142 got HTML: 5,000 characters of page, with the full menu. Fable and Opus start from guessed `/en-latest/` URLs, so they met it most. The menu links to every page, so runs that got an HTML homepage or section page almost never read llms.txt, in either snapshot (4% and 3%). 53 runs of Fable, Opus and Sonnet got one in 20261115, and 147 in 20261116. Any page Cloudflare caches this way serves HTML to agents until it's purged.

**Unchanged from 20261115:**

- The old editor manual still costs answers: `troubleshoot-recover-deleted-document` fails 22 of 40 runs (21 before), and `troubleshoot-locked-page` 15 of 40 (16 before). Luna fails it in four runs, against five before.
- Fable and Opus still guess `/en-latest/` URLs in 82–84% of runs, which only work because they redirect.
- No model used the MCP server or the agent skill.
- Smaller models still struggle when the prompt doesn't name the guide: Haiku passes 73% of those runs, Luna 76%, DeepSeek 62%.

**Noise worth knowing about.** Qwen's `info-snippets-vs-pages` went from 5 passes to 1. In three of the four failing runs, it searched the developer docs specifically, like `site:docs.wagtail.org`, and in the fourth it didn't search at all, so the guide's page never came up. That's the model's choice of query, not the site.

## What to try next

- Stop Cloudflare from serving cached HTML to requests for Markdown: leave pages out of the cache when the request asks for Markdown, or add `Accept` to the cache key. Then purge `/en/?target_version=latest`.
- Rerun `releases-7-4-incomplete-blocks` and the other release cases, 10 times each, to tell whether reading section lists rather than llms.txt costs answers.
- Add each page's description to the "In this section" lists, as llms.txt does, so agents can tell which page answers their question before opening it.

## Reading these results

- **Same caveats as [20261115](../20261115/README.md#reading-these-results).** Five repeats per case, Claude Code on a subscription login, and trace columns that can't see server-side reads.
- **The judge passed three answers as `UNKNOWN:`**, listed in [summary.md](summary.md) for review by hand.
- **Navigation counts come from the raw output**, not `summary.md`: which page or file each fetched URL first appeared in, and how many guide links each page had. The raw promptfoo output isn't in the repository (95 MB).
