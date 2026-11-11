# Retrieval friction and citation evidence

This analysis uses the existing 7,432 attempts and 7,402 saved trajectories.
It makes no candidate or search requests and leaves all published grades intact.
The deterministic pass covers every trace; a separate Jevotron pilot reviews
16 deliberately selected traces. Neither repeated retrieval nor uncited retrieval
is automatically classified as waste.

## Raw statistics

- [Per-attempt retrieval statistics](TRACE_RETRIEVAL_TRIALS.csv): 7,432 rows.
- [Grouped retrieval statistics](TRACE_RETRIEVAL_STATISTICS.csv): 2,740 rows,
  split by cohort and by cohort × harness × model × arm. Each metric includes
  its eligible denominator, total, affected-trace count and percentage, mean
  and median per eligible trace.
- [Metric definitions](TRACE_RETRIEVAL_DEFINITIONS.csv): 20 metrics.
- [Citation provenance](TRACE_CITATION_PROVENANCE.csv): 10,589 distinct
  trace/page pairs, with the event IDs that exposed each page and an explicit
  `semantic_support: not_assessed` field.
- [Jevotron pilot](TRACE_JEV_PILOT.csv): all 16 results, including low scores,
  with separate Codex review notes for seven traces.

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
outside the Jev pilot's bounded excerpts. These are case studies, not a
population support rate or a certification of every claim in an answer.

| Trace and evidence                      | Checked claim                                                                               | Assessment                                                                                                                                                      |
| --------------------------------------- | ------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `27145ad5cea5f3e8`, `s4:1`              | Wagtail 8.1 adds SEO metadata to content checks                                             | Supported by the saved 8.1 page's description of meta title, meta description and additional tags. The original fixed-8.0 grade is a separate grading artefact. |
| `3e49675d44f7f2b0`, `s3:0`              | Content checks use Axe and include `empty-meta-description`                                 | Supported by the saved guide passage naming the engine and the rule.                                                                                            |
| `42383817403a7fe0`, `s7:0` and `s8:0`   | Deleted documents cannot be recovered through Wagtail; deletion removes the file            | Supported by visible search/fetch passages. One cited source is the forbidden legacy editor manual: source-policy compliance and factual support differ.        |
| `032f383034dc553d`, `s11:0` and `s12:0` | Page privacy is changed through the status panel; shared passwords are stored in plain text | Supported by the saved manage-pages passage. The identical URL and arguments were fetched twice, making the second call a redundancy candidate.                 |

## Jevotron pilot

The installed `jt` CLI used `jev-1.13.0` with
[task-specific guidance](jev-retrieval-guidance.md). It assessed `/answer` and
`/retrieval` independently in 16 records selected by the existing
harness/arm-diversity, technique-enriched selector. All completed, using 147,139
input tokens and 1,119 output tokens. Dollar cost was not returned by this
report. The run exited successfully with 16 assessments, none from cache.

At a 0.5 threshold, five retrieval fields were flagged and no answer fields
were flagged. The CLI returned scores and labels, not explanatory rationales.
The notes in the published CSV are subsequent Codex review, not Jev explanations
or human adjudication. Low scores do not establish citation support.

Review of all five flagged traces found:

- Vibe repeated a successful page fetch with identical arguments
  (`032f383034dc553d`): a plausible redundancy candidate.
- OpenCode attempted unavailable tools three times in a baseline trace
  (`01ee2acc8198192f`), and Vibe repeatedly attempted denied tools in another
  (`30079b324c58f114`): clear friction, but not successful website requests.
- OpenCode hit Exa rate limits, obsolete developer paths and 404s before
  finding the accessibility page (`3b963949db3fa304`): observable discovery
  friction; not every recovery step was avoidable.
- Codex's search and subsequent fetch verified the document-deletion claim
  (`42383817403a7fe0`): plausible verification, not established waste.

Two low-score controls were also checked against full observations: the Fable
8.1 release answer and MiMo's content-checks answer above. This is insufficient
to estimate precision or recall. Truncated evidence, omitted middle calls, and
opaque actions limit semantic review; a negative flag is not an all-clear.

Jev is useful as a review queue over prepared evidence. It cannot perform the
cross-record joins, reconstruct missing HTTP data, or certify factual support
without passages. A larger review should first annotate a balanced validation
set with supported, contradicted and unknown claims, then measure reviewer
agreement. No full-corpus paid semantic scan has been launched.

## Reproduce

`just eval-agents-traces --output PATH` now also produces the four retrieval
CSVs. Use the existing review command to stage bounded, sanitized historical
observations; no raw result/config/session directories are copied:

```sh
just eval-agents-trace-review PATH --citation-review-stage --limit 16
just --command jt preview STAGING/evidence.jsonl \
  --id-column id --field /answer --field /retrieval --limit 2
just --command jt scan STAGING/evidence.jsonl \
  --id-column id --field /answer --field /retrieval \
  --guidance-file content/evals/agent-readiness-harbor/jev-retrieval-guidance.md \
  --cache PATH/citation-review-inputs/jev-cache.sqlite3 \
  -o STAGING/assessments.jsonl 2> STAGING/scan.log
```

The scan uses `TYPESAFE_API_KEY` and sends each entire staged record, not just
the selected fields. Staging caps records at 12 calls (first six and last six
for longer traces), 4,000 characters per observation, and 12,000 characters per
answer, with explicit omission/truncation flags. API credentials and local
session databases are not staged. Do not replace missing historical passages
with today's website content. The pilot's raw evidence, preview, assessments,
cache and log remain local under
`trace-analysis-followups-2026-11-11/citation-review-inputs/20261111T180310Z/`
(the cache is in the parent directory).
