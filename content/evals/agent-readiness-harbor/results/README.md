# Results and findings

- **Benchmark:** 5,247 first attempts; 18 model/harness pairs; 33 questions × three repeats per arm.
- **Dates:** original batches completed 7 November 2026; Fable 5.2 completed 11 November; five further MCP suites completed 13 November.
- **Follow-ups:** 1,761 failure retries, 862 Tavily reruns and 57 integration-pilot attempts.
- **Trace inventory:** 7,927 attempts, with 7,894 saved trajectories.

## Benchmark

### Success

Each cell counts passes out of 99 planned answers, including failed attempts.

| Harness / model                |  Native | No tools | Web-only | Native + MCP |
| ------------------------------ | ------: | -------: | -------: | -----------: |
| Claude Code / Haiku 5.5        |   78/99 |     9/99 |    82/99 |      93/99 † |
| Claude Code / Sonnet 5.5       |   83/99 |    15/99 |    84/99 |            — |
| Claude Code / Opus 5.5         |   89/99 |    34/99 |    87/99 |      94/99 † |
| Claude Code / Fable 5.1        |   91/99 |    37/99 |    93/99 |            — |
| Claude Code / Fable 5.2        |   96/99 |    34/99 |    96/99 |        95/99 |
| Codex / Sol                    |   95/99 |    26/99 |        — |            — |
| Codex / Luna                   |   86/99 |  16/99 † |        — |        88/99 |
| Codex / Terra                  |   88/99 |    12/99 |        — |            — |
| Codex / Astra                  | 93/99 † |  23/99 † |        — |        96/99 |
| Cursor / Grok 4.7 Medium       |   96/99 |        — |        — |            — |
| OpenCode / DeepSeek V4.1 Flash |   93/99 |     9/99 |    93/99 |      95/99 † |
| OpenCode / GLM 5.3 Flash       |   90/99 |  12/99 † |    87/99 |            — |
| OpenCode / MiMo v2.6 Pro       |   95/99 |     1/99 |    92/99 |            — |
| OpenCode / GLM 5.3             |   87/99 |   7/99 † |  76/99 † |            — |
| OpenCode / Qwen 3.8 27B        | 75/99 † |     0/99 |  85/99 † |            — |
| OpenCode / Gemma 4 31B         | 24/99 † |     1/99 |    76/99 |            — |
| OpenCode / Kimi K3             |   93/99 |     2/99 |    90/99 |            — |
| Mistral Vibe / Large 4         |   78/99 |  12/99 † |        — |            — |

† Includes execution or tool-control errors. Baseline audits reject attempted tool use, including blocked calls. — indicates an arm without a full-suite run.

### Speed and cost

- Time: median agent execution, with setup and grading recorded separately.
- Cost: mean estimated candidate API usage per attempt, shown with complete coverage.
- Total: **$297.66** candidate usage, covering 5,215/5,247 attempts; **$21.42** judge usage.
- [Benchmark CSV](benchmark.csv): all 53 rows, including baseline/MCP timing, versions and errors.

| Harness / model                | Native median seconds |          Native mean USD | Web median seconds |             Web mean USD |
| ------------------------------ | --------------------: | -----------------------: | -----------------: | -----------------------: |
| Claude Code / Haiku 5.5        |                  19.4 |                $0.010582 |               17.4 |                $0.015282 |
| Claude Code / Sonnet 5.5       |                  16.1 |                $0.055771 |               15.2 |                $0.049245 |
| Claude Code / Opus 5.5         |                  25.4 |                $0.093413 |               24.8 |                $0.086257 |
| Claude Code / Fable 5.1        |                  33.6 |                $0.302966 |               31.7 |                $0.259414 |
| Claude Code / Fable 5.2        |                  33.3 |                $0.246632 |               32.7 |                $0.228465 |
| Codex / Sol                    |                  11.1 |                $0.051152 |                  — |                        — |
| Codex / Luna                   |                  12.1 |                $0.003356 |                  — |                        — |
| Codex / Terra                  |                   8.9 |                $0.027114 |                  — |                        — |
| Codex / Astra                  |                  11.0 | Unknown (96/99 recorded) |                  — |                        — |
| Cursor / Grok 4.7 Medium       |                  25.0 |                $0.056400 |                  — |                        — |
| OpenCode / DeepSeek V4.1 Flash |                  10.9 |                $0.001767 |                9.1 |                $0.001658 |
| OpenCode / GLM 5.3 Flash       |                  14.0 |                $0.003905 |               18.6 |                $0.004516 |
| OpenCode / MiMo v2.6 Pro       |                  13.2 |                $0.005465 |               14.5 |                $0.008090 |
| OpenCode / GLM 5.3             |                  20.9 |                $0.038366 |               42.3 | Unknown (81/99 recorded) |
| OpenCode / Qwen 3.8 27B        |                  40.7 |                $0.060516 |               24.7 |                $0.041529 |
| OpenCode / Gemma 4 31B         |                  16.1 |                $0.002411 |                9.4 |                $0.000775 |
| OpenCode / Kimi K3             |                  15.4 |                $0.054328 |               24.9 |                $0.106938 |
| Mistral Vibe / Large 4         |                  27.1 |                $0.023132 |                  — |                        — |

### Retries

- Each original failure received one fresh attempt with the same question and tool arm.
- Passes increased from **2,595/4,356 (59.6%)** to **2,757/4,356 (63.3%)**.
- **162/1,761 retries recovered (9.2%)**.
- Timing and cost include both attempts; each original slot retains one final score.
- Scope: the original 17 model/harness pairs. [Per-arm retry results](retries.csv).

### Search

We used the **Tavily MCP** for OpenCode search.

- Scope: 862 slots whose earlier attempts encountered search rate limits.
- Passes: **750/862 (87.0%)**, compared with **736/862 (85.4%)** after earlier retries.
- Paired outcomes: 57 improvements, 43 regressions; net gain of 14 slots.
- Four Qwen timeouts remain failures.
- All 1,442 recorded Tavily searches completed.
- Candidate cost: **$20.73**; judging: **$3.49**; search credits billed separately.
- [Search results](search.csv) · [Paired outcomes](../analysis/data/tavily-pairs.csv).

### Guide MCP

We configured `https://guide.wagtail.org/mcp` alongside each harness's native tools.

- **Full suites:** six model/harness pairs × 99 attempts, including Fable 5.2.
- The five 13 November suites passed **466/495**, using the original grading snapshot and CLI versions.
- Four execution failures remain in the scores: three Claude setup timeouts and one DeepSeek agent exit.
- **Integration pilot:** 17 model/harness pairs × three questions; **49/51 passed**. [Pilot results](mcp-pilot.csv).

| Model                          | Passes | Median agent seconds | Mean candidate USD | Guide MCP / available traces |
| ------------------------------ | -----: | -------------------: | -----------------: | ---------------------------: |
| OpenCode / DeepSeek V4.1 Flash |  95/99 |                  9.4 |          $0.001290 |                        93/99 |
| Claude Code / Opus 5.5         |  94/99 |                 13.9 |    Partial (97/99) |                        85/97 |
| Claude Code / Haiku 5.5        |  93/99 |                 10.1 |    Partial (98/99) |                        83/98 |
| Codex / Astra                  |  96/99 |                 12.2 |          $0.263735 |                         0/99 |
| Codex / Luna                   |  88/99 |                 10.9 |          $0.003323 |                         0/99 |
| Claude Code / Fable 5.2        |  95/99 |                 12.5 |          $0.136886 |                        87/99 |

Codex used web tools through `exec`; the saved calls contain no guide MCP invocations. Claude setup failures account for the three missing trajectories.

Fable 5.2's tool-enabled arms:

| Measure                            |        Native |      Web-only | Native+guide MCP |
| ---------------------------------- | ------------: | ------------: | ---------------: |
| Graded passes                      | 96/99 (97.0%) | 96/99 (97.0%) |    95/99 (96.0%) |
| Direct web-search traces           | 72/99 (72.7%) | 80/99 (80.8%) |      0/99 (0.0%) |
| Guide MCP traces                   |   0/99 (0.0%) |   0/99 (0.0%) |    87/99 (87.9%) |
| Final answers citing `/en-latest/` | 50/99 (50.5%) | 49/99 (49.5%) |      0/99 (0.0%) |
| Median tool calls                  |             4 |             2 |                4 |
| Mean tool calls                    |          3.48 |          2.86 |             4.07 |
| Median agent time                  |        33.3 s |        32.7 s |           12.5 s |

The baseline passed 34/99 with zero tool calls. MCP's 12.5-second median accompanied more calls than native's 33.3-second median.

### Historical Promptfoo comparison

Compared with [October's Promptfoo results](../../agent-readiness/RESULTS.md):

- Baseline and web-only arms share question coverage.
- Opus uses the 28 shared questions: 84 answers per arm. Other models use 99.
- October used a proxied site copy; Harbor used the live site in November.

| Model      | Tools    | Promptfoo success | Harbor success |  Difference |
| ---------- | -------- | ----------------: | -------------: | ----------: |
| Haiku 5.5  | baseline |               10% |    9.1% (9/99) | -0.9 points |
| Haiku 5.5  | web      |               80% |  82.8% (82/99) | +2.8 points |
| Sonnet 5.5 | baseline |               15% |  15.2% (15/99) | +0.2 points |
| Sonnet 5.5 | web      |               89% |  84.8% (84/99) | -4.2 points |
| Opus 5.5   | baseline |               36% |  36.9% (31/84) | +0.9 points |
| Opus 5.5   | web      |               89% |  90.5% (76/84) | +1.5 points |
| Fable 5.1  | baseline |               41% |  37.4% (37/99) | -3.6 points |
| Fable 5.1  | web      |               90% |  93.9% (93/99) | +3.9 points |

Web-only timing and cost use means:

| Model      | Promptfoo seconds | Harbor seconds | Promptfoo cost/answer | Harbor cost/answer |
| ---------- | ----------------: | -------------: | --------------------: | -----------------: |
| Haiku 5.5  |                22 |           17.8 |                $0.016 |            $0.0153 |
| Sonnet 5.5 |                17 |           15.6 |                $0.028 |            $0.0492 |
| Opus 5.5   |                28 |           24.3 |                $0.046 |            $0.0855 |
| Fable 5.1  |                36 |           32.4 |                $0.133 |            $0.2594 |

## Trace findings

### Retrieval and navigation

- **24,292 recorded outer tool calls:** median 2, mean 3.08, p90 8, maximum 177.
- **2,777 traces have zero calls**; 33 attempts have missing trajectories.
- **20,302 visible retrieval calls**, including 5,744 failures.
- **346 calls revisit a returned page**, across 247 traces.
- Native workspace inspection appears in Qwen 42/99, GLM 5.3 38/99 and Cursor 30/99; Fable 5.2 has zero detected cases.
- Fable's site-start questions begin at the homepage in 3/15 native and 6/15 web-only attempts; its MCP arm uses the guide server in 15/15.
- The 12 Fable MCP-arm answers without guide MCP calls concern developer/server questions; all pass.

Counts cover the full mixed inventory. Compare models within the same phase and arm; query framing also varies by question.

Tavily reruns show continued friction after search succeeds:

| Measure                                                   | Absolute count |                 Relative count |
| --------------------------------------------------------- | -------------: | -----------------------------: |
| Visible retrieval calls                                   |          4,616 |             Median 4 per trace |
| Failed retrieval calls                                    |            902 |       19.5% of retrieval calls |
| Traces with failed retrieval                              |            423 |            49.1% of 862 traces |
| Calls revisiting a previously returned page target        |             46 |        In 33/862 traces (3.8%) |
| Traces with returned pages absent from answer URLs        |            441 | 51.4% of 858 available answers |
| Answer page URLs matching returned fetch targets          |            831 |  59.0% of 1,408 citation pages |
| Answer page URLs visible only in search output            |            281 |  20.0% of 1,408 citation pages |
| Answer page URLs absent from visible retrieval and prompt |             96 |   6.8% of 1,408 citation pages |

Four Qwen reruns timed out with 29–34 calls. Trace `0491ca55c0f95e16` expanded from an admin question into GitHub implementation details and ended without an answer.

### Citations and support

- Fable native and web-only answers cite `/en-latest/` in 50/99 and 49/99 attempts; native+MCP does so in 0/99.
- Citation pages matching returned targets: native 105/206 (51.0%), web-only 120/217 (55.3%), native+MCP 140/201 (69.7%).
- URL matches identify provenance. Claim support requires inspecting the returned passages.
- Trace `42383817403a7fe0` correctly describes document deletion but cites the prohibited legacy editor manual.
- Trace `032f383034dc553d` supports the privacy instructions and repeats an identical fetch.
- URL-pattern counts preserve requested/cited paths; actual served versions require redirect or content evidence.

### Grading findings

- The historical latest-release case requires 8.0; Fable retrieved supported 8.1 answers.
- A multi-tenancy answer used “Separate per tenant” under a Database heading; the literal phrase check rejected it.
- Published grades retain those outcomes. Future evaluations use a fixed-8.0 question and a broader database phrase check.

### Automated review highlights

- **Jevotron** surfaced a source contradiction: Haiku denied guide coverage of multi-tenancy despite its retrieved summary (`071700dfc25d0ddb:s3:0`).
- It also found an unrelated fetch whose own prompt said “Not needed; skip” (`6b9dac8fd2388c3e:s2:1`).
- Reviewing full passages overturned some flags caused by truncated excerpts. The earlier review labeled all 489 opaque-wrapper traces NORMAL for retrieval, limiting confidence in negative judgments.
- Use its flags as a review queue, with original evidence and separate confirmed/plausible/unknown dispositions.
- **GEPA/TextGrad** suggested clearer source attribution and fallback after repeated access failures. Their outputs also copied benchmark answers and misread traces; suggestions remain untested.

## Energy

Illustrative Neuralwatt inference energy across 3,957 attempts:

- **3,102.848 Wh** from strictly matched requests, covering 3,927 attempts.
- **129.712 Wh** added through execution-window attribution.
- **3.233 kWh** combined total.

### Initial OpenCode arms: median Wh per attempt

| Model               | No tools | Native | Web-only |
| ------------------- | -------: | -----: | -------: |
| DeepSeek V4.1 Flash |   0.0051 | 0.0445 |   0.0291 |
| Gemma 4 31B         |   0.0166 | 0.1457 |   0.0751 |
| GLM 5.3             |   0.0598 | 0.7619 |   0.6425 |
| GLM 5.3 Flash       |   0.0228 | 0.2081 |   0.1647 |
| Kimi K3             |   0.6623 | 1.5794 |   3.9117 |
| MiMo v2.6 Pro       |   0.0214 | 0.4437 |   0.4413 |
| Qwen 3.8 27B        |   0.0319 | 0.4201 |   0.2024 |

- Each cell includes 99 attempts with attributed energy, except GLM 5.3 baseline (96) and web-only (81).
- These are partial attributed medians, including failed attempts with known energy.
- Shared cohort energy contributes to batch means only.

### DeepSeek MCP comparison

- **MCP median: 0.0325 Wh/attempt**, versus native 0.0445 Wh and web-only 0.0291 Wh.
- MCP strict mean: **0.0586 Wh/attempt**, with energy attributed to all 99 attempts.
- MCP total including time-window attribution: **5.992 Wh**; batch mean **0.0605 Wh/attempt**.
- Comparisons span different run dates and the provider's reporting change.

### All phases: illustrative totals

| Model               | Attempts / strict energy rows | Strict mean Wh | Strict median Wh | Window total Wh | Window mean Wh | Strict share of window Wh |
| ------------------- | ----------------------------- | -------------- | ---------------- | --------------- | -------------- | ------------------------- |
| deepseek-v4.1-flash | 508 / 508                     | 0.0547         | 0.0184           | 31.4166         | 0.0618         | 88.52%                    |
| gemma-4-31b         | 593 / 585                     | 0.1590         | 0.0744           | 99.2911         | 0.1674         | 93.69%                    |
| glm-5.3             | 598 / 576                     | 1.3098         | 0.3515           | 780.2683        | 1.3048         | 96.69%                    |
| glm-5.3-flash       | 542 / 542                     | 0.2941         | 0.1258           | 164.9717        | 0.3044         | 96.62%                    |
| kimi-k3             | 512 / 512                     | 2.2173         | 0.9627           | 1184.5928       | 2.3137         | 95.84%                    |
| kimi-k3.1-pro       | 3 / 3                         | 0.1204         | 0.1194           | 0.3857          | 0.1286         | 93.66%                    |
| mimo-v2.6-pro       | 588 / 588                     | 0.7489         | 0.3667           | 466.1023        | 0.7927         | 94.47%                    |
| qwen-3.8-27b        | 613 / 613                     | 0.8029         | 0.2625           | 505.5317        | 0.8247         | 97.36%                    |

- Strict means/medians use attempts with matched energy; window means use all attempts.
- Totals combine original runs, selected retries and follow-ups.
- Figures span Neuralwatt's [6 November reporting change](https://neuralwatt.com/changelog?area=energy).
- Coverage is provider-attributed inference energy; local execution, search and MCP services have separate resource use.

## Data

| Dataset                                                                                                                                                                               | Contents                                                                     |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| [Benchmark](benchmark.csv), [retries](retries.csv), [search](search.csv), [MCP pilot](mcp-pilot.csv)                                                                                  | Success, timing, cost and coverage.                                          |
| [Patterns](../analysis/data/patterns.csv), [definitions](../analysis/data/pattern-definitions.csv)                                                                                    | 47 patterns: absolute counts, percentages and eligible/unknown denominators. |
| [Tool calls](../analysis/data/tool-calls.csv), [per-trace statistics](../analysis/data/trials.csv)                                                                                    | Call distributions and all 7,927 attempt rows.                               |
| [Retrieval statistics](../analysis/data/retrieval-statistics.csv), [definitions](../analysis/data/retrieval-definitions.csv), [per-trace rows](../analysis/data/retrieval-trials.csv) | 20 retrieval/friction measures.                                              |
| [Citation provenance](../analysis/data/citation-provenance.csv)                                                                                                                       | 11,444 trace/page pairs with evidence event IDs.                             |
| [By arm](../analysis/data/by-arm.csv), [by framing](../analysis/data/by-framing.csv), [Tavily pairs](../analysis/data/tavily-pairs.csv)                                               | Grouped patterns and paired intervention outcomes.                           |
| [Inventory](../analysis/data/inventory.json), [coverage](../analysis/data/data-coverage.csv)                                                                                          | Cohort counts and available evidence.                                        |

Raw runs live in `~/.cache/guide-agent-eval/harbor/`. [Source configuration](../config/trace-sources.yaml) lists their directories. Join trace IDs through the extracted `trials.jsonl` and `events.jsonl`; original trajectories contain the returned passages.

## Research informing the analysis

- [AgentReady/Ora](https://github.com/agentready-org/standard/blob/main/spec/spec.md): distinguish site capabilities and task outcomes.
- [Joost's specification](https://specification.website/spec/agent-readiness/markdown-source-endpoints/): check Markdown discoverability and representation parity.
- [Cloudflare](https://blog.cloudflare.com/agent-readiness/): inspect repeated index reads and search loops.
- [Tom Cranstoun's MX principles](https://mx.allabout.network/learn/key-principles.html): track provenance, versions and canonical identity.
- [Mintlify's benchmark](https://www.mintlify.com/blog/llms-txt-agent-benchmark): measure retrieval friction alongside answer quality.
- [Ahrefs](https://ahrefs.com/blog/why-chatgpt-cites-pages/): distinguish search exposure, opened pages and final citations.
