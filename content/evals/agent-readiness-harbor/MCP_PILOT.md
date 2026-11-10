# Guide MCP pilot — 10 November 2026

The `native+mcp` arm exposes `https://guide.wagtail.org/mcp` alongside each harness's native tools. Harbor handles server registration through its existing `AgentConfig.mcp_servers` field; the server name is `wagtail-guide` and the transport is explicitly `streamable-http`. The original user question and grading rules are unchanged, with no added request to use MCP and no new agent adapter.

The pilot uses three unchanged cases, one repeat each:

| Case                       | Framing           | Purpose                                                         |
| -------------------------- | ----------------- | --------------------------------------------------------------- |
| `info-schedule-page`       | Site named        | Find scheduling instructions and cite the guide.                |
| `troubleshoot-locked-page` | Site not named    | Find locked-page information and cite official documentation.   |
| `start-content-checker`    | Start at the site | Discover what the content checker tests and which tool it uses. |

Execution order is Kimi K3.1 Pro, Kimi K3, the other six OpenCode models (DeepSeek, GLM Flash, MiMo, GLM, Qwen, Gemma), the four Claude models, the four Codex models, then Cursor Grok. This is **17 model/harness pairs × 3 cases = 51 candidate trials**, plus the original Promptfoo grading. Vibe is outside this batch. This is an integration and tool-adoption pilot, not a full-suite accuracy comparison or a paired causal test of MCP's effect.

OpenCode is pinned to 1.19.5, Claude Code to 2.1.318 and Codex to 0.166.0, matching the earlier benchmark. Harbor installs the current Cursor CLI and records its actual version. The preview is configured separately in [matrix-kimi-preview.yaml](matrix-kimi-preview.yaml), so it does not change the main benchmark matrix. Its unlisted-model opt-in permits preparation without a catalog entry; candidate pricing remains unknown when absent. Listed Neuralwatt prices are snapshotted during preparation.

The pilot retains the existing search configuration, including OpenCode's Exa search route. It does not include the separate proposed search-access fix or HTTP proxy instrumentation. Tool availability is not the same as tool use: inspect recorded MCP calls and observations, and distinguish direct calls from opaque scripted intent in Codex.

The public server also supplies its own initialization instructions: it describes the guide's audience, asks clients to search with `search_docs`, read pages with `fetch_docs_page`, cite their URLs, and route developer questions to the developer documentation. Thus this arm measures the supplied MCP integration, including its instructions and tool descriptions; it does not isolate tool availability from that extra context. The initialization response and tool schemas are saved in `mcp-server-2026-11-10.json` in the cache root.

## Run

```sh
# First model: unlisted preview, three cases, one repeat.
just eval-agents-harbor prepare ~/.cache/guide-agent-eval/harbor/mcp-preview \
  --matrix content/evals/agent-readiness-harbor/matrix-kimi-preview.yaml \
  --arms native+mcp \
  --case info-schedule-page,troubleshoot-locked-page,start-content-checker \
  --repeat 1 --concurrency 3

just eval-agents-harbor run ~/.cache/guide-agent-eval/harbor/mcp-preview
just eval-agents-harbor grade ~/.cache/guide-agent-eval/harbor/mcp-preview
just eval-agents-harbor report ~/.cache/guide-agent-eval/harbor/mcp-preview

# A standard model uses the same arm and existing main matrix.
just eval-agents-harbor prepare ~/.cache/guide-agent-eval/harbor/mcp-kimi \
  --entry opencode-kimi --arms native+mcp \
  --case info-schedule-page,troubleshoot-locked-page,start-content-checker \
  --repeat 1 --concurrency 3
```

The example standard-model command resolves the current CLI version. To reproduce this pilot's pins and order, use the saved ordered matrix below. Preparation is free; `run` and `grade` call the candidate and judge respectively. Credentials follow the existing file/environment precedence. The launched services remove inherited `NEURALWATT_API_KEY` so the selected file key is used; Kimi and Gemma retain the previously verified GLM fallback key.

## Artifacts and verification

Artifacts remain under `~/.cache/guide-agent-eval/harbor/`:

- `mcp-pilot-2026-11-10-preview/`: first three trials, grades and comparison CSV.
- `mcp-pilot-2026-11-10-rest/`: remaining 48 trials, grades and comparison CSV.
- `mcp-pilot-matrix-2026-11-10.json`: ordered standard-model entries and CLI pins.

The preview service is `agent-readiness-mcp-preview-20261110b`; the remaining queue is `agent-readiness-mcp-rest-20261110b`. Each writes `run.log` in its export directory. Earlier launchers failed before candidate execution because of an incomplete executable PATH and a missing Cursor credential in the service environment. The corrected services use the current PATH, and the remaining queue inherits `CURSOR_API_KEY` from the session without embedding its value in the launch command or repository. Each export retains its original questions, source hash, MCP configuration, trajectories and costs. These pilot exports are excluded from `trace-sources.yaml` and the published 6,117-attempt benchmark.

Regression checks cover native/MCP configuration parity, registered transport and endpoint, explicit unlisted-model opt-in, unknown cost omission, unchanged selected prompts, and guide-specific relative MCP URLs. The original 33-case and grading definitions remain unchanged.

## Results

All **51 trials completed without execution or grading errors; 49/51 passed (96.1%)**. OpenCode, Claude and Cursor all used guide MCP successfully in every trial. The 12 original Codex trials had no observed guide MCP calls; successful tool discovery was not recorded in those trials.

| Model/harness         | Passes | Direct MCP use | Median agent seconds |
| --------------------- | ------ | -------------- | -------------------- |
| opencode-kimi-preview | 3/3    | 3/3            | 17.0                 |
| opencode-kimi         | 3/3    | 3/3            | 14.4                 |
| opencode-deepseek     | 3/3    | 3/3            | 9.8                  |
| opencode-glm          | 3/3    | 3/3            | 20.8                 |
| opencode-mimo         | 3/3    | 3/3            | 13.6                 |
| opencode-glm-full     | 3/3    | 3/3            | 14.7                 |
| opencode-qwen         | 3/3    | 3/3            | 26.7                 |
| opencode-gemma        | 3/3    | 3/3            | 14.5                 |
| claude-haiku          | 3/3    | 3/3            | 8.8                  |
| claude-sonnet         | 3/3    | 3/3            | 12.6                 |
| claude-opus           | 3/3    | 3/3            | 15.2                 |
| claude-fable          | 3/3    | 3/3            | 20.4                 |
| codex-sol             | 3/3    | 0/3            | 18.5                 |
| codex-luna            | 2/3    | 0/3            | 18.8                 |
| codex-terra           | 2/3    | 0/3            | 15.0                 |
| codex-astra           | 3/3    | 0/3            | 18.1                 |
| cursor-grok           | 3/3    | 3/3            | 20.0                 |

The two failures were Luna and Terra on `troubleshoot-locked-page`: both missed the required guide reports-page citation. Luna cited the legacy developer-docs editor manual. These are answer-grading failures, not execution errors.

Known candidate cost was **$2.2723 for 48/51 trials**, plus **$0.1893 for judging all 51**. Kimi K3.1 Pro candidate cost is unknown because it is absent from the live pricing catalog; it is not treated as free. [MCP_PILOT.csv](MCP_PILOT.csv) includes per-model costs, coverage, timings and MCP counts. Three questions and one repeat are insufficient for model rankings.

A separate Sol connectivity diagnostic explicitly asked it to discover and use the guide MCP tools. It successfully discovered both tools through `ALL_TOOLS`, searched, fetched the scheduling page, and returned the relevant guide citation. Returned observations confirm successful calls, not just scripted intent. This establishes that the pinned Codex/Harbor integration can expose and use the server, but does not prove discovery occurred in the original 12 trials. The diagnostic adds instructions, is ungraded and is excluded from the 51-trial table. Its candidate cost was $0.046393; artifacts are in `mcp-codex-connectivity-2026-11-10/`.

Cursor wraps calls as `mcpToolCall` with server and tool identifiers. Offline normalization now recognizes that wrapper; native logs confirm discovery status `ready` and successful search/fetch calls. The archived Promptfoo grades predate this normalization and retain their old zero MCP metric for Cursor. The CSV audit corrects MCP usage without rejudging answers or changing pass/fail outcomes.

The aggregate audit and per-trial records are saved as `mcp-pilot-audit-2026-11-10.json`. This pilot and the connectivity diagnostic remain separate from the original benchmark and its retries.
