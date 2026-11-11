"""Export native Jevotron assessments without treating flags as verified errors."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from trace_analysis import csv_rows, dump
from trace_review import lines


def summarize(directory, trials, output):
    manifest = json.loads((directory / "manifest.json").read_text())
    completion = json.loads((directory / "completion.json").read_text())
    if not all(r["complete"] for r in completion):
        raise ValueError(
            "One or more native Jevotron shards failed; resume before publishing"
        )
    assessments = [
        r for p in sorted(directory.glob("assessments-*.jsonl")) for r in lines(p)
    ]
    ids = [r["id"] for r in assessments]
    if len(ids) != len(set(ids)) or set(ids) != set(manifest["ids"]):
        raise ValueError("Assessment IDs do not exactly cover the declared scope")
    source = {r["id"]: r for r in lines(trials)}
    coverage = {}
    for path in directory.glob("input-*.jsonl"):
        for record in lines(path):
            coverage[record["id"]] = {
                "context_reduced": bool(record.get("context_reduction")),
                "observation_excerpts_omitted": record.get(
                    "observation_excerpts_omitted", 0
                ),
                "truncated_excerpts": sum(
                    bool(e.get("excerpt_truncated")) and not e.get("excerpt_omitted")
                    for e in record["retrieval"]
                ),
                "all_recorded_call_summaries_included": record["calls_omitted"] == 0,
            }
    rows, usage, fresh_usage = [], Counter(), Counter()
    for assessment in assessments:
        record = source[assessment["id"]]
        row = {
            key: record[key]
            for key in (
                "id",
                "phase",
                "harness",
                "model",
                "arm",
                "case",
                "passed",
                "trace_present",
                "answer_present",
                "native_calls_without_atif",
            )
        }
        row.update(
            reviewer_model=assessment["model"],
            assessed_at=assessment["assessed_at"],
            request_hash=assessment["request_hash"],
            cached_on_this_scan=assessment["cached"],
            verification="model_assessment_not_adjudicated",
        )
        row.update(coverage[record["id"]])
        row["opaque_trace"] = bool(record["techniques"].get("opaque_calls"))
        fields = {f["path"]: f for f in assessment["fields"]}
        if set(fields) != {"/answer", "/retrieval"}:
            raise ValueError("Expected exactly the answer and retrieval assessments")
        for name in ("answer", "retrieval"):
            field = fields["/" + name]
            probabilities = field["probabilities"]
            if set(probabilities) != {"NORMAL", "ANOMALY", "UNKNOWN"}:
                raise ValueError("Expected revision 2/3 three-label assessment")
            row.update(
                {
                    name + "_label": field["label"],
                    name + "_anomaly_probability": probabilities["ANOMALY"],
                    name + "_unknown_probability": probabilities["UNKNOWN"],
                    name + "_normal_probability": probabilities["NORMAL"],
                    name + "_flagged_at_0_5": probabilities["ANOMALY"] >= 0.5,
                    name + "_confidence": field["confidence"],
                }
            )
        rows.append(row)
        usage.update(assessment.get("usage") or {})
        if not assessment["cached"]:
            fresh_usage.update(assessment.get("usage") or {})
    rows.sort(key=lambda r: r["id"])
    output.mkdir(parents=True, exist_ok=True)
    csv_rows(output / "jev-trials.csv", rows)
    groups = {("all", "all", "all", "all", "all"): rows}
    for row in rows:
        for key in (
            ("phase", row["phase"], "all", "all", "all"),
            ("arm", row["phase"], row["harness"], row["model"], row["arm"]),
        ):
            groups.setdefault(key, []).append(row)
    stats = []
    for key, group in sorted(groups.items()):
        for field in ("answer", "retrieval"):
            eligible = [
                r
                for r in group
                if r["trace_present"] and (field == "retrieval" or r["answer_present"])
            ]
            labels = Counter(r[field + "_label"] for r in eligible)
            n = len(eligible)
            flagged = sum(r[field + "_flagged_at_0_5"] for r in eligible)
            stats.append(
                {
                    **dict(zip(("scope", "phase", "harness", "model", "arm"), key)),
                    "field": field,
                    "scored_attempts": len(group),
                    "eligible": n,
                    "missing_answer_or_trajectory": len(group) - n,
                    "normal_label": labels["NORMAL"],
                    "anomaly_label": labels["ANOMALY"],
                    "unknown_label": labels["UNKNOWN"],
                    "flagged_at_0_5": flagged,
                    "flagged_percent": 100 * flagged / n if n else None,
                    "unknown_percent": 100 * labels["UNKNOWN"] / n if n else None,
                }
            )
    csv_rows(output / "jev-statistics.csv", stats)
    metadata = {
        "attempts": len(rows),
        "field_assessments": 2 * len(rows),
        "reviewer_models": sorted({r["reviewer_model"] for r in rows}),
        "cached_on_this_scan": sum(r["cached_on_this_scan"] for r in rows),
        "usage_including_cached_original_calls": dict(usage),
        "usage_fresh_calls_on_this_scan": dict(fresh_usage),
        "config_hashes": manifest.get("config_hashes"),
        "input_hashes": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(directory.glob("input-*.jsonl"))
        },
        "selection": manifest["selection"],
        "flags_are_not_verified_errors": True,
        "context_reduced_attempts": sum(r["context_reduced"] for r in rows),
        "attempts_with_omitted_observation_excerpts": sum(
            r["observation_excerpts_omitted"] > 0 for r in rows
        ),
        "attempts_with_truncated_excerpts": sum(
            r["truncated_excerpts"] > 0 for r in rows
        ),
        "opaque_traces": sum(r["opaque_trace"] for r in rows),
    }
    dump(output / "jev-inventory.json", metadata)
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--trials", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(args.directory, args.trials, args.output), indent=2))


if __name__ == "__main__":
    main()
