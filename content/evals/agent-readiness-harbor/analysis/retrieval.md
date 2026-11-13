# Retrieval friction and citation evidence

This analysis uses the existing 7,432 attempts and 7,402 saved trajectories.
It makes no candidate or search requests and leaves all published grades intact.
The deterministic pass covers every trace. Repeated or uncited retrieval is not
automatically waste; see the [review highlights](README.md#what-automated-trace-review-added).

## Raw statistics

- [Per-attempt retrieval statistics](data/retrieval-trials.csv): 7,432 rows.
- [Grouped retrieval statistics](data/retrieval-statistics.csv): 2,740 rows,
  split by cohort and by cohort × harness × model × arm. Each metric includes
  its eligible denominator, total, affected-trace count and percentage, mean
  and median per eligible trace.
- [Metric definitions](data/retrieval-definitions.csv): 20 metrics.
- [Citation provenance](data/citation-provenance.csv): 10,589 distinct
  trace/page pairs, with the event IDs that exposed each page and an explicit
  `semantic_support: not_assessed` field.

Across the whole mixed inventory, 19,437 visible retrieval calls include 5,741
recorded failures. There are 346 calls that revisit a previously returned page
target, across 247 traces. These totals include initial runs, failure-selected
retries, interventions and baseline arms; they are an inventory, not a fair
pooled model ranking. Opaque nested calls and two native calls missing from ATIF
are excluded from the event-level measurements.

## Tavily: discovery works, fetching still causes friction

In the 862-attempt Tavily intervention:

| Measure                                                   | Absolute count |                 Relative count |
| --------------------------------------------------------- | -------------: | -----------------------------: |
| Visible retrieval calls                                   |          4,616 |             Median 4 per trace |
| Failed retrieval calls                                    |            902 |       19.5% of retrieval calls |
| Traces with failed retrieval                              |            423 |            49.1% of 862 traces |
| Calls revisiting a previously returned page target        |             46 |        In 33/862 traces (3.8%) |
| Traces with returned pages absent from answer URLs        |            441 | 51.4% of 858 available answers |
| Answer page URLs matching returned fetch targets          |            831 |  59.0% of 1,408 citation pages |
| Answer page URLs visible only in search output            |            281 |  20.0% of 1,408 citation pages |
| Answer page URLs absent from visible retrieval and prompt |             96 |   6.8% of 1,408 citation pages |

All 1,442 native Tavily search calls recorded completed status. The 902 failures
are other visible retrieval calls, not evidence that Tavily failed 902 times.
Other-output and prompt provenance account for the citation categories not
shown in the table. Four timeout attempts have unknown answer metrics, not zero
citations. Some successful fetches are only navigation, indexes or background
information, so the 1,319 returned page targets not cited do not measure waste.

## Fable 5.2: MCP changes the retrieval-to-citation relationship

Each arm has 99 attempts and 99 available answers. Citation percentages use
unique trace/page pairs, so a page repeated within an answer counts once.

| Arm          | Retrieval calls | Failed retrieval calls | Citation pages matching returned targets | Traces with returned targets not cited |
| ------------ | --------------: | ---------------------: | ---------------------------------------: | -------------------------------------: |
| Native       |             259 |                      0 |           105/206 citation pages (51.0%) |                          55/99 (55.6%) |
| Web          |             283 |                      0 |           120/217 citation pages (55.3%) |                          57/99 (57.6%) |
| Native + MCP |             315 |                      4 |           140/201 citation pages (69.7%) |                            9/99 (9.1%) |
| Baseline     |               0 |                      0 |                0/195 citation pages (0%) |                              0/99 (0%) |

MCP has more visible retrieval calls, but more citation pages match returned
targets and fewer traces contain fetched targets absent from the answer. This
is consistent with more focused source selection, not proof of less wasted
work or better factual support. Existing timing results also show why fewer
calls should not stand in for faster execution.

The baseline's 195 citation pages have no observed retrieval, as expected from
its instructions. They may be remembered URLs; absence of a fetch is not proof
of a fabricated citation. Apply the same restraint to tool-enabled traces with
incomplete or opaque observations.

## What the measurements can establish

The funnel distinguishes URLs exposed in search output, requested pages,
returned targets and final answer URLs. Search output can include navigation
links, so this is not a reconstructed ranking of search candidates. A returned
tool status is not an HTTP status or a guarantee that the response contains
useful page text. Missing observations stay distinguishable from observed
errors. Repeats and link-following require an earlier step, never an invented
order among calls listed in one step.

Page matching retains version paths and Markdown representations. It ignores
scheme, trailing slash, query and fragment, using sanitized host/path pairs.
It does not assume `/en-latest/`, `/en/`, or `/markdown/` are equivalent or infer
unrecorded redirects. Consequently, some apparent uncited retrieval is a
representation/alias mismatch. The older general technique flags use broader
page normalization; the two measures deliberately answer different questions.

`calls_before_reference_return` measures outer calls before the first returned
fetch whose target matches a frozen reference URL. It is available for 1,814
traces, with median 3 preceding calls; other traces are null. It is only a URL
proxy, not time to useful evidence: the answer may already be in a search
snippet, another page, or memory. The historical release reference can itself
be stale. Do not interpret this metric as a quality score.

## Citation support: checked claims, not just URL matches

Codex inspected the full saved observations for these claims, including text
outside bounded review excerpts. These are case studies, not a
population support rate or a certification of every claim in an answer.

| Trace and evidence                      | Checked claim                                                                               | Assessment                                                                                                                                                      |
| --------------------------------------- | ------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `27145ad5cea5f3e8`, `s4:1`              | Wagtail 8.1 adds SEO metadata to content checks                                             | Supported by the saved 8.1 page's description of meta title, meta description and additional tags. The original fixed-8.0 grade is a separate grading artefact. |
| `3e49675d44f7f2b0`, `s3:0`              | Content checks use Axe and include `empty-meta-description`                                 | Supported by the saved guide passage naming the engine and the rule.                                                                                            |
| `42383817403a7fe0`, `s7:0` and `s8:0`   | Deleted documents cannot be recovered through Wagtail; deletion removes the file            | Supported by visible search/fetch passages. One cited source is the forbidden legacy editor manual: source-policy compliance and factual support differ.        |
| `032f383034dc553d`, `s11:0` and `s12:0` | Page privacy is changed through the status panel; shared passwords are stored in plain text | Supported by the saved manage-pages passage. The identical URL and arguments were fetched twice, making the second call a redundancy candidate.                 |

## Reproduce

```sh
just eval-agents-traces --output ~/.cache/guide-agent-eval/harbor/trace-analysis-followups-2026-11-11
```

This extracts statistics offline from the saved runs; it makes no paid calls.
