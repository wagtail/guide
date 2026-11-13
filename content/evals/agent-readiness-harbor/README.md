# Agent readiness with Harbor

Harbor runs the [33 agent-readiness questions](../agent-readiness/README.md) through native coding agents. Promptfoo grades saved answers with the shared assertions and Sonnet 5.5 rubric.

**[Results and findings](results/README.md)** covers success, speed, cost, retries, MCP, search, traces and energy.

## Files

| Path             | Contents                                                |
| ---------------- | ------------------------------------------------------- |
| `results/`       | Consolidated report and benchmark CSVs.                 |
| `analysis/data/` | Trace statistics, definitions and evidence coverage.    |
| `config/`        | Model matrix, tool arms, run sources and review rubric. |
| `scripts/`       | Runner, answer replay and trace analysis.               |
| `tests/`         | Offline regression tests.                               |

## Configuration

The [matrix](config/matrix.yaml) contains 18 full-suite model/harness pairs and an opt-in Kimi K3.1 Pro preview. Select models with `--entry`; use [arms.yaml](config/arms.yaml) for tool controls.

| Harness               | Supported arms                            |
| --------------------- | ----------------------------------------- |
| Claude Code, OpenCode | `native`, `baseline`, `web`, `native+mcp` |
| Codex                 | `native`, `baseline`, `native+mcp`        |
| Cursor                | `native`, `native+mcp`                    |
| Mistral Vibe          | `native`, `baseline`, `native+mcp`        |

- `native`: default harness tools.
- `baseline`: no usable tools; attempted tool calls fail the audit.
- `web`: search and fetch.
- `native+mcp`: native tools plus `https://guide.wagtail.org/mcp`.
- OpenCode search follow-ups used the Tavily MCP (`search_provider: tavily`).

## Run

Requirements: Docker, Node, `just`, `uv` and provider credentials. Harbor 0.25.0 is pinned.

- Keys: environment variables, then `~/dev/.keys.yml`; override with `--keys`.
- Tavily also reads a literal `TAVILY_API_KEY` assignment from `~/.extra`.
- Use a fresh output directory for each experiment.
- Preparation is offline except for version/catalog lookups. Execution and grading make paid calls.

```sh
just eval-agents-init
just eval-agents-harbor doctor
just eval-agents-harbor prepare ~/.cache/guide-agent-eval/harbor/pilot \
  --entry claude-fable-5-2 --case info-schedule-page \
  --arms native,baseline,web,native+mcp --repeat 1
just eval-agents-harbor run ~/.cache/guide-agent-eval/harbor/pilot
just eval-agents-harbor grade ~/.cache/guide-agent-eval/harbor/pilot
just eval-agents-harbor report ~/.cache/guide-agent-eval/harbor/pilot
just eval-agents-harbor-cli view ~/.cache/guide-agent-eval/harbor/pilot/jobs
```

All default models with `--arms native,baseline,web --repeat 3` produce **4,653 candidate runs**, plus grading. The preview requires an explicit `--entry` selection. Default limits are 300 seconds per attempt and one concurrent trial per job; spending scales with selected jobs and repeats.

## Grading and reruns

- Cases: 15 information, eight troubleshooting, six release, three developer-routing and one guide-to-developer question.
- Framing: 19 name the guide, nine ask for official documentation, five start at the site.
- Success requires all checks to pass. The original rubric accepts passing `UNKNOWN:` judgments.
- Historical results retain their original grades.
- New evaluations pin the release question to 8.0 and accept broader multi-tenancy database wording. Both cases carry grading revision 2.
- Manifests record cases, source hashes and CLI versions; grading enforces the source hash.
- For before/after runs, match grading, model/CLI versions, tools, timeouts and repeats; record the site revision and deployment time.
- Fresh preparation resolves unpinned CLI versions. Cursor installs the current version.
- Compare within matching arms and phases. Each pair measures the model together with its harness.

## Analyze saved traces

```sh
just eval-agents-traces --output ~/.cache/guide-agent-eval/harbor/trace-analysis
just eval-agents-trace-review ~/.cache/guide-agent-eval/harbor/trace-analysis --stage-only --limit 16
```

- Extraction reads the runs in [trace-sources.yaml](config/trace-sources.yaml).
- Outputs include `trials.jsonl`, `events.jsonl`, `instructions.jsonl`, retry links and CSV statistics.
- IDs derive from original trial paths; retain those IDs when moving data.
- Event exports contain tool metadata; original trajectories contain full returned observations.
- Optional paid Harbor review: omit `--stage-only`. Inspect its evidence-linked findings against the saved traces.
- Metrics retain missing/opaque coverage. Source-support review uses the original returned passages.

## Verify

```sh
just eval-agents-harbor-test
just eval-agents-check
just lint
```
