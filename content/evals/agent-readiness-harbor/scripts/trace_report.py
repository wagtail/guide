"""Summarize recorded trace techniques without changing benchmark grades."""

import json
from collections import defaultdict
from math import ceil
from pathlib import Path
from statistics import mean, median

from trace_analysis import csv_rows

FEATURES = (
    "search_requested",
    "homepage_first",
    "llms_txt_requested",
    "llms_full_requested",
    "sitemap_requested",
    "local_inspection",
    "curl_requested",
    "visible_link_following",
    "multiple_queries",
    "continued_after_error",
)

PATTERNS = {
    "search_requested": "Any direct web/guide search or recognizable scripted search intent.",
    "web_search_requested": "Direct public-web search, including Tavily; excludes guide search and opaque scripts.",
    "guide_search_requested": "Direct search_docs call in the registered Wagtail guide namespace.",
    "guide_mcp_requested": "Direct search or fetch in the registered Wagtail guide MCP namespace.",
    "tavily_search_requested": "Direct tavily_tavily_search call; public web search over MCP.",
    "mcp_requested": "Recognized direct MCP search or fetch, including both guide and Tavily tools.",
    "script_search_requested": "Opaque script contains a recognized web-search request expression; intent only.",
    "script_fetch_requested": "Opaque script contains a recognized fetch/open request expression; intent only.",
    "fetch_requested": "At least one direct URL target, literal curl target or recognizable scripted fetch intent.",
    "search_first": "All calls in the first navigation step are direct search calls.",
    "homepage_first": "All calls in the first navigation step target only the guide homepage.",
    "mixed_first_navigation": "First navigation step contains multiple distinct kinds/target surfaces.",
    "local_inspection": "Recognized file read/search/glob or local-inspection shell command.",
    "curl_requested": "A shell command invokes literal curl, including unresolved targets.",
    "shell_targets_unresolved": "Curl recognized but no safe literal target could be extracted.",
    "markdown_requested": "OpenCode webfetch requests Markdown, or curl explicitly requests text/markdown.",
    "delegation_requested": "Recognized Agent/Task/task tool call; not proof of useful delegated work.",
    "opaque_calls": "At least one exec/js_repl wrapper; nested actions may be hidden.",
    "missing_observations": "At least one ATIF call lacks a linked observation, even if native status exists.",
    "parallel_tool_group": "Multiple calls listed in one step; actual concurrency is not established.",
    "tool_error": "At least one ATIF call has a native/structured error, denial or recognized error text.",
    "continued_after_error": "A later step contains a call after an earlier error; does not establish intentional recovery.",
    "multiple_queries": "More than one distinct lowercased, trimmed visible query (bounded to 500 characters).",
    "repeated_query": "The same lowercased, trimmed visible query occurs more than once.",
    "repeated_fetch": "A URL target matches an earlier target after page normalization, even if either request failed.",
    "visible_link_following": "A requested normalized page appeared in an earlier returned tool output.",
    "search_result_following": "A requested normalized page appeared in an earlier returned search output.",
    "url_not_previously_visible": "A target has no normalized match in the prompt or earlier returned outputs; not necessarily guessed.",
    "no_observed_calls": "Saved ATIF trajectory contains no tool calls; missing trajectories are unknown.",
    "legacy_editor_manual_requested": "Direct/literal URL target on docs.wagtail.org contains editor_manual.",
    "en_latest_requested": "Direct/literal guide.wagtail.org target starts with /en-latest/.",
    "answer_cites_legacy_editor_manual": "Successfully replayed answer contains a docs.wagtail.org editor_manual URL.",
    "answer_cites_en_latest": "Successfully replayed answer contains a guide.wagtail.org /en-latest/ URL.",
}


def table(headers, rows):
    return "\n".join(
        [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
            *["| " + " | ".join(map(str, row)) + " |" for row in rows],
        ]
    )


def count(group, feature):
    return sum(r["techniques"].get(feature, False) for r in group)


def ratio(group, feature):
    known = [r for r in group if r["trace_present"]]
    if not known:
        return "Missing"
    if feature != "search_requested" and all(
        r["techniques"].get("opaque_calls") for r in known
    ):
        return "Opaque"
    return f"{count(known, feature)}/{len(known)}"


def statistics_exports(directory, records):
    """Absolute counts and explicit eligible denominators, without pooled scoring."""
    features = sorted({f for r in records for f in r["techniques"]})
    csv_rows(
        directory / "pattern-definitions.csv",
        [
            {
                "pattern": f,
                "definition": PATTERNS.get(
                    f,
                    "Direct/literal URL request classified by the original surface classifier as "
                    + f.removesuffix("_requested")
                    + "; not proof of successful access.",
                ),
                "denominator": "answers_present"
                if f.startswith("answer_")
                else "trajectories_present",
                "unknown": "Missing eligible answer/trajectory; opaque scripts and omitted observations also limit absence claims.",
            }
            for f in features
        ],
    )
    groups = {("all-recorded", "all", "all", "all", "all"): records}
    for r in records:
        for key in (
            ("cohort", r["phase"], "all", "all", "all"),
            ("arm", r["phase"], r["harness"], r["model"], r["arm"]),
        ):
            groups.setdefault(key, []).append(r)
    patterns, tools = [], []
    for key, group in sorted(groups.items()):
        identity = dict(
            zip(("scope", "phase", "harness", "model", "arm"), key, strict=True)
        )
        for feature in features:
            eligible = (
                [r for r in group if r["answer_present"]]
                if feature.startswith("answer_")
                else [r for r in group if r["trace_present"]]
            )
            n = len(eligible)
            present = count(eligible, feature)
            patterns.append(
                {
                    **identity,
                    "pattern": feature,
                    "attempts": len(group),
                    "denominator": "answers_present"
                    if feature.startswith("answer_")
                    else "trajectories_present",
                    "eligible": n,
                    "present": present,
                    "not_observed": n - present,
                    "unknown": len(group) - n,
                    "observed_rate": present / n if n else None,
                    "observed_percent": 100 * present / n if n else None,
                    "opaque_traces": count(eligible, "opaque_calls"),
                }
            )
        calls = sorted(
            r["recorded_tool_call_count"]
            for r in group
            if r["recorded_tool_call_count"] is not None
        )
        tools.append(
            {
                **identity,
                "attempts": len(group),
                "count_coverage": len(calls),
                "missing_counts": len(group) - len(calls),
                "total_calls": sum(calls),
                "zero_call_traces": calls.count(0),
                "mean_calls": mean(calls) if calls else None,
                "median_calls": median(calls) if calls else None,
                "p90_calls": calls[ceil(0.9 * len(calls)) - 1] if calls else None,
                "max_calls": max(calls) if calls else None,
                "atif_calls": sum(r["event_count"] for r in group),
                "native_calls_without_atif": sum(
                    r["native_calls_without_atif"] for r in group
                ),
                "opaque_traces": count(group, "opaque_calls"),
            }
        )
    csv_rows(directory / "pattern-statistics.csv", patterns)
    csv_rows(directory / "tool-call-statistics.csv", tools)
    csv_rows(
        directory / "per-trace-statistics.csv",
        [
            {
                **{
                    k: r[k]
                    for k in (
                        "id",
                        "phase",
                        "harness",
                        "model",
                        "agent_version",
                        "arm",
                        "case",
                        "framing",
                        "passed",
                        "execution_error",
                        "trace_present",
                        "answer_present",
                        "event_count",
                        "native_tool_call_count",
                        "native_calls_without_atif",
                        "recorded_tool_call_count",
                        "agent_seconds",
                    )
                },
                **{
                    f: int(r["techniques"].get(f, False))
                    if (
                        r["answer_present"]
                        if f.startswith("answer_")
                        else r["trace_present"]
                    )
                    else None
                    for f in features
                },
            }
            for r in records
        ],
    )
    return patterns, tools


def data_coverage(directory, records):
    groups = defaultdict(list)
    for r in records:
        groups[(r["phase"], r["harness"])].append(r)
    csv_rows(
        directory / "data-coverage.csv",
        [
            {
                "phase": phase,
                "harness": harness,
                "attempts": len(group),
                "atif_present": sum(r["trace_present"] for r in group),
                "native_log_present": sum(
                    (
                        Path(r["trial_path"]).parent / "agent" / (harness + ".txt")
                    ).is_file()
                    for r in group
                ),
                "trial_config_present": sum(
                    (Path(r["trial_path"]).parent / "config.json").is_file()
                    for r in group
                ),
                "manifest_present": sum(
                    (Path(r["trial_path"]).parents[3] / "manifest.json").is_file()
                    for r in group
                ),
                "replayed_answer_present": sum(r["answer_present"] for r in group),
                "system_text_recorded": sum(
                    r["system_visibility"] == "recorded" for r in group
                ),
                "timing_present": sum(r["agent_seconds"] is not None for r in group),
                "candidate_cost_present": sum(
                    r["candidate_cost_usd"] is not None for r in group
                ),
                "traces_with_missing_observations": count(
                    group, "missing_observations"
                ),
                "opaque_traces": count(group, "opaque_calls"),
            }
            for (phase, harness), group in sorted(groups.items())
        ],
    )


def intervention_pairs(directory, records):
    originals = {r["trial_path"]: r for r in records if r["phase"] == "initial"}
    retries = {r["original_trial"]: r for r in records if r["phase"] == "retry"}
    pairs = []
    for r in records:
        if r["phase"] != "tavily":
            continue
        original = originals[r["original_trial"]]
        assert (r["job"], r["case"], r["prompt"]) == (
            original["job"],
            original["case"],
            original["prompt"],
        )
        previous = retries.get(r["original_trial"], original)
        row = {
            "original_id": original["id"],
            "previous_id": previous["id"],
            "tavily_id": r["id"],
            "job": r["job"],
            "case": r["case"],
            "initial_passed": original["passed"],
            "previous_passed": previous["passed"],
            "tavily_passed": r["passed"],
            "improved_vs_previous": not previous["passed"] and r["passed"],
            "regressed_vs_previous": previous["passed"] and not r["passed"],
            "both_traces_present": previous["trace_present"] and r["trace_present"],
        }
        for prefix, record in (("previous", previous), ("tavily", r)):
            row[prefix + "_calls"] = record["recorded_tool_call_count"]
            for feature in (
                "tool_error",
                "local_inspection",
                "search_result_following",
                "multiple_queries",
                "homepage_first",
            ):
                row[prefix + "_" + feature] = (
                    record["techniques"].get(feature, False)
                    if record["trace_present"]
                    else None
                )
        pairs.append(row)
    assert len({p["original_id"] for p in pairs}) == len(pairs)
    csv_rows(directory / "tavily-pairs.csv", pairs)
    return pairs


def followup_sections(directory, records, tools, pairs):
    lines = [
        "## Completed follow-ups",
        "",
        "Each cohort stays separate from the original benchmark. Pattern fractions use available trajectories; tool counts include unique native OpenCode calls omitted from ATIF. No-tool traces contribute zero; missing counts are blank. Codex wrappers count as one outer call, not all nested operations.",
        "",
        table(
            [
                "Cohort",
                "Attempts",
                "Count coverage",
                "Total calls",
                "Mean",
                "Median",
                "P90",
                "Max",
                "Zero-call traces",
            ],
            [
                [
                    r["phase"],
                    r["attempts"],
                    r["count_coverage"],
                    r["total_calls"],
                    f"{r['mean_calls']:.2f}",
                    r["median_calls"],
                    r["p90_calls"],
                    r["max_calls"],
                    r["zero_call_traces"],
                ]
                for r in tools
                if r["scope"] == "cohort"
            ],
        ),
        "",
        "### Fable 5.2: same questions, different tool arms",
        "",
    ]
    rows = []
    for arm in ("native", "baseline", "web", "native+mcp"):
        group = [r for r in records if r["phase"] == "fable-5-2" and r["arm"] == arm]
        if not group:
            continue
        rows.append(
            [
                arm,
                f"{sum(r['passed'] for r in group)}/{len(group)}",
                ratio(group, "web_search_requested"),
                ratio(group, "guide_mcp_requested"),
                ratio(group, "homepage_first"),
                ratio(group, "local_inspection"),
                ratio(group, "tool_error"),
                median(r["recorded_tool_call_count"] for r in group),
                f"{median(r['agent_seconds'] for r in group):.1f}",
            ]
        )
    lines += [
        table(
            [
                "Arm",
                "Passes",
                "Web search",
                "Guide MCP",
                "Homepage first",
                "Local inspection",
                "Any tool error",
                "Median calls",
                "Median seconds",
            ],
            rows,
        ),
        "",
        "### Tavily: exact affected slots",
        "",
        "Each Tavily attempt is paired to its exact original slot. The previous outcome is the existing failure retry when present, otherwise the initial attempt. Previously passing slots are retained. Search provider, tool interface and run date changed; improvements and regressions are descriptive, not a causal estimate. The four timeouts remain failures.",
        "",
        table(
            [
                "Slots",
                "Initial passes",
                "Previous passes",
                "Tavily passes",
                "Improved vs previous",
                "Regressed vs previous",
            ],
            [
                [
                    len(pairs),
                    sum(p["initial_passed"] for p in pairs),
                    sum(p["previous_passed"] for p in pairs),
                    sum(p["tavily_passed"] for p in pairs),
                    sum(p["improved_vs_previous"] for p in pairs),
                    sum(p["regressed_vs_previous"] for p in pairs),
                ]
            ],
        ),
        "",
        "### Raw statistics and pattern definitions",
        "",
        "[Pattern statistics](data/patterns.csv) gives present/not-observed/unknown counts and rates for every detected pattern, by cohort and model/arm, plus an explicitly pooled inventory row. Answer-citation rates use available replayed answers; other rates use available trajectories. Not observed is not proof of absence, especially for opaque wrappers or incomplete observations.",
        "",
        "[Tool-call statistics](data/tool-calls.csv) gives totals, mean, median, nearest-rank p90, maximum and zero-call counts. [Per-trace statistics](data/trials.csv) gives each trace ID, case, result, call counts and every pattern (1/0; blank when unknown). It contains no prompts, responses, credentials or absolute local paths. [Tavily pairs](data/tavily-pairs.csv) exposes both improvements and regressions without double-counting retries.",
        "",
        "Any-search includes public web search, guide MCP search and recognizable Codex scripted search intent. Web-search excludes guide MCP and opaque scripted intent; guide-MCP excludes Tavily. MCP is a transport label, not a synonym for guide access. Per-pattern definitions are in [the data dictionary](data/pattern-definitions.csv). Initial benchmark tables above retain their original cohorts.",
        "",
    ]
    return lines


def summarize(directory):
    records = [json.loads(line) for line in (directory / "trials.jsonl").open()]
    pairs = [json.loads(line) for line in (directory / "retry-pairs.jsonl").open()]
    inventory = json.loads((directory / "inventory.json").read_text())
    _, tool_stats = statistics_exports(directory, records)
    data_coverage(directory, records)
    tavily_pairs = intervention_pairs(directory, records)
    initial = [r for r in records if r["phase"] == "initial"]
    native = [r for r in initial if r["arm"] == "native"]
    groups = defaultdict(list)
    for record in native:
        groups[(record["harness"], record["model"])].append(record)
    rows = [
        [
            h,
            m.split("/", 1)[-1],
            len(g),
            sum(r["trace_present"] for r in g),
            ratio(g, "search_requested"),
            count(g, "script_search_requested"),
            ratio(g, "homepage_first"),
            ratio(g, "local_inspection"),
            ratio(g, "llms_txt_requested"),
            ratio(g, "sitemap_requested"),
        ]
        for (h, m), g in sorted(groups.items())
    ]
    lines = [
        "# Techniques in the saved agent traces",
        "",
        f"Analyzed **{len(records):,} graded attempts across separate cohorts**: {len(initial):,} original initial runs, {len(pairs):,} failure-selected retries, and {len(records) - len(initial) - len(pairs):,} follow-up/pilot attempts. "
        f"**{inventory['traces_present']:,} trajectories** contain {inventory['events']:,} distinct recorded tool calls; "
        f"{len(records) - inventory['traces_present']} attempts have no saved trajectory. Missing traces are not classified as no-tool answers.",
        "",
        "The analysis reuses the original Promptfoo URL surface classifier, but measures **requests**, not successful access. "
        "It retains failed/blocked calls and exposes missing observations. Codex script contents establish requested intent, "
        "not confirmed nested execution. The old reports’ “reached” and “grounded” counts should not be treated as equivalent to these measures.",
        "",
        "Visible-link flags use the original normalized-page matcher: guide-version, Markdown suffix, query and fragment differences are ignored. "
        "Events distinguish exact sanitized URLs from normalized-page matches. These establish visible source candidates, not proof that the model followed a particular link.",
        "",
        "## Original benchmark: native-tool techniques by model",
        "",
        "Fractions use recorded trajectories as the denominator. Script search is included in search requests but also shown separately. "
        "“Opaque” means the wrapper prevents a direct absence claim. Positive direct counts remain lower bounds where observations are incomplete.",
        "",
        table(
            [
                "Harness",
                "Model",
                "Attempts",
                "Traces",
                "Search requests",
                "Script-search traces",
                "Homepage-first",
                "Local inspection",
                "llms.txt requests",
                "Sitemap requests",
            ],
            rows,
        ),
        "",
        "## Original benchmark: question framing",
        "",
        "These are **different questions**, not randomized paraphrases. “Site-named” has 19 questions, “site-not-named” nine, and “site-start” five. "
        "The table describes associations with wording; it does not isolate the causal effect of an instruction. Native arms only; each harness includes all its tested models.",
        "",
    ]
    rows = []
    for harness in sorted({r["harness"] for r in native}):
        for framing in ("site-named", "site-not-named", "site-start"):
            group = [
                r for r in native if r["harness"] == harness and r["framing"] == framing
            ]
            rows.append(
                [
                    harness,
                    framing,
                    len(group),
                    ratio(group, "homepage_first"),
                    ratio(group, "search_requested"),
                    ratio(group, "local_inspection"),
                ]
            )
    lines += [
        table(
            [
                "Harness",
                "Framing",
                "Attempts",
                "Homepage-first",
                "Search requests",
                "Local inspection",
            ],
            rows,
        ),
        "",
        "## Recorded instructions and restrictions",
        "",
        "Every attempt is linked to the original question, task category, arm controls and an instruction fingerprint. "
        "A fingerprint describes only recorded evidence: it does not establish equivalence between hidden harness system prompts. "
        "The full recorded system messages stay in the local instructions.jsonl; semantic review receives bounded excerpts with an explicit truncation flag.",
        "",
    ]
    rows = []
    for harness in sorted({r["harness"] for r in initial}):
        g = [r for r in initial if r["harness"] == harness]
        rows.append(
            [
                harness,
                len(g),
                sum(r["system_visibility"] == "recorded" for r in g),
                len({r["instruction_hash"] for r in g}),
            ]
        )
    lines += [
        table(
            [
                "Harness",
                "Initial attempts",
                "System text recorded",
                "Recorded instruction profiles",
            ],
            rows,
        ),
        "",
        "Only captured instructions and explicit arm controls can support instruction-specific explanations. "
        "Unavailable system text is not evidence that a harness had no system instructions. Tool availability, model identity and harness behavior also differ.",
        "",
        "## Comparing techniques with outcomes",
        "",
        "within-case-associations.csv compares feature-present and feature-absent initial attempts only where the **same model, arm and question** has both. "
        "Each eligible question contributes equally. These remain observational associations: a model may change approach because a question is difficult. "
        "For this table, missing trajectories, opaque wrappers, unresolved shell targets and missing observations are excluded; their full counts remain in the inventory and other tables.",
        "",
    ]
    cells = defaultdict(list)
    for record in initial:
        if (
            record["trace_present"]
            and not record["techniques"].get("opaque_calls")
            and not record["techniques"].get("missing_observations")
            and not record["techniques"].get("shell_targets_unresolved")
        ):
            cells[(record["job"], record["case"])].append(record)
    associations = []
    for job in sorted({r["job"] for r in initial}):
        for feature in FEATURES:
            deltas, covered = [], 0
            for (name, _), group in cells.items():
                if name != job:
                    continue
                yes = [r for r in group if r["techniques"].get(feature)]
                no = [r for r in group if not r["techniques"].get(feature)]
                if yes and no:
                    deltas.append(
                        sum(r["passed"] for r in yes) / len(yes)
                        - sum(r["passed"] for r in no) / len(no)
                    )
                    covered += len(group)
            if deltas:
                associations.append(
                    {
                        "job": job,
                        "feature": feature,
                        "matched_questions": len(deltas),
                        "attempts": covered,
                        "mean_with_minus_without_pass_rate": sum(deltas) / len(deltas),
                    }
                )
    csv_rows(directory / "within-case-associations.csv", associations)
    lines += [
        f"There are {len(associations)} model/arm/technique comparisons with at least one matched question. Small cells are for inspection, not significance claims.",
        "",
        "## Initial versus retry paths",
        "",
        "retry-pairs.jsonl links every retry to its original failure and lists added/removed recorded features. "
        "Retries are analyzed separately throughout because they are selected failures. A changed feature is not proof that a changed strategy caused recovery.",
        "",
        table(
            ["Retry pairs", "Both trajectories present", "Recovered failures"],
            [
                [
                    len(pairs),
                    sum(p["both_traces_present"] for p in pairs),
                    sum(p["recovered"] for p in pairs),
                ]
            ],
        ),
        "",
        "## Files and evidence review",
        "",
        "- trials.jsonl: one record per attempt, question, instructions, grade, timing and technique flags.",
        "- events.jsonl: event IDs, grouped step order, tool names, direct versus script requests, statuses, sanitized URL targets and link provenance. Raw response bodies are omitted.",
        "- by-arm.csv, by-framing.csv and by-case.csv: separate initial/retry counts, trace coverage and techniques.",
        "- instructions.jsonl: local recorded system text and arm controls, indexed by fingerprint.",
        "- retry-pairs.jsonl: exact initial/retry pairing with observed feature changes.",
        "- semantic-inputs/ and analysis-jobs/: whitelisted inputs and Harbor-native rubric review; keep model assessments separate from deterministic observations.",
        "",
        "No new candidate executions or grading changes are made by this pipeline. No proxy headers were captured in these runs, so HTTP Accept negotiation, redirect success and browser-only capabilities cannot be inferred from requests. "
        "Explicit Markdown formats are requests, not proof of served content. A URL with no visible earlier source is not automatically a guess. "
        "Shell analysis recognizes a conservative subset of literal curl and local commands; unrecognized shell constructs are not interpreted or executed.",
        "",
    ]
    lines += followup_sections(directory, records, tool_stats, tavily_pairs)
    (directory / "report.md").write_text("\n".join(lines))
    print(f"Wrote {directory / 'report.md'}")


if __name__ == "__main__":
    import sys

    summarize(Path(sys.argv[1]).expanduser())
