# Results and findings

- **Benchmark:** 6,534 first attempts; 19 model/harness pairs; 33 questions × three repeats per arm.
- **Dates:** original batches completed 7 November 2026; Fable 5.2 completed 11 November; 18 further MCP suites completed 13–14 November.
- **Follow-ups:** 1,761 failure retries, 862 Tavily reruns and 62 integration/preflight attempts.
- **Trace inventory:** 9,219 attempts, with 9,185 saved trajectories.

## Benchmark

### Success

Each cell counts passes out of 99 planned answers, including failed attempts.

| Harness / model                |  Native | No tools | Web-only | Native + MCP |
| ------------------------------ | ------: | -------: | -------: | -----------: |
| Claude Code / Haiku 5.5        |   78/99 |     9/99 |    82/99 |      93/99 † |
| Claude Code / Sonnet 5.5       |   83/99 |    15/99 |    84/99 |        96/99 |
| Claude Code / Opus 5.5         |   89/99 |    34/99 |    87/99 |      94/99 † |
| Claude Code / Fable 5.1        |   91/99 |    37/99 |    93/99 |        96/99 |
| Claude Code / Fable 5.2        |   96/99 |    34/99 |    96/99 |        95/99 |
| Codex / Sol                    |   95/99 |    26/99 |        — |        96/99 |
| Codex / Luna                   |   86/99 |  16/99 † |        — |        88/99 |
| Codex / Terra                  |   88/99 |    12/99 |        — |        81/99 |
| Codex / Astra                  | 93/99 † |  23/99 † |        — |        96/99 |
| Cursor / Grok 4.7 Medium       |   96/99 |        — |        — |        96/99 |
| OpenCode / DeepSeek V4.1 Flash |   93/99 |     9/99 |    93/99 |      95/99 † |
| OpenCode / GLM 5.3 Flash       |   90/99 |  12/99 † |    87/99 |        94/99 |
| OpenCode / MiMo v2.6 Pro       |   95/99 |     1/99 |    92/99 |        96/99 |
| OpenCode / GLM 5.3             |   87/99 |   7/99 † |  76/99 † |        96/99 |
| OpenCode / Qwen 3.8 27B        | 75/99 † |     0/99 |  85/99 † |      94/99 † |
| OpenCode / Gemma 4 31B         | 24/99 † |     1/99 |    76/99 |        77/99 |
| OpenCode / Kimi K3             |   93/99 |     2/99 |    90/99 |        96/99 |
| OpenCode / Kimi K3.1 Pro       |       — |        — |        — |        96/99 |
| Mistral Vibe / Large 4         |   78/99 |  12/99 † |        — |        93/99 |

† Includes execution or tool-control errors. Baseline audits reject attempted tool use, including blocked calls. — indicates an arm without a full-suite run.

### Speed and cost

- Time: median agent execution, with setup and grading recorded separately.
- Cost: mean estimated candidate API usage per attempt, shown with complete coverage.
- Total: **$347.65** candidate usage, covering 6,501/6,534 attempts; **$26.62** judge usage.
- [Benchmark CSV](benchmark.csv): all 66 rows, including baseline/MCP timing, versions and errors.

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

- **Full suites:** 19 model/harness pairs × 99 attempts; **1,768/1,881 passed**.
- The latest 13 suites passed **1,207/1,287 (93.8%)** using the original grading snapshot. CLI versions are recorded in the benchmark CSV.
- Five execution failures remain: three Claude setup timeouts, one DeepSeek agent exit and one Qwen network error.
- **Integration pilot:** 49/51 passed. **Additional preflight:** 5/5 passed. [Pilot results](mcp-pilot.csv).

| Model                          | Passes | Median agent seconds | Mean candidate USD | Direct guide MCP / available traces |
| ------------------------------ | -----: | -------------------: | -----------------: | ----------------------------------: |
| Claude Code / Fable 5.1        |  96/99 |                 17.0 |          $0.191899 |                               90/99 |
| Claude Code / Fable 5.2        |  95/99 |                 12.5 |          $0.136886 |                               87/99 |
| Claude Code / Haiku 5.5        |  93/99 |                 10.1 |    Partial (98/99) |                               83/98 |
| Claude Code / Opus 5.5         |  94/99 |                 13.9 |    Partial (97/99) |                               85/97 |
| Claude Code / Sonnet 5.5       |  96/99 |                 10.7 |          $0.034339 |                               85/99 |
| Codex / Astra                  |  96/99 |                 12.2 |          $0.263735 |                                0/99 |
| Codex / Luna                   |  88/99 |                 10.9 |          $0.003323 |                                0/99 |
| Codex / Sol                    |  96/99 |                 11.2 |          $0.051752 |                                0/99 |
| Codex / Terra                  |  81/99 |                  9.0 |          $0.027630 |                                0/99 |
| Cursor / Grok 4.7 Medium       |  96/99 |                 20.7 |          $0.057538 |                               95/99 |
| Mistral Vibe / Large 4         |  93/99 |                 32.2 |          $0.026458 |                               98/99 |
| OpenCode / DeepSeek V4.1 Flash |  95/99 |                  9.4 |          $0.001290 |                               93/99 |
| OpenCode / GLM 5.3             |  96/99 |                 12.5 |          $0.012632 |                               93/99 |
| OpenCode / GLM 5.3 Flash       |  94/99 |                 12.9 |          $0.001780 |                               90/99 |
| OpenCode / Gemma 4 31B         |  77/99 |                 14.2 |          $0.001021 |                               93/99 |
| OpenCode / Kimi K3             |  96/99 |                 19.0 |          $0.051273 |                               92/99 |
| OpenCode / Kimi K3.1 Pro       |  96/99 |                 18.4 |          $0.034144 |                               89/99 |
| OpenCode / MiMo v2.6 Pro       |  96/99 |                 15.9 |          $0.002525 |                               91/99 |
| OpenCode / Qwen 3.8 27B        |  94/99 |                 17.1 |    Partial (98/99) |                               89/98 |

- Codex uses `exec` wrappers, excluded from the direct-call counts. Sol trace `071117ae5c45a41d` fetched guide content through MCP; Astra, Luna and Terra have no observed guide MCP calls.
- Four execution failures lack trajectories.
- Gemma improved from **24/99 native to 77/99 MCP**, Qwen from **75/99 to 94/99**, and Mistral from **78/99 to 93/99**.
- Of the latest 1,286 saved traces, one Sonnet answer cites `/en-latest/`; five Terra answers and one GLM Flash answer cite the legacy editor manual.

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

- **28,574 recorded outer tool calls:** median 2, mean 3.11, p90 7, maximum 177.
- **2,794 traces have zero calls**; 34 attempts have missing trajectories.
- **23,751 visible retrieval calls**, including 5,771 failures.
- **353 calls revisit a returned page**, across 252 traces.
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

Illustrative Neuralwatt inference energy across 4,650 attempts:

- **3,424.491 Wh** from strictly matched requests, covering 4,619 attempts.
- **155.628 Wh** added through execution-window attribution.
- **3.580 kWh** combined total.

### OpenCode arms: median Wh per attempt

| Model               | No tools | Native | Web-only | Native + MCP |
| ------------------- | -------: | -----: | -------: | -----------: |
| DeepSeek V4.1 Flash |   0.0051 | 0.0445 |   0.0291 |       0.0325 |
| Gemma 4 31B         |   0.0166 | 0.1457 |   0.0751 |       0.2105 |
| GLM 5.3             |   0.0598 | 0.7619 |   0.6425 |       0.3150 |
| GLM 5.3 Flash       |   0.0228 | 0.2081 |   0.1647 |       0.1489 |
| Kimi K3             |   0.6623 | 1.5794 |   3.9117 |       0.4897 |
| Kimi K3.1 Pro       |        — |      — |        — |       0.3635 |
| MiMo v2.6 Pro       |   0.0214 | 0.4437 |   0.4413 |       0.1618 |
| Qwen 3.8 27B        |   0.0319 | 0.4201 |   0.2024 |       0.2792 |

- Each cell includes 99 attempts with attributed energy, except GLM baseline (96), GLM web-only (81) and Qwen MCP (98).
- These are partial attributed medians, including failed attempts with known energy. Shared cohort energy contributes to batch means only.
- MCP medians are below native for six of seven comparable models; Gemma is higher. Comparisons span run dates and the provider’s reporting change.

### MCP energy totals

| Model               | Strict mean Wh | Window total Wh | Window mean Wh |
| ------------------- | -------------: | --------------: | -------------: |
| DeepSeek V4.1 Flash |         0.0586 |           5.992 |         0.0605 |
| Gemma 4 31B         |         0.2308 |          24.644 |         0.2489 |
| GLM 5.3             |         0.5865 |          61.880 |         0.6250 |
| GLM 5.3 Flash       |         0.2218 |          23.396 |         0.2363 |
| Kimi K3             |         0.8663 |          95.929 |         0.9690 |
| Kimi K3.1 Pro       |         0.8093 |          86.357 |         0.8723 |
| MiMo v2.6 Pro       |         0.1973 |          20.228 |         0.2043 |
| Qwen 3.8 27B        |         0.3403 |          35.126 |         0.3548 |

### All phases: illustrative totals

| Model               | Attempts / strict energy rows | Strict mean Wh | Strict median Wh | Window total Wh | Window mean Wh | Strict share of window Wh |
| ------------------- | ----------------------------- | -------------: | ---------------: | --------------: | -------------: | ------------------------: |
| deepseek-v4.1-flash | 508 / 508                     |         0.0547 |           0.0184 |         31.4166 |         0.0618 |                    88.52% |
| gemma-4-31b         | 692 / 684                     |         0.1694 |           0.0899 |        123.9354 |         0.1791 |                    93.50% |
| glm-5.3             | 697 / 675                     |         1.2037 |           0.3453 |        842.1480 |         1.2082 |                    96.48% |
| glm-5.3-flash       | 641 / 641                     |         0.2829 |           0.1282 |        188.3673 |         0.2939 |                    96.28% |
| kimi-k3             | 611 / 611                     |         1.9984 |           0.8487 |       1280.5214 |         2.0958 |                    95.36% |
| kimi-k3.1-pro       | 102 / 102                     |         0.7891 |           0.3501 |         86.7428 |         0.8504 |                    92.79% |
| mimo-v2.6-pro       | 687 / 687                     |         0.6694 |           0.2919 |        486.3308 |         0.7079 |                    94.56% |
| qwen-3.8-27b        | 712 / 711                     |         0.7392 |           0.2635 |        540.6572 |         0.7593 |                    97.20% |

- Strict means/medians use attempts with matched energy; window means use all attempts.
- Totals combine original runs, selected retries and follow-ups; the latest two Kimi preflight attempts are excluded.
- Figures span Neuralwatt’s [6 November reporting change](https://neuralwatt.com/changelog?area=energy).
- Coverage is provider-attributed inference energy; local execution, search and MCP services have separate resource use.

## Data

| Dataset                                                                                                                                                                               | Contents                                                                     |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| [Benchmark](benchmark.csv), [retries](retries.csv), [search](search.csv), [MCP pilot](mcp-pilot.csv)                                                                                  | Success, timing, cost and coverage.                                          |
| [Patterns](../analysis/data/patterns.csv), [definitions](../analysis/data/pattern-definitions.csv)                                                                                    | 47 patterns: absolute counts, percentages and eligible/unknown denominators. |
| [Tool calls](../analysis/data/tool-calls.csv), [per-trace statistics](../analysis/data/trials.csv)                                                                                    | Call distributions and all 9,219 attempt rows.                               |
| [Retrieval statistics](../analysis/data/retrieval-statistics.csv), [definitions](../analysis/data/retrieval-definitions.csv), [per-trace rows](../analysis/data/retrieval-trials.csv) | 20 retrieval/friction measures.                                              |
| [Citation provenance](../analysis/data/citation-provenance.csv)                                                                                                                       | 13,534 trace/page pairs with evidence event IDs.                             |
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
