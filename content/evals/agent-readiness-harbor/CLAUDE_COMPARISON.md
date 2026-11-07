# Claude Code: Harbor and historical Promptfoo results

Completed on 5 November 2026: **1,188 candidate answers**, comprising four models × three tool arms × 33 questions × three repeats. All answers were graded with the original Promptfoo assertions and Sonnet 5.5 rubric. The [October Promptfoo results](../agent-readiness/RESULTS.md) provide the historical comparison; those candidates were not rerun.

## All Harbor results

Success requires passing every original assertion. Time is mean agent execution time, excluding container setup, installation and grading. Cost is mean reported candidate API cost; judge costs are separate.

| Model      | Tools    | Passed | Success | Mean seconds | Mean candidate cost |
| ---------- | -------- | -----: | ------: | -----------: | ------------------: |
| Haiku 5.5  | native   |  78/99 |   78.8% |         18.7 |             $0.0106 |
| Haiku 5.5  | baseline |   9/99 |    9.1% |          6.4 |             $0.0006 |
| Haiku 5.5  | web      |  82/99 |   82.8% |         17.8 |             $0.0153 |
| Sonnet 5.5 | native   |  83/99 |   83.8% |         16.9 |             $0.0558 |
| Sonnet 5.5 | baseline |  15/99 |   15.2% |          9.7 |             $0.0100 |
| Sonnet 5.5 | web      |  84/99 |   84.8% |         15.6 |             $0.0492 |
| Opus 5.5   | native   |  89/99 |   89.9% |         28.3 |             $0.0934 |
| Opus 5.5   | baseline |  34/99 |   34.3% |         12.0 |             $0.0209 |
| Opus 5.5   | web      |  87/99 |   87.9% |         25.0 |             $0.0863 |
| Fable 5.1  | native   |  91/99 |   91.9% |         35.5 |             $0.3030 |
| Fable 5.1  | baseline |  37/99 |   37.4% |         21.2 |             $0.0676 |
| Fable 5.1  | web      |  93/99 |   93.9% |         32.4 |             $0.2594 |

## Comparison with Promptfoo

Only the no-tools and web-only arms have historical counterparts. Opus is restricted here to the same 28 questions as October, excluding the five site-start cases (84 answers per arm). All other comparisons use 33 questions (99 answers per arm). Historical figures are rounded as published.

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

Web-only speed and cost, using means for both runners:

| Model      | Promptfoo seconds | Harbor seconds | Promptfoo cost/answer | Harbor cost/answer |
| ---------- | ----------------: | -------------: | --------------------: | -----------------: |
| Haiku 5.5  |                22 |           17.8 |                $0.016 |            $0.0153 |
| Sonnet 5.5 |                17 |           15.6 |                $0.028 |            $0.0492 |
| Opus 5.5   |                28 |           24.3 |                $0.046 |            $0.0855 |
| Fable 5.1  |                36 |           32.4 |                $0.133 |            $0.2594 |

## Run quality and interpretation

The run recorded 0 execution errors, 0 grading errors and 2 passing UNKNOWN rubric judgments. Both UNKNOWN judgments were Opus no-tools answers to `info-stale-pages`; both answers failed deterministic assertions, so neither contributed to the success totals. Candidate cost coverage was 1,188/1,188. Total reported candidate cost was **$96.23**, with **$5.84** of judge usage ($102.07 combined). These are usage estimates, not an invoice; search charges and billing adjustments may differ.

This is a historical comparison, not a controlled measurement of Harbor's effect. The October eval used a local site copy through a proxy, with live search; this run used the live production site. CLI versions, site/search state, caching and judge randomness can affect differences. Three repeats do not make a small score difference conclusive. Native-tool scores have no equivalent historical arm.

## Reproduction and artifacts

- Harbor 0.25.0; Claude Code 2.1.318 for every trial; explicit model IDs in the manifest.
- Original cases, assertions, judge, hidden reference answers and trace grading reused unchanged. The manifest records their source hash.
- Agent limits: 300 seconds, 30 turns and a $1 CLI budget per trial. Three Claude candidate agents at a time. Sonnet, Opus and Fable allowed six concurrent trial lifecycles to overlap setup/cleanup while retaining three concurrent agent executions.
- The pinned Claude CLI was preinstalled in task images after the first few cold starts. Setup is reported separately and excluded from the timings above. A small non-Claude integration smoke batch ran at concurrency one during the later Claude jobs.
- Baseline disables all usable tools; web exposes WebSearch and WebFetch; native uses default tools. Replay audits no-tools trajectories before grading. The final audit confirmed zero tool calls across all 396 baseline trials, only WebSearch/WebFetch in all 396 web trials, exactly three repeats per case, and at most three simultaneous Claude agents in every arm.

Artifacts are under `~/.cache/guide-agent-eval/harbor/claude-comparison-2026-11-05/`: `manifest.json`, `audit.json`, `jobs/` with native transcripts and ATIF, `grades.json`, per-arm `grading/` exports, `comparison.csv` with medians and coverage, and `historical-comparison.csv` with the means and matched Opus subset used here. The temporary aggregation scripts live alongside these artifacts; no custom agent loop was added for this comparison.
