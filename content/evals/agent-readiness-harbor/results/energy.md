# Illustrative Neuralwatt energy results

Across 3,858 attempts, 16,123 strictly matched requests account for **3,097.048 Wh**.
Supplemental execution-window attribution adds **129.520 Wh**, for an illustrative
**3.227 kWh** total. Strict energy is available for 3,828 attempts. These are
provider-attributed inference amounts, excluding local harnesses, search and MCP.

## Initial OpenCode arms: median Wh per attempt

| Model               | No tools | Native | Web-only |
| ------------------- | -------: | -----: | -------: |
| DeepSeek V4.1 Flash |   0.0051 | 0.0445 |   0.0291 |
| Gemma 4 31B         |   0.0166 | 0.1457 |   0.0751 |
| GLM 5.3             |   0.0598 | 0.7619 |   0.6425 |
| GLM 5.3 Flash       |   0.0228 | 0.2081 |   0.1647 |
| Kimi K3             |   0.6623 | 1.5794 |   3.9117 |
| MiMo v2.6 Pro       |   0.0214 | 0.4437 |   0.4413 |
| Qwen 3.8 27B        |   0.0319 | 0.4201 |   0.2024 |

Each cell uses 99 attempts with attributed energy except GLM 5.3 no-tools
(96/99) and web-only (81/99). Failed attempts are included when energy is known;
missing amounts are excluded. These are partial task medians, not energy per
successful answer. Kimi K3.1 Pro has only three MCP pilot attempts.

## All recorded phases: illustrative totals

| Model               | Attempts / strict energy rows | Strict mean Wh | Strict median Wh | Window total Wh | Window mean Wh | Strict share of window Wh |
| ------------------- | ----------------------------- | -------------- | ---------------- | --------------- | -------------- | ------------------------- |
| deepseek-v4.1-flash | 409 / 409                     | 0.0538         | 0.0152           | 25.4242         | 0.0622         | 86.57%                    |
| gemma-4-31b         | 593 / 585                     | 0.1590         | 0.0744           | 99.2911         | 0.1674         | 93.69%                    |
| glm-5.3             | 598 / 576                     | 1.3098         | 0.3515           | 780.2683        | 1.3048         | 96.69%                    |
| glm-5.3-flash       | 542 / 542                     | 0.2941         | 0.1258           | 164.9717        | 0.3044         | 96.62%                    |
| kimi-k3             | 512 / 512                     | 2.2173         | 0.9627           | 1184.5928       | 2.3137         | 95.84%                    |
| kimi-k3.1-pro       | 3 / 3                         | 0.1204         | 0.1194           | 0.3857          | 0.1286         | 93.66%                    |
| mimo-v2.6-pro       | 588 / 588                     | 0.7489         | 0.3667           | 466.1023        | 0.7927         | 94.47%                    |
| qwen-3.8-27b        | 613 / 613                     | 0.8029         | 0.2625           | 505.5317        | 0.8247         | 97.36%                    |

Strict means and medians use attempts with matched energy. Window means divide
supplemented energy by all attempts, including failures and unknowns. These
pooled phases include failure-selected retries and different case mixes; they
must not be used to rank models.

Matching uses model, token counts and completion timestamps, with ambiguous
matches withheld. Additional requests are assigned by execution windows; shared
cohort energy contributes to batch means but never to per-task medians. Only
three tasks pass a conservative whole-window coverage guard, so the task medians
above describe partial attributed energy rather than complete consumption.

Neuralwatt changed its energy reporting on 6 November 2026; the results span
that change. The figures are illustrative rather than a uniform physical-energy
comparison. See the [provider changelog](https://neuralwatt.com/changelog?area=energy).
