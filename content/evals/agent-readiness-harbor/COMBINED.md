# Agent readiness: initial runs plus one retry

**All 4,356 original trials and 1,761 retries are complete and graded.** The combined comparison covers 17 model/harness pairs and 44 supported tool arms, with 99 scored trials per arm. There were 6,117 candidate attempts in total. Pilots, key probes, OpenClaw and the Kimi K3.1 Pro preview are excluded.

Use the native-tools tables to compare all 17 pairs on the same 33 questions and three repeats. Compare web-only or no-tools results within those arms; unsupported arms remain “Not run.” These are model-plus-harness comparisons, not isolated measurements of the harness itself.

The [complete CSV](COMBINED.csv) contains all 44 rows, first-attempt and combined scores, retry counts, cumulative timing, cost coverage and error counts. The [original report](RESULTS.md) and [original CSV](RESULTS.csv) retain first-attempt results.

With native tools, eight pairs tie at **96/99**. Among those ties with complete cost data, **OpenCode / DeepSeek V4.1 Flash has the lowest measured candidate cost: $0.002064 per scored trial**, including retries, with 11.2-second median cumulative agent execution. Codex / Terra has the lowest native median, 9.2 seconds, at 90/99. These observations describe this fixed benchmark and its pricing snapshots.

## How the combination works

- A first-attempt pass is kept. Every original non-passing attempt, including execution/audit errors, received exactly one fresh retry with the same question and tool arm. A trial passes the combined score if either attempt passed all original assertions.
- The denominator stays at 99 per arm. Retries are linked to their exact original trial, so repeated questions remain three separate scored trials. Failed original attempts are not appended as extra scored questions or dropped.
- Time and cost include both attempts for retried trials, including the unsuccessful first attempt. Mean candidate cost divides total candidate usage by 99; cost per success divides it by the combined number of passes.
- Retry selection used the benchmark grader. This is success with a grading-triggered second chance, not evidence that an agent can detect its own mistakes. The initial and retry attempts used the same prompt; the retry was not given the first answer or grading feedback.
- The original graders, strict tool audit and passing `UNKNOWN:` behavior are unchanged. No candidate or judge calls were made to combine the saved results.

## Success by tool arm

Each cell shows **initial passes → combined passes, out of 99**. Missing arms are not treated as failures.

| Harness / model                |    Native |  No tools |  Web-only |
| ------------------------------ | --------: | --------: | --------: |
| Claude Code / Haiku 5.5        |   78 → 82 |     9 → 9 |   82 → 87 |
| Claude Code / Sonnet 5.5       |   83 → 87 |   15 → 17 |   84 → 91 |
| Claude Code / Opus 5.5         |   89 → 93 |   34 → 37 |   87 → 92 |
| Claude Code / Fable 5.1        |   91 → 96 |   37 → 41 |   93 → 96 |
| Codex / Sol                    |   95 → 96 |   26 → 32 |   Not run |
| Codex / Luna                   |   86 → 90 | 16 → 19 † |   Not run |
| Codex / Terra                  |   88 → 90 | 12 → 12 † |   Not run |
| Codex / Astra                  | 93 → 96 † | 23 → 30 † |   Not run |
| Cursor / Grok 4.7 Medium       |   96 → 96 |   Not run |   Not run |
| OpenCode / DeepSeek V4.1 Flash |   93 → 96 |    9 → 10 |   93 → 95 |
| OpenCode / GLM 5.3 Flash       |   90 → 96 | 12 → 13 † |   87 → 92 |
| OpenCode / MiMo v2.6 Pro       |   95 → 96 |     1 → 2 |   92 → 96 |
| OpenCode / GLM 5.3             |   87 → 92 |  7 → 11 † | 76 → 95 † |
| OpenCode / Qwen 3.8 27B        | 75 → 85 † |     0 → 2 | 85 → 91 † |
| OpenCode / Gemma 4 31B         | 24 → 27 † |     1 → 2 |   76 → 78 |
| OpenCode / Kimi K3             |   93 → 96 |     2 → 4 |   90 → 92 |
| Mistral Vibe / Large 4         |   78 → 85 | 12 → 12 † |   Not run |

† At least one attempt in this arm had an execution or replay/tool-audit error. Those attempts remain included in time, cost and the trial denominator. In particular, affected no-tools arms are not clean knowledge-only controls; the audit rejects attempted tool calls even if execution was blocked.

## Speed and candidate cost

Timing is measured per scored trial: initial agent execution plus retry agent execution when a retry occurred. Median and mean summarize these cumulative values across the 99 trials; they are not sums of per-run medians. Setup and judge latency are excluded. The CSV separately records cumulative setup time.

Medians use only trials with timing recorded for every attempt; partial coverage is shown. Means are shown only with complete coverage. Unknown costs remain unknown, even when a later retry succeeded. Candidate prices are the original token-price estimates, not invoices; search fees, subscriptions and credits may differ. The mean cost is per scored trial, including unsuccessful trials.

### Native tools

| Harness / model                | Median total agent seconds | Mean total agent seconds |        Mean candidate USD / trial | Candidate USD / success |
| ------------------------------ | -------------------------: | -----------------------: | --------------------------------: | ----------------------: |
| Claude Code / Haiku 5.5        |                       20.7 |                     22.9 |                         $0.012921 |               $0.015600 |
| Claude Code / Sonnet 5.5       |                       17.5 |                     19.9 |                         $0.063707 |               $0.072494 |
| Claude Code / Opus 5.5         |                       27.3 |                     32.0 |                         $0.104402 |               $0.111138 |
| Claude Code / Fable 5.1        |                       34.9 |                     38.9 |                         $0.334505 |               $0.344959 |
| Codex / Sol                    |                       11.5 |                     12.5 |                         $0.053092 |               $0.054751 |
| Codex / Luna                   |                       12.5 |                     17.3 |                         $0.003910 |               $0.004301 |
| Codex / Terra                  |                        9.2 |                     10.4 |                         $0.030256 |               $0.033281 |
| Codex / Astra                  |               11.1 (96/99) |                  Unknown | Unknown (102/105 attempts priced) |                 Unknown |
| Cursor / Grok 4.7 Medium       |                       25.1 |                     30.1 |                         $0.058349 |               $0.060172 |
| OpenCode / DeepSeek V4.1 Flash |                       11.2 |                     13.6 |                         $0.002064 |               $0.002128 |
| OpenCode / GLM 5.3 Flash       |                       14.1 |                     23.0 |                         $0.004555 |               $0.004697 |
| OpenCode / MiMo v2.6 Pro       |                       13.7 |                     16.2 |                         $0.005832 |               $0.006014 |
| OpenCode / GLM 5.3             |                       21.9 |                     32.5 |                         $0.049281 |               $0.053030 |
| OpenCode / Qwen 3.8 27B        |                       45.4 |                     82.4 |                         $0.087082 |               $0.101425 |
| OpenCode / Gemma 4 31B         |                       28.9 |                     40.8 |                         $0.004956 |               $0.018172 |
| OpenCode / Kimi K3             |                       15.7 |                     19.9 |                         $0.059947 |               $0.061820 |
| Mistral Vibe / Large 4         |                       31.4 |                     37.2 |                         $0.028566 |               $0.033271 |

### Web-only tools

| Harness / model                | Median total agent seconds | Mean total agent seconds |        Mean candidate USD / trial | Candidate USD / success |
| ------------------------------ | -------------------------: | -----------------------: | --------------------------------: | ----------------------: |
| Claude Code / Haiku 5.5        |                       18.1 |                     21.4 |                         $0.018245 |               $0.020761 |
| Claude Code / Sonnet 5.5       |                       15.6 |                     18.1 |                         $0.057016 |               $0.062028 |
| Claude Code / Opus 5.5         |                       25.7 |                     28.1 |                         $0.097081 |               $0.104467 |
| Claude Code / Fable 5.1        |                       32.8 |                     34.3 |                         $0.274333 |               $0.282906 |
| OpenCode / DeepSeek V4.1 Flash |                        9.1 |                     12.0 |                         $0.001957 |               $0.002039 |
| OpenCode / GLM 5.3 Flash       |                       18.8 |                     24.5 |                         $0.004832 |               $0.005199 |
| OpenCode / MiMo v2.6 Pro       |                       15.2 |                     19.1 |                         $0.008551 |               $0.008818 |
| OpenCode / GLM 5.3             |                       43.0 |                     99.3 | Unknown (104/122 attempts priced) |                 Unknown |
| OpenCode / Qwen 3.8 27B        |                       25.7 |                     59.3 |                         $0.059454 |               $0.064681 |
| OpenCode / Gemma 4 31B         |                       10.1 |                     12.7 |                         $0.001126 |               $0.001429 |
| OpenCode / Kimi K3             |                       26.7 |                     29.9 |                         $0.116745 |               $0.125627 |

### No-tools control

| Harness / model                | Median total agent seconds | Mean total agent seconds |        Mean candidate USD / trial | Candidate USD / success |
| ------------------------------ | -------------------------: | -----------------------: | --------------------------------: | ----------------------: |
| Claude Code / Haiku 5.5        |                       12.0 |                     12.4 |                         $0.001069 |               $0.011761 |
| Claude Code / Sonnet 5.5       |                       18.3 |                     17.9 |                         $0.018703 |               $0.108919 |
| Claude Code / Opus 5.5         |                       21.4 |                     20.2 |                         $0.035343 |               $0.094566 |
| Claude Code / Fable 5.1        |                       32.3 |                     34.0 |                         $0.114377 |               $0.276179 |
| Codex / Sol                    |                       21.0 |                     20.1 |                         $0.048738 |               $0.150782 |
| Codex / Luna                   |                       28.0 |                     28.3 |                         $0.003210 |               $0.016727 |
| Codex / Terra                  |               13.1 (98/99) |                  Unknown | Unknown (185/186 attempts priced) |                 Unknown |
| Codex / Astra                  |               24.2 (95/99) |                  Unknown | Unknown (170/175 attempts priced) |                 Unknown |
| OpenCode / DeepSeek V4.1 Flash |                       11.6 |                     12.5 |                         $0.000554 |               $0.005488 |
| OpenCode / GLM 5.3 Flash       |                       19.7 |                     27.4 |                         $0.001854 |               $0.014122 |
| OpenCode / MiMo v2.6 Pro       |                       11.8 |                     13.0 |                         $0.000687 |               $0.034011 |
| OpenCode / GLM 5.3             |               54.1 (98/99) |                  Unknown | Unknown (187/191 attempts priced) |                 Unknown |
| OpenCode / Qwen 3.8 27B        |                       16.0 |                     20.0 |                         $0.004752 |               $0.235217 |
| OpenCode / Gemma 4 31B         |                       10.1 |                     10.5 |                         $0.000107 |               $0.005301 |
| OpenCode / Kimi K3             |                       19.4 |                     22.9 |                         $0.031353 |               $0.775996 |
| Mistral Vibe / Large 4         |                       44.4 |                     43.5 |                         $0.043228 |               $0.356632 |

## Totals and interpretation

Across this particular matrix, the original score was **2,595/4,356 (59.6%)**. Retrying every failed trial recovered **162/1,761 (9.2%)**, giving **2,757/4,356 (63.3%)** with one retry; **1,599** trials still fail. These totals describe the run inventory, not a fair overall harness ranking, because harnesses support different numbers of arms.

Known candidate usage was **$198.15 initially + $47.83 for retries = $245.98**. Recorded judging adds **$24.00**, for **$269.98 known total usage**. Candidate cost is recorded for **6,086/6,117 attempts**; the rest are unknown. This excludes separate pilots, credential probes and interrupted partial attempts.

The initial run had 233 execution/replay errors, and retries had 194. The final selected answers still have 194 execution/replay errors. There were 0 grading-system errors in the saved grades. 3 final passing answers contain an `UNKNOWN:` judgment, retained under the original rules. Per-arm counts and trials with an error in either attempt are in the CSV.

The native results now have eight pairs tied at 96/99: Fable, Sol, Astra, Grok, DeepSeek, GLM Flash, MiMo and Kimi. Three repeats of 33 questions do not establish a reliable ordering between close scores. Use the cumulative speed and cost columns to assess the tradeoffs, while retaining the first-attempt scores when comparing reliability without a grading-triggered retry.

## Audit and provenance

- The join checks 4,356 unique original trials, exactly 1,761 distinct retries, and exactly one retry for each original failure and none for an original pass. Every model/arm retains all 33 questions with three repeats.
- Source-case/grader hashes, task checksums and model identities match across each pair. CLI versions are recorded separately for initial and retry attempts in the CSV. Cursor recorded the same version in both batches despite its always-latest installer.
- Tool settings, timeouts and pricing snapshots were retained. The retry services explicitly selected Neuralwatt file keys; some older original jobs used an inherited key. The live site, API load, caches and run dates can still affect timing or behavior.
- All candidate retries finished on 7 November 2026 at 22:20 UTC. Grading completed on 8 November after fixing a reporting-only JSON/YAML reader mismatch; saved grades and candidate answers were reused.
- [Retry notes](RETRIES.md) document the native Harbor task exports, credential handling and rejected Codex web-only pilots.

Raw data remain under `~/.cache/guide-agent-eval/harbor/`: the three original comparison directories and `failed-retries-2026-11-07/`. The analysis retains an exact pairing ledger in `combined-initial-retries-pairs.json` and aggregate totals in `combined-initial-retries-summary.json`. `combine_initial_retries.py` in that cache directory regenerates the CSV from saved results without paid calls.
