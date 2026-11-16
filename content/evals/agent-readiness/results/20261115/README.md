# Production snapshot: 20261115

How well Claude Code, Codex and OpenCode answer the [33 agent readiness cases](../../tests.yaml) with guide.wagtail.org as it was in production, each harness with its native tools. Config: [`agent-readiness-snapshot.yaml`](../../agent-readiness-snapshot.yaml), method in the [README](../../README.md#production-snapshot-claude-code-codex-and-opencode).

- **Runs:** 1,320: eight models, 33 cases, five repeats each. Every run produced an answer, except one OpenCode timeout (DeepSeek V4.1 Flash, 300 seconds).
- **When:** 16 November 2026, 13:59 to 15:31 GMT, against the live site.
- **Site:** `main` at `c63f3df`, before [#509](https://github.com/wagtail/guide/pull/509) (page Markdown converted from rendered HTML), which merged after the run. A rerun shows what #509 changes for agents.
- **Versions:** promptfoo 0.124.1, Claude Agent SDK 0.3.325 (Claude Code 2.1.325), Codex SDK and CLI 0.169.0, OpenCode 1.19.5. Judge: Claude Sonnet 5.5.
- **Search:** Claude Code and Codex use their providers' server-side search. OpenCode uses Exa, authenticated.

## Results

A case passes when at least three of its five runs pass. Duration and cost are each case's median run, then the median across cases. Costs are at API list prices, without the judge: $73.20 for all runs. OpenCode has no price for DeepSeek V4.1 Flash on TensorX.

| Harness / model                | Cases passed | Runs passed | Median duration | Median cost |
| ------------------------------ | -----------: | ----------: | --------------: | ----------: |
| Claude Code / Fable 5.2        |        33/33 |         98% |             29s |       20.7¢ |
| Claude Code / Opus 5.5         |        33/33 |         96% |             26s |        9.5¢ |
| Claude Code / Sonnet 5.5       |        32/33 |         96% |             25s |        4.8¢ |
| Claude Code / Haiku 5.5        |        27/33 |         83% |             27s |        1.5¢ |
| Codex / Sol 6.1                |        33/33 |         99% |             11s |        4.8¢ |
| Codex / Luna 6                 |        31/33 |         92% |             10s |        0.3¢ |
| OpenCode / Qwen 3.8 27B        |        33/33 |         96% |             34s |        0.8¢ |
| OpenCode / DeepSeek V4.1 Flash |        28/33 |         82% |             14s |           — |

[summary.md](summary.md) has the full tables from `summarize.py`: checks, pass rates by task and framing, surfaces reached, and failed runs per case. [runs.csv](runs.csv) has one row per run.

## Findings

**Each harness reads the guide its own way.**

- Claude Code fetches pages: Fable and Opus search in 0–6% of runs and go straight to the guide, while Haiku searches in 75%. Sonnet, Opus and Fable read llms.txt in 36–56% of runs.
- Codex searches in 97–98% of runs, on OpenAI's servers. It never fetched a page with its shell, so its trace only shows pages it opened by URL. Its answers cite the guide as often as other harnesses', but few cite a page it was seen to open (`answer_grounded`: 5–23%).
- OpenCode mixes Exa search with `webfetch`. DeepSeek reads Markdown pages and llms.txt in about a third of runs.
- No model found the MCP server on its own, and only Qwen reached the agent skill, in one run.

**Guessed `/en-latest/` URLs only work because they redirect.** Fable's first fetch is a `guide.wagtail.org/en-latest/…` URL in 137 of the 144 runs that fetch anything, Opus in 128 of 140, Sonnet 52 of 130 and DeepSeek 48 of 103. These URLs follow the developer docs' pattern and redirect to the current page. 42–45% of Fable's and Opus's answers cite them.

**The old editor manual still costs correct answers.** The developer docs' versioned `editor_manual` pages still turn up in search, for questions the guide answers:

- `troubleshoot-recover-deleted-document` fails in 21 of 40 runs across all models: answers cite old editor manual pages or a wagtail.org blog post, not the guide's documents page.
- Codex Luna fails `troubleshoot-locked-page` in all five runs, citing developer docs and the editor manual's dashboard page, not the guide's reports page.
- The check against links to the old editor manual fails 27 runs, mostly Haiku (11) and Luna (8).

Getting the developer docs' old editor manual pages to point to the guide would likely fix more answers than any other change.

**Smaller models struggle with troubleshooting and questions that don't name the guide.** Haiku passes 68% of troubleshooting runs and 69% when the prompt doesn't name the guide, Luna 72% and 73%, DeepSeek 80% and 60%. Every model passes at least 87% of runs that name the guide.

## Reading these results

- **Not comparable with the [Harbor 20261113 results](../../../agent-readiness-harbor/results/20261113/README.md).** Harbor runs harnesses in containers, with other versions and settings, and OpenCode searched there with Exa's anonymous, rate-limited endpoint.
- **Five repeats per case.** Differences of a case or two between models are within run-to-run variation: see the spread in [summary.md](summary.md).
- **Claude Code ran with a subscription login.** Its costs are what the same tokens would cost through the API.
- **Trace columns undercount server-side reads**: Codex's and Claude Code's searches, and pages Codex opens without a URL in its search item.
- **The judge passed eight answers as `UNKNOWN:`**, listed in [summary.md](summary.md) for review by hand.
- **Raw promptfoo output isn't in the repository** (92 MB). It has every answer and trace, and stays with whoever ran the snapshot.
