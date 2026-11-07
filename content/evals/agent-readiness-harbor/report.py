"""Join original grades to Harbor's execution timing and reported cost."""

import csv
import json
from datetime import datetime
from statistics import median


def seconds(timing):
    if not timing or not timing.get("started_at") or not timing.get("finished_at"):
        return None
    return (
        datetime.fromisoformat(timing["finished_at"])
        - datetime.fromisoformat(timing["started_at"])
    ).total_seconds()


def report(root):
    manifest = json.loads((root / "manifest.json").read_text())
    grades = json.loads((root / "grades.json").read_text())["results"]["results"]
    by_trial = {r["testCase"]["vars"]["trial_path"]: r for r in grades}
    rows = []
    for job in manifest["jobs"]:
        paths = sorted((root / "jobs" / job["name"]).glob("*/result.json"))
        times, costs, setup_times, judge_costs, versions = [], [], [], [], set()
        passed = errors = unknown = graded = grading_errors = 0
        for path in paths:
            trial = json.loads(path.read_text())
            grade = by_trial.get(str(path.resolve()))
            versions.add(trial["agent_info"]["version"])
            if (duration := seconds(trial.get("agent_execution"))) is not None:
                times.append(duration)
            if (cost := (trial.get("agent_result") or {}).get("cost_usd")) is not None:
                costs.append(cost)
            setup = [
                seconds(trial.get(p)) for p in ("environment_setup", "agent_setup")
            ]
            if all(t is not None for t in setup):
                setup_times.append(sum(setup))
            if grade:
                graded += 1
                passed += bool(grade.get("success"))
                errors += bool(
                    trial.get("exception_info")
                    or (grade.get("response") or {}).get("error")
                )
                components = (grade.get("gradingResult") or {}).get(
                    "componentResults", []
                )
                unknown += any(
                    str(c.get("reason", "")).startswith("UNKNOWN:") for c in components
                )
                grading_errors += any(
                    str(c.get("reason", "")).startswith("Error") for c in components
                )
                for component in components:
                    usage = (component.get("metadata") or {}).get("modelUsage", {})
                    judge_costs.extend(
                        m["costUSD"]
                        for m in usage.values()
                        if m.get("costUSD") is not None
                    )
            elif trial.get("exception_info"):
                errors += 1
        expected = len(manifest["cases"]) * manifest["repeat"]
        rows.append(
            {
                "job": job["name"],
                "model": job["entry"]["model"],
                "versions": ",".join(sorted(versions)),
                "expected": expected,
                "finished": len(paths),
                "graded": graded,
                "passed": passed,
                "success_rate": passed / expected,
                "errors": errors,
                "grading_errors": grading_errors,
                "unknown_judgments": unknown,
                "median_agent_seconds": median(times) if times else None,
                "timing_coverage": len(times),
                "median_setup_seconds": median(setup_times) if setup_times else None,
                "known_judge_cost_usd": sum(judge_costs) if judge_costs else None,
                "known_agent_cost_usd": sum(costs) if costs else None,
                "cost_coverage": len(costs),
                "cost_per_success_usd": sum(costs) / passed
                if passed and len(costs) == expected
                else None,
            }
        )
    with (root / "comparison.csv").open("w") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print("Job | Passed / expected | Median agent seconds | Known cost USD (coverage)")
    for row in rows:
        duration = row["median_agent_seconds"]
        cost = row["known_agent_cost_usd"]
        print(
            f"{row['job']} | {row['passed']}/{row['expected']} | {duration if duration is not None else 'unknown'} | {cost if cost is not None else 'unknown'} ({row['cost_coverage']}/{row['expected']})"
        )
    print(f"Full comparison: {root / 'comparison.csv'}")
