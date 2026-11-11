# Illustrative Neuralwatt task energy

This analysis retrieves existing account usage; it does not run candidates or
change grades. It covers the 3,858 Neuralwatt attempts in the published trace
inventory, including initial executions, retries, MCP and Tavily follow-ups.
The unit is an **attempt**, so initial and retry rows remain separate.

The complete cursor export contains **31,604 account requests**. Strict matching
assigns **16,123 of 16,331 recorded native turns** to **3,828 attempts**,
with **3,097.048 Wh** of attributed energy. This is 98.7% of recorded turns,
**not** 98.7% energy coverage. Thirty attempts have no strictly attributable energy;
22 have no completed native token event. Twenty-two turns are ambiguous and 186
have no compatible request within the matching tolerance. There are no exact
HTTP request-ID matches in these saved logs.

Supplemental time windows assign another **4,066 requests / 129.520 Wh**:
1,759 uniquely to one attempt and 2,307 only to a cohort shared by overlapping
attempts. The combined illustrative total is **3,226.568 Wh (3.227 kWh)**.
Strict token matches provide **95.99% of this window-attributed Wh**, which is
not a claim about the remaining account traffic. The other 11,415 exported
requests have no eligible saved execution window and remain unallocated.
No accepted request is counted twice. All 20,189 accepted requests have named
non-estimate attribution methods and nonmissing energy.

The following pools phases and arms for illustration. Strict means and medians
use attempts with strictly matched energy; window means divide supplemented
energy by **all** attempts, including failures and unknowns. Differences in case
mix, missing coverage and reporting regime prevent model rankings from this table.

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

## What the figures mean

For a comparison with the same original question/repeat counts, the initial
OpenCode arms have these **partial attributed medians in Wh per attempt**:

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
(96/99) and web-only (81/99). These medians include failed attempts when energy
is available, exclude missing amounts, and omit unallocated/group-only energy.
They compare resource use, not success-adjusted efficiency. Kimi K3.1 Pro has
only three MCP pilot attempts in this inventory and is absent from this table.

[ENERGY_TRIALS.csv](ENERGY_TRIALS.csv) contains one row per inventory attempt.
`attributed_energy_wh` sums energy on confidently matched requests, including
partially observed and failed attempts. Blank means unknown; a recorded zero
stays zero. `covered_task_energy_wh` is populated only when every recorded native
turn matches one API request with energy, there is no unassigned same-model
account request in the execution window, and Harbor reports no execution error.
This is a conservative coverage rule for the saved evidence, not proof that no
unrecorded provider retry occurred. Factual grading failures remain eligible.

[ENERGY_GROUPS.csv](ENERGY_GROUPS.csv) reports counts, totals, means and medians by
phase, harness, model and arm. `mean_attributed_attempt_wh` and `median_attributed_attempt_wh` use attempts
with strictly attributable energy, with denominator `attempts_with_attributed_energy`.
These are partial task amounts. The separate `mean_covered_task_wh` and
`median_covered_task_wh` use only the three tasks passing the strict whole-window
coverage guard; their `covered_tasks` denominator is explicit. Totals of attributed energy also retain
partial attempts. Missing and estimated requests have separate counts. The
`partial_attributed_wh_per_published_pass` column divides known attributed Wh,
including unsuccessful attempts, by all published passes in that group. Missing
energy makes it an incomplete accounting ratio, not a complete energy-per-success
benchmark. Timeouts are absent from covered-task means, so those means can
understate the cost of difficult tasks. Unequal coverage and case mixtures prevent
unqualified model or arm rankings.

There are two parallel grouping views: `scope=cohort` pools reporting regimes for
illustration, and `scope=regime` separates them. Do not sum both views together.
Requests within one task can span regimes; that task gets a combined regime label.
The grouped values are arithmetic means and medians of task sums, not medians
inferred from batch totals. Retried attempts are additional executions rather
than independent new questions.

[ENERGY_WINDOW_GROUPS.csv](ENERGY_WINDOW_GROUPS.csv) supplies a separate
illustrative batch view by phase, harness, model and arm. It combines strict
matches with supplemental time attribution, then divides by all attempts in the
cohort. This is a **mean**, never a median. Its three disjoint components
(`strict_attributed_wh`, `time_only_wh`, `group_only_wh`) reconcile to
`window_attributed_total_wh`. No per-task portion is invented for group-only
requests, so those requests cannot contribute to any per-task median.

[ENERGY_WINDOW_REQUESTS.csv](ENERGY_WINDOW_REQUESTS.csv) records only supplemental
requests. A request can receive `time_only` attribution if its accounting time is
inside exactly one saved same-model execution interval; with several overlapping
attempts it receives `group_only_time` only when all share the same cohort.
Debug tasks compete. Different-cohort overlaps and requests outside all eligible
intervals stay unallocated. The window uses the actual interval without padding.
This is an inference that assumes the eligible account traffic belongs to these
known runs, not an identity join: uncached or unrelated concurrent activity could
contaminate these illustrative amounts. Small auxiliary calls may be included,
but their function is not established by account metadata.

The per-task `time_only_energy_wh` and `matched_plus_time_energy_wh` expose the
uniquely allocated supplement without changing the strict per-task median basis.
The window ledger and strict ledger are disjoint. Neither the combined totals nor
strict share prove complete energy coverage; missing native events, provider
retries or delayed accounting can remain outside the assigned sets.

## Attribution and coverage

[energy_analysis.py](energy_analysis.py) reads native OpenCode `step_finish`
records, deduplicated by session and message ID. API prompt tokens equal native
input plus cache reads and writes; API completion tokens equal native output plus
reasoning. Matching requires the requested model, prompt tokens, cached tokens,
completion tokens and a completion timestamp within three seconds of the API
recording time. A match must be unique in both directions. Exact request IDs are
preferred when saved, but no chat-completion body ID is treated as an HTTP request
ID. Ambiguous matches are withheld rather than allocated across concurrent tasks.

Fifteen other cached Neuralwatt debug/preflight attempts compete for matches to
prevent accidental attribution; their energy is not included in inventory totals.
Unassigned account traffic is not assumed to belong to this benchmark. The
execution-window guard includes two seconds on either side. Delayed accounting,
missing native completion events and recorded execution errors can leave task
coverage partial even when some requests match. This deliberately trades coverage
for attribution confidence.

[ENERGY_REQUESTS.csv](ENERGY_REQUESTS.csv) provides each strictly matched request's task,
hashed request identifier, matching method, timestamp difference, token counts,
energy and attribution method. Each request appears at most once. Raw usage pages
and request IDs stay in the local cache; no credentials or transcripts are
published. The API is content-free, and this script never reads credential
databases. Sessions were not used for allocation: the provider's default derived
sessions can merge or split conversations. See the [request API](https://docs.neuralwatt.com/api/usage-requests)
and [session documentation](https://docs.neuralwatt.com/api/sessions).

Energy is reported in Wh, using joules / 3,600, or kWh × 1,000 when joules are
absent. Methods explicitly containing `estimated`, `fallback` or `compaction`
are counted as estimates; other named methods are labelled `reported_non_estimate`,
which does not mean direct measurement of each individual request. Unknown
methods remain distinct in the request ledger. All values concern
Neuralwatt-attributed inference energy: local agent execution, network traffic,
web search and MCP services are excluded.

## Measurement change

[Neuralwatt's 6 November 2026 changelog](https://neuralwatt.com/changelog?area=energy)
says consumed energy previously could include billing adjustments; new requests
report raw consumption or marked estimates, while historical rows stay unchanged.
The exact deployment time and which earlier rows were affected are unknown.
Requests before 6 November are labelled `pre_change`, those on that UTC date
`change_day_uncertain`, and later requests `post_change`. These are calendar
partitions, not a verified deployment boundary. Pooled figures are explicitly
illustrative, as requested; they must not be interpreted as a uniform physical
energy comparison. No prices or billing discounts are used to reconstruct energy.

## Reproduce

From the repository root, using the existing saved trials and native artifacts:

```sh
just --command uv run python content/evals/agent-readiness-harbor/energy_analysis.py fetch
just --command uv run python content/evals/agent-readiness-harbor/energy_analysis.py analyze
just --command uv run python -m unittest discover -s content/evals/agent-readiness-harbor -p test_energy_analysis.py
```

The default inventory is
`~/.cache/guide-agent-eval/harbor/trace-analysis-followups-2026-11-11/trials.jsonl`;
the usage cache is `~/.cache/guide-agent-eval/harbor/energy-2026-11-11/`.
`fetch` reads the Neuralwatt key locally from `~/dev/.keys.yml`, requests each
model's UTC execution range plus five minutes, respects the shared usage rate
limit and saves every cursor page. It checks the returned period and requires
complete pagination. Repeating `fetch` reuses saved pages; a changed inventory
range requires a fresh `--cache` directory. `analyze` is entirely offline and
accepts `--trials`, `--cache` and `--output` overrides. The local
`attribution-summary.json` records the inventory SHA-256 and reconciliation counts.
Eight regression tests cover token accounting, ambiguous overlaps, request IDs,
missing versus zero energy, the measurement-change date, CSV denominators and time-window allocation.
