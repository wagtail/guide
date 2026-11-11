# Tavily search reruns and Fable 5.2 queue

The 10 November 2026 follow-up keeps the original questions and grading, and preserves earlier results. The [guide MCP pilot](MCP_PILOT.md) finished first. Search reruns follow, then the new Claude release.

## Tavily search configuration

OpenCode 1.19.5 supports Exa and Parallel as built-in search providers. The current [Tavily provider setting](https://opencode.ai/docs/websearch/) belongs to OpenCode v2, which uses a [different CLI package](https://opencode.ai/docs/). Harbor 0.25.0 installs `opencode-ai`, the v1 package. This experiment retains the original 1.19.5 pin and uses [Tavily's official remote MCP server](https://github.com/tavily-ai/tavily-mcp) through native OpenCode configuration. No new agent adapter, search implementation or CLI patch is used.

An OpenCode matrix entry opts in with:

```yaml
search_provider: tavily
credentials:
  NEURALWATT_API_KEY: [neuralwatt_keys, glm-5.3-flash]
  TAVILY_API_KEY: [TAVILY_API_KEY]
```

The runner disables the old `websearch` tool, enables `tavily_tavily_search`, and disables Tavily extract, map, crawl and research. Existing `webfetch` remains available. Native arms keep their other native tools; web-only arms retain their deny-by-default permissions. No guide MCP server is added to these search reruns.

The Tavily key comes from the environment, then `--keys`, then a literal `TAVILY_API_KEY=...` or `export TAVILY_API_KEY=...` assignment in `~/.extra`. The file is parsed without executing shell code. Generated configs contain `Bearer {env:TAVILY_API_KEY}`, never the secret value or a credential-bearing URL. Harbor drops top-level remote MCP headers for OpenCode, so the authenticated server is configured through its supported `opencode_config.mcp` field.

This is a **search intervention**, not an identical retry: tool name, schema, descriptions, results, provider and potentially ranking all change. Site state and execution date also differ. Token-price snapshots and CLI versions are retained from the original exports. Search credits are not included in Harbor's candidate-token cost; their dollar cost remains unmeasured.

The replay layer translates Tavily search for the existing trace metrics and also records MCP use. Raw tool identities are retained. Offline trace extraction classifies the call as MCP search. Original case definitions, answer assertions and judge rubrics are unchanged.

## Selection

Selection scans the original benchmark's OpenCode `agent/opencode.txt` files for `tool_use` events whose `websearch` state is `error` and contains HTTP 429 or a rate-limit message. Calls are deduplicated by call ID. This found **989 affected attempts: 803 initial attempts and 186 retries**. Mapping retries back to their original trial produces **862 distinct slots**. Each is scheduled once, including slots whose answers passed despite the tool error. Selection does not depend on answer correctness.

| OpenCode model      | Native slots | Web-only slots |
| ------------------- | -----------: | -------------: |
| DeepSeek V4.1 Flash |            4 |              3 |
| Gemma 4 31B         |           80 |             17 |
| GLM 5.3 Flash       |           46 |             86 |
| GLM 5.3             |           81 |             90 |
| Kimi K3             |           13 |             87 |
| MiMo v2.6 Pro       |           86 |             93 |
| Qwen 3.8 27B        |           84 |             92 |
| **Total**           |      **394** |        **468** |

The integration pilot ran GLM Flash on `info-schedule-page` once in each arm: **2/2 passed**, with no execution or grading errors. Both native logs show successful Tavily searches and no Exa search calls. The native trial also encountered one ordinary page-fetch 404; this is unrelated to search authentication or rate limits. Agent time was 34.7 seconds native and 23.2 seconds web-only; known candidate-token cost totaled $0.00718, excluding search credits. Pilot answers are graded separately and excluded from the 862 slots.

Exports remain under `~/.cache/guide-agent-eval/harbor/`:

- `tavily-pilot-2026-11-10/`: two pilot trials, native logs and grades.
- `tavily-reruns-2026-11-10/plan.json`: 14 jobs and planned counts.
- `tavily-reruns-2026-11-10/selection.json`: affected attempt provenance.
- Each child export's `manifest.json` maps unique Harbor task sources to exact original result paths through `retry_sources`. Repeated case records deliberately represent separate original repeat slots.
- `prepare-tavily-reruns-2026-11-10.py`: local one-off preparation script, using native Harbor task entries.

These exports remain outside the old combined comparison and `trace-sources.yaml`. Future analysis should compare the paired intervention results with their original slots, report both improvements and regressions, and avoid counting initial attempts and retries as independent samples.

## Claude Fable 5.2

[Anthropic lists](https://platform.claude.com/docs/en/models/fable-5-2/overview) `claude-fable-5-2`, released 9 November 2026. An authenticated model lookup confirms account availability. The new [matrix](matrix-fable-5-2.yaml) pins Claude Code 2.1.322, above the [required minimum 2.1.321](https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan). The earlier Fable 5.1 results remain intact; both model and CLI version change in this comparison.

The queue runs a four-trial control pilot, then **33 questions × 3 repeats × 4 arms = 396 candidate trials**:

- `native`: standard Claude Code tools.
- `baseline`: no usable tools.
- `web`: web search and fetch only.
- `native+mcp`: native tools plus the guide MCP server.

The pilot uses `info-schedule-page` once per arm and is excluded from the 396. The full suite includes every original question, including time-sensitive release questions whose fixed expected answer may now be stale. Those checks remain unchanged for comparability. This does not add the older Promptfoo proxy-specific arms.

```sh
just eval-agents-harbor prepare ~/.cache/guide-agent-eval/harbor/fable-5-2-new \
  --matrix content/evals/agent-readiness-harbor/matrix-fable-5-2.yaml \
  --arms native,baseline,web,native+mcp --repeat 3 --concurrency 3
```

The prepared full export is `fable-5-2-comparison-2026-11-10/`; the control pilot is `fable-5-2-pilot-2026-11-10/`.

## Execution order and status

`run-tavily-then-fable-2026-11-10.py` in the cache executes the 14 Tavily jobs, the Fable control pilot, then the Fable full comparison. Each export is run, checked, graded with the existing Promptfoo judge, and reported before advancing. Candidate concurrency is three per full job; automatic infrastructure retries remain disabled. Completion markers prevent repeating finished work. A partial export requires explicit Harbor resume rather than silently creating extra attempts.

The queue stops on missing/invalid candidate outputs, new Tavily access/rate-limit errors, unexpected Exa calls, or grading errors. Ordinary answer-check failures do not stop it. A stopped queue does not start Fable early.

On 10 November at 16:45 UTC, the queue stopped after Qwen native completed all 84 attempts with three `AgentTimeoutError` results. Two were `info-stale-pages` and one was `troubleshoot-locked-page`; their traces showed continued source-code investigation at the unchanged 300-second limit. On 11 November these three exact result paths were recorded in the cache's `reviewed-timeouts-2026-11-11.json`, accepted as failed attempts, and the queue resumed at grading. No attempts were rerun, no timeout was extended and no partial answer was salvaged. Other execution, tool-access and grading checks remain active. At recovery, 770/862 Tavily attempts had finished and all 1,313 recorded Tavily searches had succeeded; Fable had not started.

The durable user service is `agent-readiness-tavily-fable-20261110`. Live stage and stop details are recorded in `tavily-fable-queue-2026-11-10.json`; each export has `queue.log`. Scheduling is conditional on successful completion of the preceding stages, not a wall-clock estimate. Read those artifacts for current progress; planned counts are not completed results.

## Completed results — 11 November 2026

The queue completed at **14:45 UTC on 11 November**. All 862 Tavily attempts and all 396 Fable comparison trials were executed, graded and reported. The integration pilots remain separate.

### OpenCode with Tavily

**750/862 attempts passed (87.0%)**. Four Qwen attempts hit the unchanged 300-second timeout and remain failures: three native and one web-only. There were no grading errors. The user's later instruction to accept partial Qwen results after reaching the Tavily quota was applied; no failed searches or timed-out attempts were rerun and no provider was substituted. All 1,442 recorded Tavily search calls had native status `completed`; no native search error states were recorded. This is trace evidence, not a billing/quota reconciliation.

| Model/arm                 | Passed | Planned |
| ------------------------- | -----: | ------: |
| opencode-deepseek--native |      3 |       4 |
| opencode-deepseek--web    |      3 |       3 |
| opencode-gemma--native    |     48 |      80 |
| opencode-gemma--web       |      4 |      17 |
| opencode-glm--native      |     41 |      46 |
| opencode-glm--web         |     81 |      86 |
| opencode-glm-full--native |     76 |      81 |
| opencode-glm-full--web    |     85 |      90 |
| opencode-kimi--native     |     11 |      13 |
| opencode-kimi--web        |     85 |      87 |
| opencode-mimo--native     |     81 |      86 |
| opencode-mimo--web        |     89 |      93 |
| opencode-qwen--native     |     67 |      84 |
| opencode-qwen--web        |     76 |      92 |

Known candidate-token cost totaled **$20.73**, with coverage for all 862 attempts; judging cost **$3.49**. Search credits are excluded. [Tavily results CSV](TAVILY_RESULTS.csv) includes model/arm timing, costs, errors and uncertain judge decisions. This selected subset is not comparable to the original whole-suite rate without pairing the affected slots.

### Claude Fable 5.2

**321/396 passed (81.1%)**, with no execution or grading errors. Every arm contains all 33 original cases and three repeats. One baseline judgment was `UNKNOWN`, which remains passing under the original rules. The four-trial control pilot passed 3/4, with only the baseline answer failing; it is excluded below.

| Arm        | Passed | Success | Median agent time | Candidate-token cost |
| ---------- | -----: | ------: | ----------------: | -------------------: |
| native     |  96/99 |   97.0% |            33.3 s |               $24.42 |
| baseline   |  34/99 |   34.3% |            13.0 s |                $4.82 |
| web        |  96/99 |   97.0% |            32.7 s |               $22.62 |
| native+mcp |  95/99 |   96.0% |            12.5 s |               $13.55 |

Trace checks found guide MCP calls in 87/99 native+MCP trials. The baseline contained no tool calls, and web-only calls were limited to `WebSearch` and `WebFetch`.

The native+MCP arm had a similar observed pass rate to the other tool-enabled arms and lower median time and candidate-token cost. This does not establish statistical equivalence or isolate MCP availability from its supplied descriptions/instructions. These trials use the live site and fixed original release expectations.

Known candidate-token cost totaled **$65.40**, plus **$1.81** for judging, excluding the pilot. [Fable 5.2 results CSV](FABLE_5_2_RESULTS.csv) provides full accounting and setup timings. Agent timing excludes container/CLI installation; the median setup time was approximately 91–99 seconds per arm.
