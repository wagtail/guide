# Benchmark results

The main comparison contains **4,752 first attempts across 18 model/harness
pairs**, with 33 questions and three repeats per arm. It includes the original
4,356 runs and Fable 5.2's 396 runs. [All 48 model/arm rows](benchmark.csv) retain
batch dates, versions, timings, costs and errors. Fable 5.2 ran on 11 November
with Claude Code 2.1.322; the original batches completed on 7 November. Both use
the same original grading snapshot and live website, so run date and CLI version
remain potential confounders.

[Retry results](retries.md) cover only the original 4,356 slots, with one retry
per failure. Fable 5.2 was not retried. [Tavily](search.md) is a selected
search intervention; [MCP pilots](mcp-pilot.md) are small integration checks.
Neither is pooled into the first-attempt rates below.

## Success by tool arm

Each populated cell contains 99 planned answers, including failures. Native
means default tools; no-tools is the intended baseline; web-only permits
search/fetch. These compare model plus harness, not the harness independently.

| Harness / model                |  Native | No tools | Web-only | Native + MCP |
| ------------------------------ | ------: | -------: | -------: | -----------: |
| Claude Code / Haiku 5.5        |   78/99 |     9/99 |    82/99 |      Not run |
| Claude Code / Sonnet 5.5       |   83/99 |    15/99 |    84/99 |      Not run |
| Claude Code / Opus 5.5         |   89/99 |    34/99 |    87/99 |      Not run |
| Claude Code / Fable 5.1        |   91/99 |    37/99 |    93/99 |      Not run |
| Claude Code / Fable 5.2        |   96/99 |    34/99 |    96/99 |        95/99 |
| Codex / Sol                    |   95/99 |    26/99 |  Not run |      Not run |
| Codex / Luna                   |   86/99 |  16/99 † |  Not run |      Not run |
| Codex / Terra                  |   88/99 |    12/99 |  Not run |      Not run |
| Codex / Astra                  | 93/99 † |  23/99 † |  Not run |      Not run |
| Cursor / Grok 4.7 Medium       |   96/99 |  Not run |  Not run |      Not run |
| OpenCode / DeepSeek V4.1 Flash |   93/99 |     9/99 |    93/99 |      Not run |
| OpenCode / GLM 5.3 Flash       |   90/99 |  12/99 † |    87/99 |      Not run |
| OpenCode / MiMo v2.6 Pro       |   95/99 |     1/99 |    92/99 |      Not run |
| OpenCode / GLM 5.3             |   87/99 |   7/99 † |  76/99 † |      Not run |
| OpenCode / Qwen 3.8 27B        | 75/99 † |     0/99 |  85/99 † |      Not run |
| OpenCode / Gemma 4 31B         | 24/99 † |     1/99 |    76/99 |      Not run |
| OpenCode / Kimi K3             |   93/99 |     2/99 |    90/99 |      Not run |
| Mistral Vibe / Large 4         |   78/99 |  12/99 † |  Not run |      Not run |

† Execution or replay/tool-control errors are included in the denominator.
Affected no-tools arms are not clean knowledge-only controls: attempted calls
can fail the audit even when the harness blocks execution. See error counts in
the CSV and [control investigations](../methodology/pilots.md). Small score differences across
three repeats are not conclusive rankings.

## Speed and candidate cost

Median agent time excludes setup and grading. Mean candidate cost is shown only
with complete cost coverage; unknown is not zero. Full timings for every arm,
including no-tools, are in the CSV. Search fees and subscriptions are excluded.

### Native tools

| Harness / model                | Median seconds | Mean candidate USD / attempt |
| ------------------------------ | -------------: | ---------------------------: |
| Claude Code / Haiku 5.5        |           19.4 |                    $0.010582 |
| Claude Code / Sonnet 5.5       |           16.1 |                    $0.055771 |
| Claude Code / Opus 5.5         |           25.4 |                    $0.093413 |
| Claude Code / Fable 5.1        |           33.6 |                    $0.302966 |
| Claude Code / Fable 5.2        |           33.3 |                    $0.246632 |
| Codex / Sol                    |           11.1 |                    $0.051152 |
| Codex / Luna                   |           12.1 |                    $0.003356 |
| Codex / Terra                  |            8.9 |                    $0.027114 |
| Codex / Astra                  |           11.0 |     Unknown (96/99 recorded) |
| Cursor / Grok 4.7 Medium       |           25.0 |                    $0.056400 |
| OpenCode / DeepSeek V4.1 Flash |           10.9 |                    $0.001767 |
| OpenCode / GLM 5.3 Flash       |           14.0 |                    $0.003905 |
| OpenCode / MiMo v2.6 Pro       |           13.2 |                    $0.005465 |
| OpenCode / GLM 5.3             |           20.9 |                    $0.038366 |
| OpenCode / Qwen 3.8 27B        |           40.7 |                    $0.060516 |
| OpenCode / Gemma 4 31B         |           16.1 |                    $0.002411 |
| OpenCode / Kimi K3             |           15.4 |                    $0.054328 |
| Mistral Vibe / Large 4         |           27.1 |                    $0.023132 |

### Web-only tools

| Harness / model                | Median seconds | Mean candidate USD / attempt |
| ------------------------------ | -------------: | ---------------------------: |
| Claude Code / Haiku 5.5        |           17.4 |                    $0.015282 |
| Claude Code / Sonnet 5.5       |           15.2 |                    $0.049245 |
| Claude Code / Opus 5.5         |           24.8 |                    $0.086257 |
| Claude Code / Fable 5.1        |           31.7 |                    $0.259414 |
| Claude Code / Fable 5.2        |           32.7 |                    $0.228465 |
| OpenCode / DeepSeek V4.1 Flash |            9.1 |                    $0.001658 |
| OpenCode / GLM 5.3 Flash       |           18.6 |                    $0.004516 |
| OpenCode / MiMo v2.6 Pro       |           14.5 |                    $0.008090 |
| OpenCode / GLM 5.3             |           42.3 |     Unknown (81/99 recorded) |
| OpenCode / Qwen 3.8 27B        |           24.7 |                    $0.041529 |
| OpenCode / Gemma 4 31B         |            9.4 |                    $0.000775 |
| OpenCode / Kimi K3             |           24.9 |                    $0.106938 |

### Native tools with guide MCP

| Harness / model         | Median seconds | Mean candidate USD / attempt |
| ----------------------- | -------------: | ---------------------------: |
| Claude Code / Fable 5.2 |           12.5 |                    $0.136886 |

Known candidate usage totals **$263.56**, with cost coverage for **4723/4,752** attempts, plus **$19.37** of recorded judge usage. These are estimates, not billing reconciliation.

## Interpretation

Fable 5.2 passed 321/396 overall, with no execution or grading errors. Its
native+MCP arm made guide MCP calls in 87/99 traces and had a 12.5-second median,
versus 33.3 seconds native. Similar observed success does not establish
statistical equivalence or isolate the effects of MCP instructions. See
[trace findings](../analysis/README.md) for retrieval and citation differences.

Historical scores are unchanged. The original latest-release check expects 8.0,
even when a retrieved 8.1 answer is supported. Future-only [grading corrections](../methodology/grading.md)
address this and overly literal multi-tenancy wording. Passing `UNKNOWN:` judge
results retain the original behavior and are counted in the CSV.

The [Claude/Promptfoo comparison](claude-comparison.md) describes the older
controlled-site experiment. [Energy results](energy.md) provide
illustrative Neuralwatt arm medians. [Methodology](../README.md) explains controls,
accounting and reproduction. Raw runs stay in the local Harbor cache; the batch
column identifies their source directories.
