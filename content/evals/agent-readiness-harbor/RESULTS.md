# Harbor agent readiness results

**All 4,356 planned candidate trials and their grades completed on 7 November 2026.** This covers 17 model/harness pairs, 44 supported model/tool-arm combinations, 33 questions and three repeats per arm. The last candidate finished at 04:12 UTC. The final audit found exactly three results per question per arm, one grade per trial, and the same source-case/grader hash across all three batches.

Harbor ran the installed agents; Promptfoo graded saved answers using the original assertions and Sonnet 5.5 rubric. See the [method and question breakdown](README.md), [historical Claude comparison](CLAUDE_COMPARISON.md), and [all 44 result rows](RESULTS.csv). The original 3,168-run matrix and subsequent 1,188-run Neuralwatt expansion are combined here; integration pilots and credential probes are excluded.

## Success by tool arm

Every cell uses all 99 planned answers as its denominator, including execution failures. Success requires passing every original assertion. Native means default harness tools; baseline means the intended no-usable-tools control; web means search/fetch only. These compare model plus harness, not an isolated harness effect.

| Harness / model                |  Native | No tools | Web-only |
| ------------------------------ | ------: | -------: | -------: |
| Claude Code / Haiku 5.5        |   78/99 |     9/99 |    82/99 |
| Claude Code / Sonnet 5.5       |   83/99 |    15/99 |    84/99 |
| Claude Code / Opus 5.5         |   89/99 |    34/99 |    87/99 |
| Claude Code / Fable 5.1        |   91/99 |    37/99 |    93/99 |
| Codex / Sol                    |   95/99 |    26/99 |  Not run |
| Codex / Luna                   |   86/99 |  16/99 † |  Not run |
| Codex / Terra                  |   88/99 |    12/99 |  Not run |
| Codex / Astra                  | 93/99 † |  23/99 † |  Not run |
| Cursor / Grok 4.7 Medium       |   96/99 |  Not run |  Not run |
| OpenCode / DeepSeek V4.1 Flash |   93/99 |     9/99 |    93/99 |
| OpenCode / GLM 5.3 Flash       |   90/99 |  12/99 † |    87/99 |
| OpenCode / MiMo v2.6 Pro       |   95/99 |     1/99 |    92/99 |
| OpenCode / GLM 5.3             |   87/99 |   7/99 † |  76/99 † |
| OpenCode / Qwen 3.8 27B        | 75/99 † |     0/99 |  85/99 † |
| OpenCode / Gemma 4 31B         | 24/99 † |     1/99 |    76/99 |
| OpenCode / Kimi K3             |   93/99 |     2/99 |    90/99 |
| Mistral Vibe / Large 4         |   78/99 |  12/99 † |  Not run |

† This arm contains execution or replay/tool-audit errors; see the validity table below. In particular, the flagged no-tools arms are not clean measurements of knowledge without tools. Rejected traces were not converted into ordinary answer failures or silently omitted from the denominator.

Grok had the highest observed native score (96/99); Sol and MiMo each scored 95/99. DeepSeek and Kimi each scored 93/99 without execution errors. These small score differences should not be treated as conclusive rankings from only three repeats. Gemma showed a much larger arm difference: 24/99 with native tools versus 76/99 with web-only tools; this experiment does not isolate the cause.

## Speed and candidate cost

Time is median agent execution time, excluding installation, container setup and grading. Cost is mean reported/estimated candidate API usage per planned answer, shown only where all 99 costs are available. Missing values remain unknown. Installation often took about a minute per trial and dominated overall wall time; it is recorded separately in the CSV.

### Native tools

| Harness / model                | Median seconds |       Mean candidate USD |
| ------------------------------ | -------------: | -----------------------: |
| Claude Code / Haiku 5.5        |           19.4 |                $0.010582 |
| Claude Code / Sonnet 5.5       |           16.1 |                $0.055771 |
| Claude Code / Opus 5.5         |           25.4 |                $0.093413 |
| Claude Code / Fable 5.1        |           33.6 |                $0.302966 |
| Codex / Sol                    |           11.1 |                $0.051152 |
| Codex / Luna                   |           12.1 |                $0.003356 |
| Codex / Terra                  |            8.9 |                $0.027114 |
| Codex / Astra                  |           11.0 | Unknown (96/99 recorded) |
| Cursor / Grok 4.7 Medium       |           25.0 |                $0.056400 |
| OpenCode / DeepSeek V4.1 Flash |           10.9 |                $0.001767 |
| OpenCode / GLM 5.3 Flash       |           14.0 |                $0.003905 |
| OpenCode / MiMo v2.6 Pro       |           13.2 |                $0.005465 |
| OpenCode / GLM 5.3             |           20.9 |                $0.038366 |
| OpenCode / Qwen 3.8 27B        |           40.7 |                $0.060516 |
| OpenCode / Gemma 4 31B         |           16.1 |                $0.002411 |
| OpenCode / Kimi K3             |           15.4 |                $0.054328 |
| Mistral Vibe / Large 4         |           27.1 |                $0.023132 |

### Web-only tools

| Harness / model                | Median seconds |       Mean candidate USD |
| ------------------------------ | -------------: | -----------------------: |
| Claude Code / Haiku 5.5        |           17.4 |                $0.015282 |
| Claude Code / Sonnet 5.5       |           15.2 |                $0.049245 |
| Claude Code / Opus 5.5         |           24.8 |                $0.086257 |
| Claude Code / Fable 5.1        |           31.7 |                $0.259414 |
| OpenCode / DeepSeek V4.1 Flash |            9.1 |                $0.001658 |
| OpenCode / GLM 5.3 Flash       |           18.6 |                $0.004516 |
| OpenCode / MiMo v2.6 Pro       |           14.5 |                $0.008090 |
| OpenCode / GLM 5.3             |           42.3 | Unknown (81/99 recorded) |
| OpenCode / Qwen 3.8 27B        |           24.7 |                $0.041529 |
| OpenCode / Gemma 4 31B         |            9.4 |                $0.000775 |
| OpenCode / Kimi K3             |           24.9 |                $0.106938 |

Known candidate usage totals **$198.15**, plus **$17.56** of recorded judge usage: **$215.71 known usage overall**. Candidate cost coverage is 4,327/4,356, so this is not a complete bill. Pilots, credential probes and interrupted partial attempts are excluded. Neuralwatt figures use snapshotted token prices, not account credits, energy-based invoices or negotiated rates. Search fees, subscriptions, caching and billing adjustments can change actual charges.

## Failures and control validity

There were **38 Harbor execution failures**: 31 agent timeouts at the existing 300-second cap and seven setup/network failures. An additional **195 completed outputs were rejected by replay**, all in intended no-tools arms, for attempted tool use, nonempty tool discovery or unfinished tool-call trajectories. There were **zero grading-system errors**.

| Arm                         | Execution/replay errors | Detail                                                                                                                             |
| --------------------------- | ----------------------: | ---------------------------------------------------------------------------------------------------------------------------------- |
| codex-luna--baseline        |                      25 | 25 rejected tool-attempt traces.                                                                                                   |
| codex-astra--native         |                       3 | Three CLI setup/network failures.                                                                                                  |
| codex-astra--baseline       |                       5 | Four setup failures and one timeout.                                                                                               |
| opencode-glm--baseline      |                      31 | 31 rejected traces, including seven ending with a tool call and no final answer.                                                   |
| vibe-large--baseline        |                      72 | 72 rejected traces; discovery sometimes exposed tools and attempted execution followed. Sampled shell calls were denied by policy. |
| opencode-glm-full--baseline |                      73 | Six timeouts and 67 replay rejections.                                                                                             |
| opencode-glm-full--web      |                      19 | 19 timeouts.                                                                                                                       |
| opencode-qwen--native       |                       1 | One timeout.                                                                                                                       |
| opencode-qwen--web          |                       2 | Two timeouts.                                                                                                                      |
| opencode-gemma--native      |                       2 | Two timeouts.                                                                                                                      |

The strict baseline audit rejects attempted calls even when the harness blocks execution. A rejection therefore does not automatically mean the model successfully fetched information. No control or grader was relaxed during these runs. Failed trials were preserved, not selectively rerun to improve scores.

The original rubric allows a passing `UNKNOWN:` judgment. There were 277 such rubric judgments, but only three answers containing them passed all other assertions: Luna native and Terra native on `releases-7-3-to-8-0-overview`, and Vibe native on `info-stale-pages`. These remain included in the published scores, matching the original grading rules. Most UNKNOWN judgments occurred in baseline answers that still failed fact/citation assertions.

## Reproduction and limits

- Harbor 0.25.0. Claude Code 2.1.318; Codex 0.166.0; Cursor 2026.11.05-86047df; OpenCode 1.19.5; Vibe 3.1.0.
- Live production site, fixed 33-question snapshot, three repeats and a 300-second agent cap. Harness/provider reasoning defaults differ. Claude additionally used the original 30-turn and $1 per-trial CLI caps.
- At most three candidate agents within each benchmark job. Small integration pilots briefly overlapped benchmark work. The four-model expansion waited for the original remaining batch to finish.
- The original remaining batch stopped after 1,215 results; Harbor resumed the incomplete GLM Flash native job under systemd. Completed candidates and their grades were reused. The cause of the interruption was not established.
- Expansion credentials explicitly excluded the inherited Neuralwatt environment key: GLM and Qwen used matching file keys; Gemma and Kimi used the validated GLM fallback after their matching keys returned HTTP 401. Initial smoke tests used the inherited key. See the pilot report for details.
- Cursor has no supported no-tools arm. OpenClaw remains deferred. Kimi K3.1 Pro passed separate preview smoke tests but is excluded from this full matrix; its candidate pricing is unknown.
- Historical Promptfoo results differ in site/proxy state, CLI version and run date. Use the separate Claude comparison for matched historical subsets; these runs do not reproduce the old site-feature ablation.

Raw manifests, tasks, native transcripts, ATIF trajectories, grades and per-batch CSVs remain under `~/.cache/guide-agent-eval/harbor/` in `claude-comparison-2026-11-05/`, `remaining-comparison-2026-11-05/` and `neuralwatt-expansion-comparison-2026-11-06/`. The CSV alongside this report adds a batch column so every row can be traced back to those artifacts.
