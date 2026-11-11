"""Stage whitelisted trace evidence and invoke Harbor's native analyzer."""

import argparse
import json
import os
import re
import subprocess
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from runner import CACHE, HERE, credentials, read
from trace_analysis import csv_rows, dump, jsonl, sanitized

CONTEXT = (
    "id",
    "phase",
    "harness",
    "model",
    "arm",
    "case",
    "framing",
    "task_type",
    "prompt",
    "passed",
    "grade_error",
    "execution_error",
    "trace_present",
    "event_count",
    "recorded_tool_call_count",
    "native_calls_without_atif",
    "answer_present",
    "instruction_hash",
    "system_visibility",
    "agent_implementation",
    "controls",
    "recorded_system_excerpt",
    "system_excerpt_truncated",
    "answer_excerpt",
    "techniques",
    "status_counts",
)


def lines(path):
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def select(records, limit):
    if limit is None:
        return records
    groups = defaultdict(list)
    for record in records:
        groups[(record["harness"], record["arm"])].append(record)
    selected = []

    # Cover every supported harness/arm before filling additional slots. This is
    # a diagnostic sample, deliberately enriched for strategy and coverage issues.
    def rank(record):
        return -sum(record["techniques"].values()), record["id"]

    for group in groups.values():
        selected.append(sorted(group, key=rank)[0])
    selected.sort(key=lambda r: (r["harness"], r["arm"]))
    ids = {r["id"] for r in selected}
    selected.extend(sorted((r for r in records if r["id"] not in ids), key=rank))
    return selected[:limit]


def stage(root, records, events, population=None):
    root.mkdir(parents=True, exist_ok=False)
    (root / "job.log").touch()
    by_trial = defaultdict(list)
    for event in events:
        by_trial[event["trial_id"]].append(event)
    for record in records:
        trial = root / record["id"]
        trial.mkdir()
        (trial / "trial.log").touch()
        context = {key: record.get(key) for key in CONTEXT}
        context = sanitized(context)
        dump(trial / "context.json", context)
        jsonl(trial / "events.jsonl", sanitized(by_trial[record["id"]]))
        # Never stage result.json: Harbor follows its config.task path and copies
        # that directory, and recursively copies everything in the source trial.
        assert {p.name for p in trial.iterdir()} == {
            "trial.log",
            "context.json",
            "events.jsonl",
        }
    dump(
        root / "selection.json",
        {
            "ids": [r["id"] for r in records],
            "population": population,
            "selection": "All attempts"
            if population == len(records)
            else "Diagnostic sample, not representative prevalence",
        },
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "directory", type=Path, nargs="?", default=CACHE / "trace-analysis"
    )
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--stage-only", action="store_true")
    parser.add_argument(
        "--resume-report",
        type=Path,
        help="Review only missing/failed IDs from a previous native analysis report",
    )
    parser.add_argument("--model", default="anthropic/claude-haiku-5-5")
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--keys", type=Path, default=Path.home() / "dev/.keys.yml")
    args = parser.parse_args()
    if args.limit < 1 or args.concurrency < 1:
        parser.error("limit and concurrency must be positive")
    population = lines(args.directory / "trials.jsonl")
    if args.resume_report:
        previous = json.loads(args.resume_report.read_text())
        selection = json.loads(
            (
                args.directory
                / "semantic-inputs"
                / args.resume_report.parent.name
                / "selection.json"
            ).read_text()
        )
        completed = {r["trial_name"] for r in previous["results"] if not r.get("error")}
        missing = set(selection["ids"]) - completed
        records = [r for r in population if r["id"] in missing]
        if {r["id"] for r in records} != missing:
            raise ValueError(
                "Previous semantic IDs are missing from this extraction; restore the original inputs before resuming"
            )
    else:
        records = select(population, None if args.all else args.limit)
    if not records:
        print("No missing semantic analyses to run.")
        return
    run = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    staging = args.directory / "semantic-inputs" / run
    stage(staging, records, lines(args.directory / "events.jsonl"), len(population))
    selection_path = staging / "selection.json"
    selection = json.loads(selection_path.read_text())
    selection["parent_report"] = (
        str(args.resume_report.resolve()) if args.resume_report else None
    )
    dump(selection_path, selection)
    print(f"Staged {len(records)} whitelisted traces at {staging}", flush=True)
    if args.stage_only:
        return
    config = args.directory / "analysis-config.json"
    dump(
        config,
        {
            "retry": {"max_retries": 0},
            "agent_timeout_multiplier": 1 / 6,
            "agent_setup_timeout_multiplier": 2,
        },
    )
    env = {
        k: v
        for k, v in os.environ.items()
        if not any(word in k.upper() for word in ("KEY", "TOKEN", "SECRET", "PASSWORD"))
    }
    env.update(
        credentials(
            {
                "id": "trace-review",
                "credentials": {"ANTHROPIC_API_KEY": ["ANTHROPIC_API_KEY"]},
            },
            read(args.keys),
        )
    )
    command = [
        "harbor",
        "analyze",
        str(staging),
        "--rubric",
        str(HERE / "trace-rubric.yaml"),
        "--prompt",
        str(HERE / "trace-prompt.txt"),
        "--agent",
        "claude-code",
        "--model",
        args.model,
        "--ak",
        "version=2.1.318",
        "--ak",
        "max_turns=20",
        "--ak",
        "max_budget_usd=0.30",
        "--ak",
        "disallowed_tools=Bash,WebSearch,WebFetch,Agent,Task,Skill",
        "--ae",
        "ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}",
        "--config",
        str(config),
        "--n-concurrent",
        str(args.concurrency),
        "--job-name",
        run,
        "--jobs-dir",
        str(args.directory / "analysis-jobs"),
    ]
    completed = subprocess.run(command, env=env, check=False)
    report_path = args.directory / "analysis-jobs" / run / "analysis.json"
    if not report_path.exists():
        raise RuntimeError(
            f"Harbor analyze exited {completed.returncode} without a report: {report_path}"
        )
    report = json.loads(report_path.read_text())
    dump(args.directory / "latest-semantic-report.json", report)
    source = {r["id"]: r for r in records}
    findings = []
    for result in report["results"]:
        trial_id = result["trial_name"]
        if trial_id not in source:
            raise RuntimeError(f"Unexpected semantic result ID: {trial_id}")
        event_ids = {e["id"] for e in lines(staging / trial_id / "events.jsonl")}
        for criterion, check in result.get("checks", {}).items():
            cited = set(re.findall(r"[a-f0-9]{16}:s\d+:\d+", check["explanation"]))
            findings.append(
                {
                    "id": trial_id,
                    "model": source[trial_id]["model"],
                    "arm": source[trial_id]["arm"],
                    "criterion": criterion,
                    **check,
                    "invalid_event_ids": ",".join(sorted(cited - event_ids)),
                    "no_full_event_citations": not cited,
                }
            )
    csv_rows(report_path.parent / "findings.csv", findings)
    if (
        {r["trial_name"] for r in report["results"]} != set(source)
        or len(report["results"]) != len(records)
        or any(r.get("error") for r in report["results"])
    ):
        raise RuntimeError(
            "Native analysis is incomplete; inspect per-trial errors in analysis.json"
        )
    print(
        f"Schema-validated {len(records)} native analysis results; inspect findings.csv for evidence-reference flags."
    )


if __name__ == "__main__":
    main()
