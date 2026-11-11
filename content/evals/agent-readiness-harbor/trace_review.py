"""Stage whitelisted trace evidence and invoke Harbor's native analyzer."""

import argparse
import copy
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


def stage_citation_evidence(root, records, events, full_context=False):
    """Bounded historical evidence for Jev triage; no current-page substitutions."""
    from replay import call_api
    from trace_analysis import text

    by_trial = defaultdict(list)
    for event in events:
        by_trial[event["trial_id"]].append(event)
    staged = []
    for record in records:
        path = Path(record["trial_path"])
        trajectory = path.parent / "agent/trajectory.json"
        steps = (
            json.loads(trajectory.read_text())["steps"] if trajectory.exists() else []
        )
        outputs = {
            o["source_call_id"]: text(o.get("content"))
            for step in steps
            for o in (step.get("observation") or {}).get("results", [])
            if o.get("source_call_id")
        }
        fetch_prompts = {
            call["tool_call_id"]: call["arguments"].get("prompt", "")
            for step in steps
            for call in step.get("tool_calls") or []
            if isinstance(call.get("arguments"), dict)
        }
        answer = call_api(
            "", {}, {"vars": {"trial_path": str(path), "arm": record["arm"]}}
        ).get("output", "")
        calls = by_trial[record["id"]]
        # Both beginning and end of long attempts; never imply omitted middle is empty.
        selected = calls if len(calls) <= 12 else calls[:6] + calls[-6:]
        selected_ids = {event["id"] for event in selected}
        included = calls if full_context else selected
        retrieval = [
            {
                **{
                    k: event[k]
                    for k in ("id", "kind", "tool", "status", "query", "urls")
                },
                "observation_present": event["observation_present"],
                "returned_excerpt": outputs.get(event["call_id"], "")[:4000]
                if event["id"] in selected_ids
                else "",
                "excerpt_truncated": len(outputs.get(event["call_id"], "")) > 4000,
                "error_signal": event["error_signal"],
                **(
                    {
                        "excerpt_omitted": event["id"] not in selected_ids,
                        "argument_excerpt": event["argument_excerpt"],
                        "fetch_prompt": str(fetch_prompts.get(event["call_id"], ""))[
                            :1000
                        ],
                    }
                    if full_context
                    else {}
                ),
            }
            for event in included
        ]
        staged.append(
            sanitized(
                {
                    "id": record["id"],
                    "question": record["prompt"],
                    "harness": record["harness"],
                    "arm": record["arm"],
                    "answer": answer[:12000],
                    "answer_truncated": len(answer) > 12000,
                    "answer_present": bool(answer),
                    "retrieval": retrieval,
                    "calls_omitted": len(calls) - len(included),
                    "native_calls_without_atif": record["native_calls_without_atif"],
                    "trace_present": record["trace_present"],
                    **(
                        {
                            "evidence_version": 3,
                            "instruction_context": {
                                k: record[k]
                                for k in (
                                    "controls",
                                    "system_visibility",
                                    "recorded_system_excerpt",
                                    "system_excerpt_truncated",
                                )
                            },
                            "observation_excerpts_omitted": len(calls) - len(selected),
                        }
                        if full_context
                        else {}
                    ),
                }
            )
        )
    root.mkdir(parents=True, exist_ok=False)
    jsonl(root / "evidence.jsonl", staged)
    dump(
        root / "selection.json",
        {
            "ids": [r["id"] for r in records],
            "selection": "Caller-selected records; see caller manifest for population and sampling.",
            "max_calls": None if full_context else 12,
            "max_observation_excerpts": 12,
            "max_characters_per_observation": 4000,
            "max_answer_characters": 12000,
            "source": "Saved ATIF observations and replayed final answers; no live web fetches.",
        },
    )


def compact_citation_evidence(record):
    """Explicit fallback for context-limit failures; retain every call ID."""
    result = copy.deepcopy(record)
    limits = {
        "returned_excerpt": 1000,
        "argument_excerpt": 200,
        "fetch_prompt": 300,
        "query": 200,
        "tool": 256,
    }
    for event in result["retrieval"]:
        for field, limit in limits.items():
            if len(event.get(field, "")) > limit:
                event[field] = event[field][:limit]
                event[field + "_truncated"] = True
                if field == "returned_excerpt":
                    event["excerpt_truncated"] = True
        for field in list(event):
            if event[field] in ("", [], False):
                del event[field]
    result["context_reduction"] = {
        "reason": "Jev context limit; reduced excerpts, not omitted attempts",
        "character_limits": limits,
        "removed_call_keys": "Only empty strings, empty lists and false flags; missing keys retain these defaults.",
        "all_call_ids_retained": True,
    }
    if len(json.dumps(result)) > 32000:
        result["retrieval"][6:-6] = [
            {
                "id": event["id"],
                "summary": " ".join(
                    [
                        event["kind"],
                        event["tool"],
                        event["status"],
                        *event.get("urls", []),
                    ]
                ),
            }
            for event in result["retrieval"][6:-6]
        ]
        result["context_reduction"]["middle_request_details_omitted"] = True
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "directory", type=Path, nargs="?", default=CACHE / "trace-analysis"
    )
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--all", action="store_true")
    parser.add_argument(
        "--full-call-context",
        action="store_true",
        help="Keep every call summary and recorded instructions in citation-review staging",
    )
    parser.add_argument("--stage-only", action="store_true")
    parser.add_argument(
        "--citation-review-stage",
        action="store_true",
        help="Stage bounded saved passages and answers for Jevotron; no paid calls",
    )
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
    if args.citation_review_stage:
        staging = args.directory / "citation-review-inputs" / run
        stage_citation_evidence(
            staging,
            records,
            lines(args.directory / "events.jsonl"),
            full_context=args.full_call_context,
        )
        print(f"Staged {len(records)} citation/retrieval review records at {staging}")
        return
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
