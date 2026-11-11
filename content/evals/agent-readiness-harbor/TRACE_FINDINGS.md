# What the execution traces show

New follow-ups provide a [full Jevotron review](TRACE_JEV_RESULTS.md),
[illustrative energy results](ENERGY_ANALYSIS.md), and
[GEPA/TextGrad prompt-improvement trials](PROMPT_IMPROVEMENT.md). They preserve
historical grading and distinguish automated suggestions from verified findings.

The follow-up [retrieval and citation analysis](TRACE_RETRIEVAL.md) quantifies
friction and separates source provenance from factual support. It includes
per-attempt statistics, a Jevotron review pilot and checked passages. The
[grading notes](GRADING_NOTES.md) explain the future-only fixes for two grading
artefacts identified in these traces; the scores below remain historical.

This analysis covers the **7,432 graded attempts** enumerated in [trace-sources.yaml](trace-sources.yaml): the original 4,356 runs, 1,761 failure-selected retries, 862 Tavily interventions, 396 Fable 5.2 runs, and 57 integration pilots. Cohorts are kept separate throughout. The ungraded Codex connectivity diagnostic is described in [the MCP pilot](MCP_PILOT.md); older setup/debugging exports are outside this inventory.

The [generated report](TRACE_RESULTS.md) and [raw statistics](TRACE_PATTERNS.csv) are the numeric source of truth. They contain **47 detected patterns**, with counts, percentages, eligible denominators and unknown counts. This page interprets selected patterns and documents counterexamples. No candidates or judges were rerun for this analysis, and no saved grades were changed.

## Fable: MCP changes retrieval, not just success rate

| Measure                            |        Native |      Web-only | Native+guide MCP |
| ---------------------------------- | ------------: | ------------: | ---------------: |
| Graded passes                      | 96/99 (97.0%) | 96/99 (97.0%) |    95/99 (96.0%) |
| Direct web-search traces           | 72/99 (72.7%) | 80/99 (80.8%) |      0/99 (0.0%) |
| Guide MCP traces                   |   0/99 (0.0%) |   0/99 (0.0%) |    87/99 (87.9%) |
| Final answers citing `/en-latest/` | 50/99 (50.5%) | 49/99 (49.5%) |      0/99 (0.0%) |
| Median tool calls                  |             4 |             2 |                4 |
| Mean tool calls                    |          3.48 |          2.86 |             4.07 |
| Median agent time                  |        33.3 s |        32.7 s |           12.5 s |

MCP was faster here despite having more calls on average. Call count is not interchangeable with time, token cost or useful retrieval. These counts include discovery tools; they do not count hidden server-side HTTP requests. The 99 baseline traces contain zero calls and pass 34/99 (34.3%).

The 12 native+MCP traces without guide MCP calls all concern developer/server questions and all pass; 11 answer without tools. For example, `d0702a269bce0c3a` answers the scheduled-publishing server question from memory. Another repeat, `1ff42b36e0805766`, discovers WebFetch at `s2:0` and fetches the developer management-command reference at `s3:0`. This is consistent with task-sensitive source selection. It is not evidence that the model always discovers all available tools.

MCP also changes URL selection. Five native+MCP traces still request an `/en-latest/` URL, but none retain that URL form in the final answer. Four contain a tool error and continue. By contrast, roughly half the native and web-only final answers cite `/en-latest/`. These are **URL-pattern counts**, not proof of outdated page content: redirects and served versions were not independently captured. The distinction between a requested URL and a final citation matters.

## The instructions matter, but these are not randomized wording variants

Each Fable arm contains 57 site-named attempts, 27 site-not-named attempts and 15 site-start attempts. The questions themselves differ between these groups.

| Fable arm  | Homepage first among site-start questions | Web search among site-start questions | Guide MCP among site-start questions |
| ---------- | ----------------------------------------: | ------------------------------------: | -----------------------------------: |
| Native     |                              3/15 (20.0%) |                          9/15 (60.0%) |                          0/15 (0.0%) |
| Web-only   |                              6/15 (40.0%) |                         11/15 (73.3%) |                          0/15 (0.0%) |
| Native+MCP |                               1/15 (6.7%) |                           0/15 (0.0%) |                         15/15 (100%) |

Telling an agent to start at the site does not guarantee that its first recorded action opens the homepage. Guide MCP can provide another route to the requested site content. A homepage-first metric alone would miss that route; it should not become a pass/fail instruction-compliance grade.

The original benchmark shows more workspace inspection in some coding harnesses: Qwen native 42/99 (42.4%), GLM 5.3 native 38/99 (38.4%), and Cursor native 30/99 (30.3%). Fable 5.2 has no detected local inspection across its 396 traces. Compare explicit controls and individual targets before attributing these differences to unseen system instructions.

## Tavily removes a search failure mode, not all retrieval friction

The 862 interventions target exact original slots with a rate-limited search in their initial attempt or retry. The prior outcome is the existing failure retry when present, otherwise the initial result. This avoids discarding earlier recoveries or counting retries twice.

| Outcome                                     | Count | Percentage of 862 slots |
| ------------------------------------------- | ----: | ----------------------: |
| Initial passes                              |   669 |                   77.6% |
| Previous passes, including existing retries |   736 |                   85.4% |
| Tavily passes                               |   750 |                   87.0% |
| Improved versus previous                    |    57 |                    6.6% |
| Regressed versus previous                   |    43 |                    5.0% |

The net gain versus the previous result is 14 slots, or 1.6 percentage points. Gemma native accounts for 35 improvements and four regressions; other model/arm changes are mixed. The [paired CSV](TRACE_TAVILY_PAIRS.csv) retains both directions. Neither the aggregate increase nor an individual recovery isolates Tavily's causal effect: tool schema, results, run date and live content also changed.

All 1,442 recorded Tavily search calls have native status `completed`, but **425/862 traces (49.3%) still contain a tool error**, commonly page-fetch 404s. **410/862 (47.6%)** contain a later call after an error. That proves continuation, not a deliberate or successful recovery strategy. Native OpenCode error excerpts are now retained in the local event evidence; previously ATIF omitted their text.

Two counterposed examples make the limits clear:

- DeepSeek's initial upgrade trace `4145c4dd826d3281` fails after fetching 8.0, 7.3 and 7.2 but omitting 7.4. The passing intervention `509648abfedd1ff7` searches at `s2:0` and `s2:1`, then fetches 8.0, 7.4 and 7.3 at `s3:0`–`s3:2`. Its earlier retry `dc22c466aebf3ce9` had already passed: this is an initial-failure contrast, **not one of the 57 improvements versus the previous result**. The original search also returned, so this example does not show that fixing search availability caused the change.
- Gemma's original scheduling trace `866992b2a0d70744` passes after fetching the guide at `s9:0`. Follow-up `9931a81d545eff7c` makes a returned Tavily search at `s2:0`, fetches no page, and fails with a less actionable answer. Successful search execution is insufficient evidence of answer quality.

## Qwen: successful retrieval can turn into prolonged investigation

Four Qwen Tavily attempts time out at 300 seconds: three stale-page questions and one locked-page question. They retain 29–34 calls each and remain failures. In `0491ca55c0f95e16`, Tavily returns at `s2:0`, followed by `llms.txt` at `s11:0`, curl for Markdown at `s14:0`, and GitHub template inspection at `s25:0` and `s27:0`. The user asks how to find stale pages **from the admin**; the investigation expands into implementation details without producing a final answer within the limit.

Another timeout, `8896760de0e092e8`, makes no Tavily call. These timeouts cannot all be explained by search-provider responses. “More tool calls” and “more source inspection” are not automatically better techniques; time-to-answer and evidence relevance need separate measures.

## Some failures reflect the grading snapshot

All three Fable native+MCP `start-latest-release` answers name Wagtail 8.1, while the frozen rubric requires 8.0. Trace `27145ad5cea5f3e8` cites the guide's 8.1 page and reports its November update. Native and web-only also fail this fixed latest-release case. This is a freshness mismatch between live retrieval and frozen grading, not sufficient evidence of retrieval failure.

The other MCP failure, `7ca9e744e410bc13`, explains the multi-tenancy database distinction in a table as “Separate per tenant,” but the deterministic assertion accepts only “separate database,” “separate databases” or “own database.” This is evidence of an overly literal phrase check. The saved 95/99 result remains unchanged; do not silently recalculate it as 99/99 or reinterpret every failed assertion as an agent error.

## Reading the raw numbers

Across the selected inventory, there are **22,898 unique recorded outer tool calls** with counts available for **7,402/7,432 attempts**. Thirty missing traces remain unknown. The pooled median is 1 call, mean 3.09, p90 8 and maximum 177; **2,771 traces have zero calls**. This mixture includes no-tools arms and failure-selected retries, so it is an inventory description, not a typical agent-performance score.

Two OpenCode native calls are absent from ATIF. They contribute to call totals through call-ID deduplication, but not fabricated step order or link-following sequences. Codex's nested operations are not expanded into invented calls. Vibe's empty tool-discovery operation still counts as a call even though it exposes no usable tool.

- [All pattern counts and rates](TRACE_PATTERNS.csv): absolute presence, not-observed, unknown, eligible denominator and percentage.
- [Pattern definitions](TRACE_PATTERN_DEFINITIONS.csv): exact operational meanings and denominator rules.
- [Tool-call distributions](TRACE_TOOL_CALLS.csv): per cohort and model/arm totals, mean, median, nearest-rank p90 and maximum.
- [Per-trace statistics](TRACE_TRIALS.csv): all 7,432 IDs, cases, outcomes, call counts and binary pattern flags, with blanks for unknowns.
- [By-arm statistics](TRACE_BY_ARM.csv) and [by-framing statistics](TRACE_BY_FRAMING.csv): wide tables, with a rate column for every pattern.

For an example event, join the trace ID to `trials.jsonl` and append `:sSTEP:INDEX` to locate it in `events.jsonl`. Both are generated locally by [the pipeline](TRACE_ANALYSIS.md). Examples here were selected for diagnosis; their frequency comes from the aggregate tables, not from the examples themselves.

The [external-method review](TRACE_RESEARCH.md) separates further checks feasible from these saved outputs from experiments that need new instrumentation. These findings combine whole-inventory deterministic measurements with bounded inspection of original evidence. The subsequent [full Jevotron review](TRACE_JEV_RESULTS.md) adds semantic triage across all attempts, with separate critical review and explicit evidence limitations.
