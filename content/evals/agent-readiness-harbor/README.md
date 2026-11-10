# Agent readiness with Harbor

Run the [existing agent readiness cases](../agent-readiness/README.md) through Harbor's installed agents. Harbor handles containers, CLI installation, execution, timeouts, repetitions, trajectories, token accounting and its log viewer. We keep Promptfoo **only for grading saved answers**, so the assertions, Sonnet 5.5 judge, rubric prompt and `UNKNOWN:` behavior stay the same. There is no second implementation of the grading rules or agent loops.

The [completed full results](RESULTS.md) cover all 4,356 trials across 17 model/harness pairs, with [per-arm data](RESULTS.csv) for success, speed, cost and errors. The [Claude comparison](CLAUDE_COMPARISON.md) compares its 1,188 answers with the published Promptfoo results. The [paid pilots](PILOT.md) document integration checks, credential selection and unsupported or invalid tool controls.

The [combined comparison](COMBINED.md) and [combined CSV](COMBINED.csv) include one retry for every original failure: 2,757/4,356 trials pass with that second chance, versus 2,595/4,356 initially. Every arm retains 99 scored trials, and cumulative time and cost include both attempts when retried. The [follow-up notes](RETRIES.md) document all 1,761 completed retries and the separate Kimi K3.1 Pro preview check.

The [trace-analysis pipeline](TRACE_ANALYSIS.md) combines offline technique counts for all 6,117 attempts with Harbor's native rubric review. The [trace findings](TRACE_RESULTS.md) compare navigation, workspace inspection and explicit instructions, keeping retries and visibility limitations separate.

The [guide MCP pilot](MCP_PILOT.md) adds a `native+mcp` arm through Harbor's built-in server configuration, starting with the Kimi K3.1 Pro preview. It is separate from the completed benchmark and its retries.

The [Tavily follow-up](SEARCH_RERUNS.md) replaces rate-limited OpenCode search through native MCP configuration, with 862 affected slots scheduled once each. Claude Fable 5.2 follows with 396 trials across all four supported Claude arms. These are separate interventions, preserving the original results.

## What the 33 questions test

These are documentation-answering tasks from [the original cases](../agent-readiness/tests.yaml), not tasks that modify a CMS or codebase. Each run asks one question and expects an answer with official citations.

| Type                      | Count | Coverage                                                                                                                                                                                                  |
| ------------------------- | ----: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Information               |    15 | Scheduling, finding pages, snippets, aliases, privacy, image cropping, redirects, roles, aging pages, shortcuts, multi-site, the guide’s audience, browser support, content checks and image collections. |
| Troubleshooting           |     8 | Unpublished changes, missed schedules, deleted documents, missing Publish buttons, concurrent editing, image upload limits, locked pages and inactive accounts.                                           |
| Releases                  |     6 | Wagtail 8.0 images and API, incomplete block drafts, autosave, a multi-release upgrade summary and the latest release.                                                                                    |
| Developer routing         |     3 | Custom StreamField blocks, notification-email domains and adding page fields. The answer should use developer documentation.                                                                              |
| Guide-to-developer bridge |     1 | Configuring the server’s scheduled-publishing command, following the guide’s link to developer documentation.                                                                                             |

The framing varies: 19 prompts name the guide, 9 ask for official documentation without naming it, and 5 tell the agent to start at the site and discover an answer. These are different views of the same 33 cases, not extra cases.

Each answer gets deterministic fact/citation checks, a Sonnet 5.5 rubric judgment and shared checks against empty answers and obsolete guide links. The reference answer stays hidden from the candidate. Tool traces record which site features were reached without affecting the pass/fail score. As in the original eval, an uncertain judge can return a passing `UNKNOWN:` result; the report counts those separately.

The questions and expected answers are a fixed snapshot. In particular, the “latest release” case expects Wagtail 8.0; update the source eval deliberately when that becomes stale, then rerun both comparisons against the same snapshot.

## Matrix and arms

[matrix.yaml](matrix.yaml) lists 17 model/harness pairs, with model IDs checked on 5–6 November 2026:

| Harness      | Models                                                                                                    |
| ------------ | --------------------------------------------------------------------------------------------------------- |
| Claude Code  | Haiku 5.5, Sonnet 5.5, Opus 5.5, Fable 5.1                                                                |
| Codex        | GPT-6.1 Sol, GPT-6 Luna, GPT-6.1 Terra, GPT-6 Astra                                                       |
| Cursor CLI   | Grok 4.7 Medium                                                                                           |
| OpenCode     | Neuralwatt DeepSeek V4.1 Flash, GLM 5.3 Flash, MiMo v2.6 Pro, GLM 5.3, Qwen 3.8 27B, Gemma 4 31B, Kimi K3 |
| Mistral Vibe | Mistral Large 4                                                                                           |

`prepare` resolves current CLI releases once and saves their versions. Cursor is an exception: Harbor's installer always installs latest, so its actual version must be checked in each trial. Model IDs are explicit rather than moving aliases. Update the matrix deliberately when comparing newer models. Other than Cursor's explicit Medium selectors, reasoning settings use harness defaults; they are not equivalent reasoning budgets.

The four additional Neuralwatt models use OpenCode 1.19.5, matching the existing experiment. They add 1,188 full-suite trials. GLM and Qwen use matching file keys. Gemma and Kimi use the verified GLM key as an authorized fallback because their matching keys returned 401. The expansion service removes the inherited `NEURALWATT_API_KEY` so it cannot override these selections. A separate native-tool smoke test targets the account's unlisted `kimi-k3.1-pro` preview, also using the GLM fallback key. That preview is excluded from the main matrix; its candidate price is unknown. See [pilot findings](PILOT.md) for the initial inherited-key trial and credential checks.

[arms.yaml](arms.yaml) contains native Harbor kwargs:

| Arm          | Behavior                                                                                                                                                                          |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `native`     | The installed harness's default tools and system prompt, in an empty container.                                                                                                   |
| `native+mcp` | Native tools plus the public guide MCP server, for Claude Code, Codex, Cursor and OpenCode. The question is unchanged and does not instruct the agent to use MCP.                 |
| `baseline`   | No usable tools. Claude removes tools; OpenCode disables them in config; Codex disables tool features; Vibe disables tools, connectors, MCP and subagents. Cursor is unavailable. |
| `web`        | Web fetch/search only, currently for Claude Code and OpenCode.                                                                                                                    |

[tool_controls.py](tool_controls.py) supplies flags/config settings that Harbor doesn't expose as kwargs and maps Vibe 3's new JSON export into Harbor's existing trajectory converter. The installed-agent implementations still handle installation and execution. Replay rejects baseline tool calls, except Vibe's retained discovery operation when it returns zero tools and zero connector notices. Those empty discovery calls remain in the trace and timing. This is a no-usable-tools baseline, not an identical tool-free API request across harnesses. A failed control is an execution error, not an incorrect answer.

**Cursor's no-tools arm is not supported by this version.** The paid pilot found that deny-all `preToolUse` hooks still allowed server-side web search/fetch. `prepare` reports this combination as unavailable. Adding a custom agent loop or proxy to force it would undermine the aim of using the native harness with minimal glue. See [pilot findings](PILOT.md).

**Codex web-only remains unvalidated with CLI 0.166.0.** The follow-up pilot enabled live search while disabling non-web tools, but the models attempted browsing through `exec`, which returned `code-mode host is disabled`. Enabling the native standalone-search flag did not resolve this for Sol. Replay rejects these attempts as invalid web-only controls. See the [follow-up investigation](RETRIES.md); the full matrix still has two Codex arms.

The separate `native+mcp` pilot retains Codex's native tools and code mode; it does not use those web-only restrictions. MCP servers are registered through `AgentConfig.mcp_servers` with explicit `streamable-http` transport. No new agent adapter is needed.

**OpenClaw is deferred.** A DeepSeek smoke test for the proposed Neuralwatt pairs used Harbor upstream revision `539c1175b3276ef3e8a8c47fd95db5562147e970`. Its adapter failed before inference because `openclaw.upload.json` was written on the host but unavailable inside Docker. No custom adapter or patch was added, and the released Harbor pin and existing matrix were retained. The diagnostic artifacts are under `~/.cache/guide-agent-eval/harbor/openclaw-pilot-2026-11-05/`.

This experiment uses the **live site**. It does not reproduce the old `web-plain` proxy experiment or collect HTTP Accept headers. Native server-side search/fetch may bypass a local proxy. Use the original runner for the controlled site-feature ablation; don't pool its arms with these native-tool results.

## Run

Requires Docker, Node, `just`, `uv`, and credentials. The separate Python environment pins Harbor 0.25.0 and doesn't add it to the Django application's dependencies.

```sh
just eval-agents-init
just eval-agents-harbor doctor

# Export one question for a small pilot: no model calls during prepare.
just eval-agents-harbor prepare ~/.cache/guide-agent-eval/harbor/pilot \
  --entry opencode-deepseek --case info-schedule-page \
  --arms native,baseline,web --repeat 1 --timeout 90

# These steps call the candidate models, then the judge respectively.
just eval-agents-harbor run ~/.cache/guide-agent-eval/harbor/pilot
just eval-agents-harbor grade ~/.cache/guide-agent-eval/harbor/pilot
just eval-agents-harbor report ~/.cache/guide-agent-eval/harbor/pilot

# Review trajectories with Harbor's own viewer.
just eval-agents-harbor-cli view ~/.cache/guide-agent-eval/harbor/pilot/jobs
just eval-agents-view
```

Credentials come from environment variables first, then `~/dev/.keys.yml` (override with `--keys`). Neuralwatt uses the key for the selected model under `neuralwatt_keys`. Each job receives only its provider's key. Cursor uses `CURSOR_API_KEY`. Generated configs contain environment references, never literal credentials. The judge uses `ANTHROPIC_API_KEY` from the same source. Generated tasks contain only the question and a minimal Dockerfile; reference answers and grading files stay on the host.

Use a new experiment directory for each run. `run --job 'claude-*'` selects jobs from an existing export. For interrupted jobs, use Harbor's native commands (`just eval-agents-harbor-cli job --help`) rather than overwriting completed trials. Grading saved outputs does not rerun candidates, but does call the judge again.

To prepare all models, all supported arms, and three repeats:

```sh
just eval-agents-harbor prepare ~/.cache/guide-agent-eval/harbor/comparison \
  --arms native,baseline,web --repeat 3
```

That is **44 jobs × 33 questions × 3 repeats = 4,356 candidate runs**, plus judging. Preparation is free. Start with a pilot before launching this matrix. Default concurrency is one per job, with a 300-second agent timeout and no infrastructure retries. There is no aggregate dollar cap. Unsupported arm/harness combinations are listed explicitly. The export records a source hash; grading refuses to proceed if cases or graders have changed.

## Reading the results

`comparison.csv` joins Promptfoo's grades to Harbor's trial results:

- Success rate uses all planned trials as the denominator; finished/graded counts expose incomplete jobs. Inspect execution and grading errors before comparing rates.
- Agent latency comes from Harbor's `agent_execution`, including the harness's own API retries, but excluding installation and grading. Setup time is a separate column. Promptfoo's replay latency is **not** agent latency.
- Costs are Harbor's reported or estimated API costs, with coverage counts. Missing costs remain blank, not zero. Cost per success is only calculated when cost coverage is complete. Judge usage costs are reported separately.
- Neuralwatt prices are snapshotted from its public model catalog into OpenCode's config. These are **token-price estimates**, not invoices or measured energy charges. Vibe uses the explicit Mistral token prices in `matrix.yaml` (promotional rates checked on 5 November 2026); update these when the promotion ends. Cursor rates use Harbor's `pricing` override with published standard-context, non-Fast list prices; these exclude plan credits, Teams surcharges and regional uplifts. The original pilot omitted that override, so its recorded cost remains unknown; the pilot notes include a retrospective estimate. Search fees, subscriptions and different billing tiers can make actual charges differ.
- The original trace grader is reused. Common tool names are translated; opaque Codex code-mode calls are counted separately because ATIF does not always expose their nested actions. Trace reach rates can therefore be incomplete; consult native transcripts.
- `UNKNOWN:` judgments remain passing, as before, and are counted for manual review. A one-question pilot validates integration, not model quality.

Harbor verification is disabled because grading is performed afterward on the host. Its initial displayed mean of zero is **not** the benchmark score. Use `comparison.csv` or Promptfoo's saved grades for success rates, and Harbor for trajectories. This keeps answers and rubrics out of candidate containers and preserves the original judge exactly.

The chosen pairs compare **model plus harness**. They do not isolate the harness's effect from the model's effect. For that, add overlapping model/harness pairs and keep case selection, repeats, reasoning settings, concurrency and site state matched.

## Verification

```sh
just eval-agents-harbor-test
just eval-agents-check
just lint
```

The adapter tests check Harbor option compatibility, key selection, answer extraction, baseline contamination, Vibe export conversion, incomplete cost coverage and failed-run handling. Paid pilot transcripts are stored outside the repository.

## Upstream references

- [Harbor's installed agents](https://docs.harborframework.com/agents/pre-integrated-agents) and [job configuration](https://docs.harborframework.com/jobs/configs).
- [Claude model IDs](https://platform.claude.com/docs/en/models/overview) and [OpenAI model IDs](https://developers.openai.com/api/docs/models).
- [Cursor CLI parameters](https://cursor.com/docs/cli/reference/parameters), [model prices](https://cursor.com/docs/models-and-pricing) and [tool-denial hooks](https://cursor.com/docs/hooks).
- [Vibe tool filters](https://docs.mistral.ai/vibe/code/safety-approvals-permissions) and [Mistral Large 4](https://docs.mistral.ai/models/mistral-large).
- [Neuralwatt API and billing](https://neuralwatt.com/faq).

Inspect AI's [Agent Bridge](https://inspect.aisi.org.uk/agent-bridge.html) is another option, but routing model calls through a bridge changes more of the experiment. Harbor already supplies all five requested agent integrations, which keeps this version mostly configuration and avoids another implementation of the agents.
