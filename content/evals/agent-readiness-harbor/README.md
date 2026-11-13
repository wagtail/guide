# Agent readiness with Harbor

Run the [existing 33 agent-readiness questions](../agent-readiness/README.md)
through Harbor's installed agents, then grade saved answers with the original
Promptfoo assertions and rubric. Harbor supplies containers, agent installation,
execution, trajectories and accounting; no custom agent loops are added.

## Read the results

- [Benchmark results](results/README.md): success, speed and cost for all 18
  full-suite model/harness pairs, including Fable 5.2; [48 result rows](results/benchmark.csv).
- [Retries](results/retries.md): one retry per original failure, with cumulative
  time and cost. [Tavily search](results/search.md) and [MCP pilots](results/mcp-pilot.md)
  retain their own denominators.
- [Trace findings](analysis/README.md): retrieval techniques, instruction effects,
  citation support and useful automated-review highlights. [Raw statistics](analysis/statistics.md)
  and [retrieval measurements](analysis/retrieval.md) include counts, rates and unknowns.
- [Energy results](results/energy.md): illustrative Neuralwatt medians and totals.
- [Claude versus Promptfoo](results/claude-comparison.md): the historical comparison.

## Folder guide

| Folder         | Contents                                                                    |
| -------------- | --------------------------------------------------------------------------- |
| `results/`     | Final benchmark and follow-up results, including energy.                    |
| `analysis/`    | Trace findings, research context and numeric tables in `data/`.             |
| `config/`      | One model matrix, tool arms, trace sources and native-review configuration. |
| `scripts/`     | Harbor orchestration, answer replay and trace analysis.                     |
| `tests/`       | Offline regression tests.                                                   |
| `methodology/` | Control validation, grading notes and analysis reproduction.                |

Raw runs remain under `~/.cache/guide-agent-eval/harbor/`; they are not committed.

## Models and tool arms

The single [matrix](config/matrix.yaml) contains 18 full-suite model/harness
pairs and the opt-in Kimi preview used in pilots. Model IDs and recorded CLI
versions are explicit; update them deliberately for new experiments.

| Harness      | Models                                                                                                                |
| ------------ | --------------------------------------------------------------------------------------------------------------------- |
| Claude Code  | Haiku 5.5, Sonnet 5.5, Opus 5.5, Fable 5.1 and 5.2                                                                    |
| Codex        | GPT-6.1 Sol, GPT-6 Luna, GPT-6.1 Terra, GPT-6 Astra                                                                   |
| Cursor       | Grok 4.7 Medium                                                                                                       |
| OpenCode     | DeepSeek V4.1 Flash, GLM 5.3 Flash, MiMo v2.6 Pro, GLM 5.3, Qwen 3.8 27B, Gemma 4 31B, Kimi K3; Kimi K3.1 Pro preview |
| Mistral Vibe | Mistral Large 4                                                                                                       |

[Tool arms](config/arms.yaml) are `native`, `baseline` (no usable tools), `web`
(search/fetch only), and `native+mcp` (native tools plus the guide MCP server).
Cursor supports only native and MCP. Codex web-only failed validation; it is
excluded. Vibe supports native and baseline. OpenClaw is deferred because the
upstream adapter failed before inference. See [pilot findings](methodology/pilots.md),
[MCP validation](results/mcp-pilot.md) and [retry/control investigations](methodology/retries.md).

Baseline replay rejects attempted tool use, including blocked attempts. Vibe's
empty discovery operation is allowed only when it exposes no usable tools.
[Compatibility wrappers](scripts/tool_controls.py) apply native CLI controls and
normalize Vibe exports; Harbor still implements agent execution.

## Questions and grading

The cases cover 15 information questions, eight troubleshooting questions, six
release questions, three developer-routing questions and one guide-to-developer
bridge. Nineteen name the guide, nine ask for official documentation, and five
ask the agent to start at the site. These are different questions, not randomized
wording variants. Each arm runs all 33 questions three times.

Candidates see only the question. Promptfoo reuses deterministic checks and the
Sonnet 5.5 rubric judge; passing `UNKNOWN:` judgments retain the original behavior.
Historical grades are unchanged. [Future grading fixes](methodology/grading.md)
address the stale latest-release expectation and overly literal multi-tenancy
wording. Source hashes prevent accidentally mixing grading revisions.

## Run

Requires Docker, Node, `just`, `uv` and provider credentials. Harbor 0.25.0 is
pinned in a separate environment. Credentials come from environment variables,
then `~/dev/.keys.yml` (override with `--keys`); only the selected provider's key
is passed to each job. Generated configs use environment references.

```sh
just eval-agents-init
just eval-agents-harbor doctor

# Preparation makes no model calls. Start with one case.
just eval-agents-harbor prepare ~/.cache/guide-agent-eval/harbor/pilot \
  --entry opencode-deepseek --case info-schedule-page \
  --arms native,baseline,web --repeat 1 --timeout 90

# Candidate execution, then paid grading of saved answers.
just eval-agents-harbor run ~/.cache/guide-agent-eval/harbor/pilot
just eval-agents-harbor grade ~/.cache/guide-agent-eval/harbor/pilot
just eval-agents-harbor report ~/.cache/guide-agent-eval/harbor/pilot
just eval-agents-harbor-cli view ~/.cache/guide-agent-eval/harbor/pilot/jobs
```

Use `--entry claude-fable-5-2` or `--entry opencode-kimi-preview` to select those
entries from the same matrix. The preview has `default: false`: an unfiltered
preparation excludes it. All default entries with `--arms native,baseline,web
--repeat 3` produce 47 jobs × 99 = **4,653 candidate runs**, plus judging.
Adding MCP changes that count. Unsupported combinations are reported explicitly.
Use a fresh export directory; resume interrupted jobs through Harbor's native
commands. There is no aggregate spending cap.

## Accounting and interpretation

Success denominators include failed attempts. Agent time excludes installation
and grading; setup is recorded separately. Costs are reported or token-price
estimates with explicit coverage, not invoices; missing costs stay unknown.
Search fees and subscriptions are excluded. Retry comparisons include both
attempts' time and cost. Original runs, retries and interventions retain their
identities in the data.

The live-site benchmark compares model plus harness, with different reasoning
defaults and tool visibility. It does not isolate harness effects or reproduce
the old proxy/site-feature ablation. No HTTP headers were captured. Opaque nested
tools can limit trace counts. MCP configuration tests assisted access, not
organic endpoint discovery. See [analysis methodology](methodology/trace-analysis.md).

## Verify

```sh
just eval-agents-harbor-test
just eval-agents-check
just lint
```
