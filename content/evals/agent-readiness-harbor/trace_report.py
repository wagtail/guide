"""Summarize recorded trace techniques without changing benchmark grades."""

import json
from collections import defaultdict
from pathlib import Path

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


def summarize(directory):
    records = [json.loads(line) for line in (directory / "trials.jsonl").open()]
    pairs = [json.loads(line) for line in (directory / "retry-pairs.jsonl").open()]
    inventory = json.loads((directory / "inventory.json").read_text())
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
        f"Analyzed **{len(records):,} benchmark attempts**: {len(initial):,} initial runs and {len(pairs):,} failure-selected retries. "
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
        "## Native-tool techniques by model",
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
        "## Question framing",
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
    (directory / "report.md").write_text("\n".join(lines))
    print(f"Wrote {directory / 'report.md'}")


if __name__ == "__main__":
    import sys

    summarize(Path(sys.argv[1]).expanduser())
