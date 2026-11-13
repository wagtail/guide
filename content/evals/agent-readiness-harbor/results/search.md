# Tavily search results

All 862 selected attempts completed and were graded; 750 passed. Four Qwen timeouts remain failures. See [all-model results](README.md) for Fable 5.2.

## Results

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

Known candidate-token cost totaled **$20.73**, with coverage for all 862 attempts; judging cost **$3.49**. Search credits are excluded. [Tavily results CSV](search.csv) includes model/arm timing, costs, errors and uncertain judge decisions. This selected subset is not comparable to the original whole-suite rate without pairing the affected slots.

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
