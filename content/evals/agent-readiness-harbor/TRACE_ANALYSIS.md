# Analyze execution techniques

The [retrieval and citation analysis](TRACE_RETRIEVAL.md) adds full-inventory
friction counts, citation provenance and checked claim examples. The
[full Jevotron review](TRACE_JEV_RESULTS.md) assesses all 7,432 attempts with
explicit uncertainty and critical checks of its flags. Raw CSVs preserve unknowns
and do not label all repeated or uncited retrieval as waste.
[Neuralwatt energy results](ENERGY_ANALYSIS.md) add illustrative task medians
and batch means; [published prompt-improvement trials](PROMPT_IMPROVEMENT.md)
test GEPA and TextGrad templates without changing benchmark instructions.

This pipeline extracts deterministic measures from saved executions and optionally uses **Harbor's native `analyze` command** with a technique rubric for semantic review. It adds no agent adapters and does not rerun candidates or change Promptfoo grades. The [trace results](TRACE_RESULTS.md) cover 7,432 graded attempts: 4,356 initial attempts, 1,761 retries, 862 Tavily interventions, 396 Fable 5.2 runs and 57 pilots. Cohorts remain separate. [Interpreted findings](TRACE_FINDINGS.md), [per-arm data](TRACE_BY_ARM.csv), [question-framing data](TRACE_BY_FRAMING.csv) and the [external-method review](TRACE_RESEARCH.md) share these definitions.

It extends the [previous Promptfoo analysis](../agent-readiness/RESULTS.md): search versus site navigation, agent-readiness files, local workspace inspection, retrieval errors, and the relationship to explicit instructions. The original URL surface classifier is reused. New measures describe requests and visible sequences; they do not inherit the old classifier's assumption that a requested URL was successfully reached.

## First findings

The original-benchmark findings below use initial attempts for cross-model comparisons; the completed intervention and pilot cohorts have separate tables in the latest report. It supports several follow-up questions:

- **Explicit site-start wording accompanies a different browsing pattern.** Claude opened the homepage first in 29/60 native site-start traces, versus 10/228 site-named traces. OpenCode did so in 55/105 versus 3/399. Because the questions differ, this is an association with framing, not an estimated instruction effect.
- **Coding tools influence the visible approach.** Cursor inspected the workspace in 30/99 native traces, OpenCode Qwen in 42/99 and GLM 5.3 in 38/99. These are documentation-answering tasks; a local search is not automatically useful or inappropriate. Inspect its actual target and the question.
- **Web-only arms show more search requests.** Claude has 309 web-arm attempts with search requests versus 237 native; OpenCode has 614 versus 578. Each arm has the same questions and repeat count (396 for Claude, 693 for OpenCode). This is descriptive evidence of a strategy difference under restrictions, not proof of an accuracy benefit.
- **Agent-readiness files remain uncommon direct targets.** The extractor recorded OpenCode native `llms.txt` requests for GLM 5.3, GLM 5.3 Flash, MiMo and Qwen, in 3, 2, 5 and 3 traces respectively out of 99 each. Codex's opaque wrappers prevent an equivalent absence claim.

Two diagnostic reviews illustrate what the semantic stage adds. Their event references were manually checked against the extracted evidence:

- **MiMo pursued source-code inspection after retrieval failures.** In `71e9a33583f786ff`, the question asks how to recover a deleted PDF and to “Link to official documentation.” Failed searches at `s2:0` and `s2:1` precede direct fetches. The docs homepage at `s5:0` supplies links fetched at `s6:0` and `s6:1`. Later the agent requests PyPI metadata (`s21:0`), downloads and extracts a Wagtail wheel (`s22:0`), and greps the extracted source (`s23:0`–`s24:1`). This shows escalation from documentation retrieval to source inspection. It does not establish that hidden system instructions caused it or that the inspection improved the answer.
- **Mistral Vibe followed search results without using an agent index.** In `032f383034dc553d`, the instruction says “Check guide.wagtail.org and link to the page you used.” Searches at `s5:0` and `s8:0` precede fetching the manage-pages URL at `s11:0` and `s12:0`; that URL is visible in the earlier search output. `llms-full.txt` appears in search output but is never requested. This distinction would be lost by counting every mentioned URL as a visit.

Prefix each abbreviated step above with the trace ID and a colon to find the full event ID in `events.jsonl`. These examples come from a deliberately enriched diagnostic sample and do not establish technique prevalence. The native reviewer sometimes abbreviates citations and overstates details (for example, describing a curl wheel download as a pip download); inspect the evidence and citation flags before relying on its prose.

## Diagnostic pilot

On 8 November 2026, **12/12 selected traces received schema-valid native Harbor analyses**, covering all 11 harness/arm combinations plus one additional diagnostic example. The first job, `20261108T151100Z`, completed eight reviews and had four infrastructure failures: three missing verifier directories and one setup timeout. Job `20261108T153434Z` successfully retried those four with the log-directory workaround and longer setup timeout.

Reported agent cost across both jobs was **$0.07863**. Cost was recorded for 15 of 16 analysis attempts; the remaining attempt failed during setup before the agent ran. This is reviewer cost, separate from candidate execution and Promptfoo judging. The pilot validated orchestration and exposed citation/detail errors requiring manual review; it does not validate every semantic judgment. The native Harbor reviewer remains a diagnostic pilot. The separate [Jevotron review](TRACE_JEV_RESULTS.md) now covers all 7,432 attempts; deterministic counts and bounded inspection of original evidence remain necessary to assess its flags.

Both native reports and staged inputs remain under the local output directory described below. They preserve the earlier extraction snapshots used by the pilot; subsequent extraction refinements distinguish normalized-page matches and expose implementation names more explicitly. The published aggregate snapshot uses the final extractor.

## Run the pipeline

The first stage is offline and free. It reads the exports listed in [trace-sources.yaml](trace-sources.yaml), including the retry and Tavily plans. Completed guide MCP, Tavily and Fable pilots use their own phases; they never enter original benchmark rates. The ungraded Codex connectivity diagnostic is documented separately in MCP_PILOT.md. Older setup/debugging exports such as OpenClaw remain outside this graded inventory.

```sh
just eval-agents-traces --output ~/.cache/guide-agent-eval/harbor/trace-analysis-followups-2026-11-11

# Inspect exactly what a model reviewer would receive, without calling it.
just eval-agents-trace-review ~/.cache/guide-agent-eval/harbor/trace-analysis-followups-2026-11-11 --stage-only --limit 16

# Paid diagnostic review: native Claude Code / Haiku, three concurrent containers.
just eval-agents-trace-review ~/.cache/guide-agent-eval/harbor/trace-analysis-followups-2026-11-11 --limit 16

# Optional paid review of every saved attempt; this creates 7,432 analysis tasks.
just eval-agents-trace-review ~/.cache/guide-agent-eval/harbor/trace-analysis-followups-2026-11-11 --all

# Retry only missing/failed analyses from one native analysis report.
just eval-agents-trace-review --resume-report \
  ~/.cache/guide-agent-eval/harbor/trace-analysis/analysis-jobs/RUN_ID/analysis.json
```

The default output directory is `~/.cache/guide-agent-eval/harbor/trace-analysis/`. Override extraction with `--output DIRECTORY --config SOURCES.yaml`; pass the same directory as the first positional argument to `eval-agents-trace-review`. Source exports and saved trial paths must remain accessible. IDs are derived from absolute trial paths, so moving an archive changes its IDs.

The original 12-trace pilot covered the original harness/arm combinations. The expanded inventory has 15 combinations; use a limit of at least 15 for coverage. The example requests 16, then fills remaining slots with traces rich in recorded techniques. The selector prioritizes harness/arm coverage, not every phase; inspect selection.json before a paid review. It is a **diagnostic sample**, not a prevalence estimate. `selection.json` records the exact IDs. Full review is optional: deterministic counts already cover the entire benchmark. The reviewer has a $0.30 per-analysis budget setting, 20 turns and a five-minute execution timeout; this is not an aggregate billing cap. Reviewer cost is separate from benchmark cost.

## Evidence and outputs

The offline extractor reads Harbor ATIF trajectories, grades, manifests and recorded controls. OpenCode's native JSON event log supplies error states missing from ATIF. It never opens the native session database. The output includes:

- `report.md`, `by-arm.csv`, `by-framing.csv`, `by-case.csv`: technique counts/rates, coverage and unchanged outcomes, with every cohort separate.
- `pattern-statistics.csv` and `pattern-definitions.csv`: all 47 patterns with present, not-observed, unknown and eligible counts, rates and percentages. Answer-citation rates use replayed-answer coverage; other pattern rates use trajectory coverage.
- `tool-call-statistics.csv` and `per-trace-statistics.csv`: total/mean/median/nearest-rank p90/max calls, zeros and missing coverage, plus each trace’s counts and binary pattern flags. OpenCode totals deduplicate native/ATIF call IDs; two native-only calls are counted without inventing their step order.
- `tavily-pairs.csv`: exact affected slots, initial and previous outcomes, improvements and regressions; no outcome-selected pooling.
- `data-coverage.csv`: local raw-artifact presence, answer/system/timing/cost coverage by phase and harness.
- `trials.jsonl`: one row per attempt with its exact prompt, framing, tool arm, instruction fingerprint, grade, time and candidate cost.
- `events.jsonl`: stable event IDs, step groups, tool names, target surfaces, query excerpts, status and visible URL provenance. Raw tool response bodies are omitted.
- `instructions.jsonl`: full recorded system text and controls, retained locally. Fingerprints describe recorded evidence, not equivalence of hidden harness instructions.
- `retry-pairs.jsonl`: exact original/retry links, recovery status and added/removed observed techniques. The 30 pairs missing a trajectory have null transitions, not inferred strategy changes.
- `within-case-associations.csv`: comparisons within the same model, arm and question, using the initial repeats only. Each eligible question contributes equally; these are exploratory associations, not causal estimates.

Native `harbor analyze` receives only staged `context.json` and `events.jsonl`, with bounded excerpts, credential-like strings redacted and URL credentials/query strings/fragments removed. System excerpts select lines about tools, search, browsing or documentation, capped at 4,000 characters; answer excerpts are capped at 1,200. Missing or omitted evidence limits what a reviewer can conclude. Original transcripts, session databases, reference answers, credentials and original `result.json` are not copied into reviewer containers. The latter matters because Harbor follows its task-directory reference when staging analysis inputs.

The [eight-criterion rubric](trace-rubric.yaml) reviews search-led navigation, index-led navigation, URLs without visible prior sources, adaptation after retrieval errors, workspace inspection, alignment with explicit instructions, tool-restriction conflicts, and visibility limits. **Pass means the technique or condition is present**, not that an answer is good. The [review prompt](trace-prompt.txt) requires event citations and separates observed actions from inferred intent.

Harbor saves `analysis-jobs/RUN_ID/analysis.json`; the wrapper adds `findings.csv`, including flags for nonexistent event references and explanations without full event IDs. The latter also flags legitimate answer-only or visibility explanations; inspect these rather than automatically discarding them. `latest-semantic-report.json` is the latest job only. A retry's `selection.json` links its parent report; retain both reports to cover the original selection. Native schema validation and valid event IDs do not establish that every explanation is correct: inspect cited evidence before publishing qualitative conclusions.

Harbor 0.25's prebuilt analysis image needs its verifier and artifact log directories initialized. The review prompt asks the native agent to create empty marker files there using Write, before analysis. It never writes verification rewards. Setup gets a 12-minute timeout because CLI installation can be slow. The wrapper checks individual analysis errors and coverage rather than trusting the CLI exit code alone.

## How to interpret instruction effects

The 33 cases contain 19 site-named questions, nine site-not-named questions and five site-start questions. These are different tasks, not randomized versions of one prompt. Compare framing descriptively; compare tool arms within the same case; inspect the exact question and recorded controls when explaining an individual trace.

Only Codex consistently recorded system messages in these exports. For other harnesses, explanations can cite the user question and explicit tool configuration, but cannot attribute behavior to an unseen system prompt. Codex's `exec`/`js_repl` calls often hide nested operations: script text records intent, not proof that each nested call executed. The report marks those comparisons as opaque.

Configured controls are extracted from saved agent kwargs, together with the implementation name. Vibe's baseline controls live in the existing `NoToolsVibe` implementation rather than kwargs, so its controls object is empty; the arm still records the expected no-usable-tools restriction. Empty controls do not establish that a harness exposed every tool.

An error followed by another tool call establishes continuation, not necessarily a deliberate recovery strategy. A URL absent from earlier outputs might come from memory, an omitted observation or another source; it is not automatically a guess. Parallel calls in one step cannot establish link-following order. Shell parsing recognizes a conservative subset of literal commands, never executes them, and marks unresolved curl targets. A returned observation does not establish factual grounding.

URL provenance reuses normalized-page matching: query strings, fragments, guide-version prefixes and Markdown suffixes are ignored. Its `match` field distinguishes exact sanitized URLs from page-level matches. Both identify possible visible sources; neither establishes that an earlier output caused the later request. Check the original paths when discussing literal link-following.

Retries were selected because the original failed. Analyze their paired changes separately instead of pooling them into technique prevalence or treating recovery as a strategy's causal effect. The original benchmark's outcome remains authoritative.

The old Promptfoo proxy experiment measured controlled site-feature differences. These Harbor runs captured no proxy headers and have no equivalent plain-site ablation. Later native+MCP arms preconfigure a server alongside its descriptions/instructions; they do not isolate organic endpoint discovery or tool availability alone. They cannot establish HTTP content negotiation, the benefit of Markdown delivery, or a causal advantage for one harness independently of its models.

## Verification

```sh
just eval-agents-harbor-test
just eval-agents-check
just lint
```

Regression tests exercise URL sanitization and safe staging, structured/native failures, opaque scripts, conservative shell detection, parallel-call provenance, missing-versus-zero counts, answer-specific denominators and evidence-dependent retry transitions. Raw traces and paid-review artifacts remain outside the repository; the checked-in CSVs and Markdown are aggregate snapshots.

## Published snapshot

The current aggregate snapshot comes from `trace-analysis-followups-2026-11-11/`. Its report is published as [TRACE_RESULTS.md](TRACE_RESULTS.md); the corresponding by-arm, by-framing, pattern, call-distribution, per-trace, paired-intervention and data-coverage files are checked in as `TRACE_*.csv`. [TRACE_INVENTORY.json](TRACE_INVENTORY.json) records cohort/trace/event counts and the pattern list. The explanatory [TRACE_FINDINGS.md](TRACE_FINDINGS.md) and [TRACE_RESEARCH.md](TRACE_RESEARCH.md) distinguish observations from proposed checks. Raw traces remain local; the checked-in per-trace table contains IDs and numeric/categorical data, not prompts or responses.
