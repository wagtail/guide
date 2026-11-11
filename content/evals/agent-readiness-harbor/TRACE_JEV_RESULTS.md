# Full Jevotron trace review

Jevotron assessed **all 7,432 recorded attempts**, producing **14,864 field
assessments** for answer support and potentially avoidable retrieval. Every
input ID has exactly one completed result. Candidate answers and benchmark
grades were not rerun or changed. These are model-generated review priorities,
not a new success metric or verified counts of hallucination and waste.

## Assessment and recommended use

**Jevotron is useful as a cheap triage layer, but its flags are not reliable
enough to count as errors or wasted retrieval.** At approximately $2.06 for
the scan and calibration, it surfaced concrete attribution contradictions,
unnecessary fetches and repeated attempts to use denied tools. Critical review
also found false alarms and insufficient caution when execution was opaque.

Retain the scores and evidence links as a review queue. Use deterministic
counts to establish repetition and failures, then inspect the original tool
arguments and returned evidence to judge whether the work was unnecessary.
Keep confirmed problems, plausible problems, insufficient evidence and rejected
flags separate. A NORMAL label does not certify efficiency or citation support.

Before using these judgments to compare models, independently review a
stratified sample across harnesses, arms and evidence-visibility levels,
including flagged, unflagged and UNKNOWN results. Reviewing unflagged traces
is necessary to measure missed problems as well as false alarms. The existing
diagnostic review does not provide that validation; this is a recommendation
for a further study, not a completed accuracy assessment.

## Results and denominators

| Field               | Eligible attempts | NORMAL label | ANOMALY label | UNKNOWN label | Anomaly probability ≥ 0.5 |
| ------------------- | ----------------: | -----------: | ------------: | ------------: | ------------------------: |
| Answer support      |             6,527 |        2,954 |           495 | 3,078 (47.2%) |                314 (4.8%) |
| Avoidable retrieval |             7,402 |        7,068 |           332 |     2 (0.03%) |                323 (4.4%) |

All 7,432 attempts were processed, including failures and missing evidence.
Answer rates exclude 905 attempts without an available answer/trajectory;
retrieval rates exclude 30 missing trajectories. Unknown support for an available
answer remains in the denominator. No-tool attempts remain eligible for
retrieval: a trace with no calls contains no observed wasted retrieval.

There are **617 distinct flagged attempts**, including 20 flagged in both
fields. The probability threshold differs from the selected label: 192
ANOMALY labels have probability below 0.5, and two NORMAL labels tie at 0.5 and
are included by the inclusive threshold. Probabilities are reviewer outputs,
not calibrated probabilities that a claim is false.

The inventory mixes initial runs, failure-selected retries and interventions.
Do not rank models using the pooled percentages. Raw data separates cohorts,
harnesses, models and arms:

- [All per-attempt assessments](TRACE_JEV_TRIALS.csv): 7,432 rows, probabilities,
  labels, evidence coverage, cache status and request hashes. Every result is
  marked `model_assessment_not_adjudicated`.
- [Grouped statistics](TRACE_JEV_STATISTICS.csv): 274 rows with explicit eligible
  denominators, missingness, labels and threshold flags.
- [Run inventory](TRACE_JEV_INVENTORY.json): exact scope, usage and input/config
  hashes.
- [Expanded calibration](TRACE_JEV_CALIBRATION.csv): 160 revision-2 assessments
  and 40 revision-3 rechecks, kept separate from the full-run statistics.
- [Critical review](TRACE_JEV_REVIEW.csv): 20 field reviews across 17 traces,
  with evidence event IDs, dispositions and notes.
- [Context reductions](TRACE_JEV_CONTEXT_REDUCTIONS.csv): all 13 affected traces.

Half the retrieval flags, **162/323**, concern no-tools arms: 115 Vibe and 47
OpenCode attempts. The reviewed examples involve attempts to use unavailable
tools or repeated policy denials. These are control/recovery problems, not
successful network retrievals. Other flags include repeated fetches and
irrelevant navigation; the CSVs allow comparison within each cohort and arm.

## What critical review found

Codex checked the selected traces against saved observations, including fuller
passages where the staged excerpt was insufficient. Selection deliberately
includes high scores, earlier diagnostic cases and low-score controls. It is
not an independent random audit and does not estimate precision or recall.
The observations themselves sometimes contain tool-generated summaries rather
than raw page text; they are evidence of what the candidate saw, not an
infallible copy of the source.

Useful flags include:

- **Contradicting the cited source description:** Haiku's
  `071700dfc25d0ddb` says the guide does not discuss multi-tenancy, while the
  returned guide summary at `s3:0` explicitly says it does. Full-run anomaly
  probability: 0.99. This is a concrete attribution problem.
- **Explicitly unnecessary retrieval:** Haiku's `6b9dac8fd2388c3e:s2:1`
  fetches an unrelated settings-model page with a prompt saying it is not
  needed and asking only for its title. The answer later succeeds, showing why
  outcome grading alone misses some unnecessary work.
- **Repeated access:** Vibe's `436d1a5e0cd4f4ba` fetches the same manage-pages
  URL three times; `032f383034dc553d` does so twice with identical arguments.
  These are redundancy candidates, though purposeful verification cannot be
  ruled out solely from call counts.
- **Restriction friction:** `01ee2acc8198192f` and `30079b324c58f114` repeatedly
  attempt unavailable or denied tools. Answer-like text embedded in a malformed
  tool name is not a delivered final answer.

Flags that require restraint include:

- **Incomplete excerpts mistaken for bad support:** the full saved scheduling
  page supports the claims in `4502304f4e2fd851`, including the management
  command beyond the excerpt boundary. Its revision-2 answer flag became
  UNKNOWN under revised guidance; neither the early flag nor UNKNOWN proves an
  incorrect answer.
- **Support elsewhere in the returned evidence:** `2ab0bb7bc3a9bdef` remains
  flagged, but another search passage supports the “all locked pages” wording.
  One summary saying “your locked pages” does not establish a contradiction.
- **Explicit separation of guide and other knowledge:** `21bbbc26c941c1a5`
  correctly attributes CSV/from/to/export facts to the guide and distinguishes
  extra UI advice. Review did not establish the specific contradiction implied
  by its high answer score; unverified extra details remain a limitation.
- **Attribution versus real-world correctness:** `1b9c0660e832ca50` says all
  navigation instructions are covered by its guide, while returned summaries
  explicitly omit the Pages-menu entry. That is an attribution gap, not proof
  that the navigation instruction itself is wrong.
- **Verification versus redundancy:** Codex's `42383817403a7fe0` searches and
  then fetches passages supporting document deletion. The revised reviewer
  does not flag that retrieval. Its legacy-editor citation still violates a
  separate benchmark source rule.
- **Friction versus avoidable effort:** GLM's `3b963949db3fa304` encounters
  rate limits and missing pages, then uses sitemap/llms discovery to find the
  correct page. The failures and recovery are observable; the retrieval flag
  does not establish that the recovery work was wasteful.

Low-score controls included MiMo's content-checks answer and Vibe's privacy
answer. Checked claims have support in the saved passages; this is not a
certification of every claim in either answer. The Fable 8.1 release example
likewise has source support, while its historical fixed-8.0 grade is stale.

## Reviewer limitations

The strongest caution is that **all 489 traces with opaque tool wrappers were
labelled NORMAL for retrieval**. Only two eligible retrieval traces received
UNKNOWN at all, despite missing/truncated observations elsewhere. This suggests
the reviewer is too willing to classify visible behavior as normal when it
cannot see the full execution. Do not read its negative results as evidence of
efficient retrieval, especially across harnesses with different visibility.

Answer support is also incomplete: 3,831 records have truncated observation
excerpts and 315 omit some observation excerpts. The full run retains every
recorded ATIF call summary, but it does not expose every returned page in full.
Two native calls missing from ATIF remain explicitly unplaced in the coverage data.
Unseen content can support a claim. Repeated WebFetch URLs can serve different
purposes because each call requests a different summary; the expanded input
therefore includes its `fetch_prompt`. Same-step calls have no asserted order.

The practical use is a review queue joined to deterministic trace evidence.
Keep verified findings, plausible inefficiency, insufficient evidence and false
alarms separate. A valid quality-rate estimate would need an independently
annotated, stratified sample and field-level agreement measures. This work does
not supply those estimates or claim complete manual review of all flags.

## Expansion, cost and reproducibility

The original 16-trace binary pilot is retained in [TRACE_JEV_PILOT.csv](TRACE_JEV_PILOT.csv).
The expansion first covered **160 traces**, retaining those 16 and covering all
129 cohort/harness/model/arm combinations. A native Jevotron config added
UNKNOWN as a third label. Review exposed false flags from incomplete excerpts
and missing WebFetch purposes. Guidance and three small, explicitly labelled
illustrative exemplars were refined; **40 calibration records** were rechecked,
then the same revision-3 configuration assessed the full inventory. The 40
rechecks are not a held-out accuracy test. Their cached assessments are reused
in the full run, not counted as 40 additional benchmark attempts.

All completed assessments used the installed `jt` CLI with `jev-1.13.0`; no custom inference
client or agent adapter was added. Eight disjoint input shards shared the
native assessment cache. Context-limit failures were retried with shorter
excerpts; 13 records were reduced, including three large remaining records
compacted proactively. All call IDs survived. Two long sequences retain middle
calls as concise kind/tool/status/URL summaries with omission metadata. Several
failures were caused by malformed tool names containing very large amounts of
model text, not by ordinary page retrieval.

The completed full-run assessments account for **47,725,957 input tokens** and
619,337 output tokens, including the original usage behind cached assessments.
At the published [Jev price](https://help.typesafe.ai/articles/5187202169-how-much-does-jev-cost)
of $0.042 per million input tokens and free output, that is **about $2.00**.
The full-cache ledger, including the expanded calibration and one extra compact
probe, totals 48,912,912 input tokens; including the earlier 16-trace pilot gives
an estimated **$2.06** for this review work. These are list-price estimates, not
billing reconciliation. Do not bill cached usage again or use only the last
resume's fresh-call tokens as the cost of the entire run.

The reusable configuration is [jev_config.py](jev_config.py), with
[revision-3 guidance](jev-retrieval-full-guidance.md) and
[exemplars](jev-exemplars.json). Initial staging is offline:

```sh
just eval-agents-trace-review PATH --citation-review-stage --full-call-context --all
```

The executed inputs, exact config snapshots, per-shard logs, completion
codes and native reports remain under
`PATH/citation-review-inputs/20261111T194535Z/`. Earlier calibration is under
`20261111T194154Z/`, including the initial preview. The shared cache is
`PATH/citation-review-inputs/jev-full-cache.sqlite3`. The local `run-shards.py`
only invokes native `jt scan`; it does not implement inference or grading.
For a single input shard or a merged JSONL of the archived final inputs:

```sh
just --command jt scan INPUT.jsonl --config STAGING/config.py \
  --id-column id --field /answer --field /retrieval \
  --guidance-file STAGING/guidance.md --exemplars STAGING/exemplars.json \
  --cache PATH/citation-review-inputs/jev-full-cache.sqlite3 \
  -o assessments.jsonl 2> scan.log
```

Use the archived final inputs to reproduce the context reductions exactly;
fresh staging alone does not apply those exception-specific reductions.
`compact_citation_evidence` in [trace_review.py](trace_review.py) implements that
fallback and records its limits. Preserve failed exits as incomplete, reuse
successful cached assessments, and check the entire declared ID set.
[jev_report.py](jev_report.py) exports completed shard reports only and rejects
missing or duplicate IDs. Raw staged passages and account credentials stay local.
