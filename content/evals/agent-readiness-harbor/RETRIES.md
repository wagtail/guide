# Follow-up runs, 7 November 2026

The user requested one retry of every failed full-suite trial, another Kimi K3.1 Pro preview trial, and an investigation of Codex web-only tools.

## Failed-trial retries

The retry queue contains **1,761 trials across 44 model/arm jobs**. This includes failed assertions and all 233 execution/audit errors. Each original failed attempt gets one retry, including multiple failures of the same question. Passing original trials are excluded.

| Original batch       | Non-passing trials to retry |
| -------------------- | --------------------------: |
| Claude comparison    |                         406 |
| Remaining harnesses  |                         783 |
| Neuralwatt expansion |                         572 |
| Total                |                       1,761 |

These are native Harbor jobs with an explicit `tasks` list and `n_attempts: 1`. Each task's `source` maps through the manifest's `retry_sources` to the exact original `result.json` path. The original case, tool settings, CLI version, timeout, concurrency and pricing snapshot are retained. Cursor's installer still selects latest; check its recorded version before comparing. No new agent adapter is involved.

Each job has a separate export directory. Its manifest intentionally repeats case records when multiple original attempts failed, so the existing report's denominator equals the number of retries. Grading still looks up the original case by task name. The original 4,356 results and their scores remain unchanged. A recovery rate among selected failures is not a fresh full-suite success rate.

Artifacts are under `~/.cache/guide-agent-eval/harbor/failed-retries-2026-11-07/`:

- `plan.json`: exact job counts and original batch locations.
- `<job>/manifest.json` and `<job>/<job>.json`: exported cases and native Harbor configurations.
- `<job>/jobs/`: retry answers, trajectories and execution results.
- `<job>/grades.json` and `<job>/comparison.csv`: the existing Promptfoo grades and report.
- `outcomes.json`: original-to-retry links and whether each retry passed.
- `recovery.csv`: per-arm recovery, speed, cost and errors, updated after each job is graded.

Two user services run the candidate queue and grade completed jobs independently:

```sh
systemctl --user status agent-readiness-failed-retries-candidates-20261107.service
systemctl --user status agent-readiness-failed-retries-grades-20261107.service
```

Logs are `candidates.log` and `grades.log` in the batch directory. Completed jobs have `candidates.done` markers; the entire queues create `candidates.done` and `grades.done` at the batch root. If interrupted, the local queue script uses Harbor's native job resume, retaining completed failures instead of repeatedly retrying them.

The first eight candidate retries completed, but Harbor's terminal summary crashed because original trial paths contain its `__` grouping delimiter. Those eight results were preserved. Unstarted jobs now use delimiter-safe source IDs with the same original-trial mapping; this changes bookkeeping only.

The services unset inherited `NEURALWATT_API_KEY` so file-key selection takes effect. Direct requests on 7 November returned HTTP 200 for the matching DeepSeek, GLM Flash, MiMo, GLM 5.3 and Qwen keys. Gemma and Kimi retain the validated GLM 5.3 fallback. This credential selection differs from older jobs where the inherited key took precedence; model IDs and provider endpoint are unchanged.

## Kimi K3.1 Pro retry

The requested `neuralwatt/kimi-k3.1-pro` trial passed the original scheduling-question checks again, using OpenCode 1.19.5 and the explicit GLM 5.3 fallback key. Agent execution took **38.80 seconds**; setup took 74.43 seconds. Candidate cost remains unknown because preview pricing is unavailable. Judge cost was $0.0038611.

Artifacts: `~/.cache/guide-agent-eval/harbor/kimi-preview-retry-2026-11-07/`. This is one integration check, outside the main benchmark matrix.

## Codex web-only investigation

Web-only was originally omitted because it had not been validated. Harbor does expose Codex's `web_search` and native configuration options. The [OpenAI configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) documents separate web-search and shell-tool controls.

The new pilot uses the same CLI 0.166.0 and scheduling question as the existing comparison, with `web_search: live`, shell/editing/agent/image tools disabled, code mode disabled and plan updates disabled. Sol, Luna, Terra and Astra nevertheless attempted `exec` calls to browse; the calls returned `code-mode host is disabled`. An additional Sol trial with `features.standalone_web_search: true` behaved the same way. All five trials were rejected as invalid controls. These trials do not establish a usable web-only arm.

Replay now explicitly rejects non-web tool calls in Codex web-only experiments, including opaque `exec` and `js_repl` calls. It does not change grading for any original arm. Merely turning code mode back on would require validating which nested tools remain available and how their calls can be audited; an opaque wrapper is insufficient evidence of a web-only run. No custom agent adapter was added, and Codex web-only remains outside `arms.yaml` and the full matrix.

Artifacts: `~/.cache/guide-agent-eval/harbor/codex-web-pilot-2026-11-07/` for the four-model pilot and `codex-web-standalone-pilot-2026-11-07/` for the additional native-flag check. These diagnostic results are separate from both the original benchmark and the failed-trial retry queue.
