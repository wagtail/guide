"""
Summarize an agent readiness eval run, per arm.

Reads promptfoo's JSON output (`just eval-agents ... --output run.json`) and,
optionally, the proxy's request log, and prints Markdown tables: pass rate,
cost and duration per arm, how often each surface was reached, and which
formats agents asked the guide for.

    uv run python content/evals/agent-readiness/summarize.py run.json \
        --proxy-log ~/.cache/guide-agent-eval/requests.jsonl
"""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, stdev
from urllib.parse import urlsplit

# What each kind of check in `tests.yaml` tests: the facts in the answer, the
# pages it cites, and the judge's rubric. Reported separately, so an arm that
# knows the answer but can't cite the guide shows up as such.
CHECK_METRICS = ["facts", "citation", "judge"]

# Trace columns shown in the reach table, in the order agents tend to meet them.
# The arm others are compared with: the guide as it is, with web tools.
REFERENCE_ARM = "web"

# Columns that count things per run, rather than being 0 or 1.
COUNT_COLUMNS = {
    "citations_not_fetched",
    "fetch_errors",
    "curl_calls",
    "permission_denials",
}

REACH_COLUMNS = [
    "web_search_used",
    "homepage_reached",
    "docs_reached",
    "markdown_page_reached",
    "llms_txt_reached",
    "llms_full_reached",
    "skill_reached",
    "mcp_used",
    "sitemap_reached",
    "robots_txt_reached",
    "well_known_reached",
    "openapi_reached",
    "dev_docs_reached",
    "github_copy_reached",
    "external_reached",
    "answer_cites_guide",
    "answer_grounded",
    "citations_not_fetched",
    "versioned_url_reached",
    "answer_cites_versioned_url",
    "legacy_editor_manual_reached",
    "answer_cites_legacy_editor_manual",
    "fetch_errors",
    "curl_calls",
    "permission_denials",
]


def load_results(path):
    data = json.loads(Path(path).read_text())
    return data["results"]["results"]


def arm(result):
    provider = result.get("provider") or {}
    return provider.get("label") or provider.get("id", "?")


def table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join(lines)


def percent(values):
    return f"{100 * mean(values):.0f}%" if values else "-"


def number_repeats(results):
    """
    Set `repeat` on each result. promptfoo's `--repeat` runs each case several
    times in a row, so a case's runs in one arm are its repeats, in order.
    """
    seen = Counter()
    for result in sorted(results, key=lambda result: result.get("testIdx", 0)):
        key = (arm(result), result.get("testCase", {}).get("description"))
        result["repeat"] = seen[key]
        seen[key] += 1


def pass_rate(runs):
    """Pass rate, with its spread across repeats when there are several."""
    by_repeat = defaultdict(list)
    for run in runs:
        by_repeat[run.get("repeat", 0)].append(bool(run.get("success")))
    rates = [100 * mean(passes) for passes in by_repeat.values()]
    if len(rates) < 2:
        return percent([bool(run.get("success")) for run in runs])
    return f"{mean(rates):.0f}% ± {stdev(rates):.0f}"


def task(run):
    return run.get("testCase", {}).get("metadata", {}).get("task", "?")


def framing(run):
    return run.get("testCase", {}).get("metadata", {}).get("framing", "?")


def print_versus(by_arm):
    """Each arm against the guide as it is, like the draftjs_exporter evals."""

    def stats(runs):
        return (
            100 * mean(bool(run.get("success")) for run in runs),
            mean(run.get("latencyMs") or 0 for run in runs) / 1000,
            100 * mean(run.get("cost") or 0 for run in runs),
        )

    passed, duration, cost = stats(by_arm[REFERENCE_ARM])
    rows = []
    for name, runs in by_arm.items():
        if name == REFERENCE_ARM:
            continue
        arm_passed, arm_duration, arm_cost = stats(runs)
        rows.append(
            [
                name,
                f"{arm_passed - passed:+.1f} pts",
                f"{duration:.0f}s → {arm_duration:.0f}s",
                f"{cost:.1f}¢ → {arm_cost:.1f}¢",
            ]
        )
    print(f"\n## Versus `{REFERENCE_ARM}` (the guide as it is)\n")
    print(
        table(
            ["Arm", "Pass rate change", "Duration per answer", "Cost per answer"], rows
        )
    )


def summarize(results):
    number_repeats(results)
    repeats = len({run["repeat"] for run in results})
    by_arm = defaultdict(list)
    for result in results:
        by_arm[arm(result)].append(result)

    overview = []
    for name, runs in by_arm.items():
        overview.append(
            [
                name,
                len(runs),
                pass_rate(runs),
                *[
                    percent([run.get("namedScores", {}).get(metric, 0) for run in runs])
                    for metric in CHECK_METRICS
                ],
                f"{100 * mean(run.get('cost') or 0 for run in runs):.1f}¢",
                f"{mean(run.get('latencyMs') or 0 for run in runs) / 1000:.0f}s",
                f"{mean(run.get('namedScores', {}).get('tool_calls', 0) for run in runs):.1f}",
            ]
        )
    spread = " (mean ± SD across repeats)" if repeats > 1 else ""
    print(f"## Results per arm, {repeats} repeat(s){spread}\n")
    print(
        table(
            [
                "Arm",
                "Runs",
                "Pass",
                *(metric.capitalize() for metric in CHECK_METRICS),
                "Cost/answer",
                "Duration",
                "Tool calls",
            ],
            overview,
        )
    )

    if REFERENCE_ARM in by_arm:
        print_versus(by_arm)

    for title, key in (("task", task), ("framing", framing)):
        groups = sorted({key(run) for run in results})
        rows = [
            [
                group,
                *(
                    percent([bool(r.get("success")) for r in runs if key(r) == group])
                    for runs in by_arm.values()
                ),
            ]
            for group in groups
        ]
        print(f"\n## Pass rate by {title}\n")
        print(table([title.capitalize(), *by_arm], rows))

    reach = []
    for column in REACH_COLUMNS:
        row = [column]
        for runs in by_arm.values():
            values = [run.get("namedScores", {}).get(column, 0) for run in runs]
            is_count = column in COUNT_COLUMNS
            row.append(f"{mean(values):.1f}" if is_count else percent(values))
        reach.append(row)
    print("\n## Surfaces reached (share of runs; counts are per run)\n")
    print(table(["Column", *by_arm], reach))

    unknown = [
        [arm(run), run.get("testCase", {}).get("description", "?")]
        for run in results
        for component in (run.get("gradingResult") or {}).get("componentResults", [])
        if (component.get("reason") or "").startswith("UNKNOWN")
    ]
    if unknown:
        print("\n## Judge couldn't tell (passed as UNKNOWN, review by hand)\n")
        print(table(["Arm", "Case"], unknown))

    failures = Counter(
        run.get("testCase", {}).get("description", "?")
        for run in results
        if not run.get("success") and arm(run) != "baseline"
    )
    if failures:
        runs_per_case = Counter(
            (arm(run), run.get("testCase", {}).get("description")) for run in results
        )
        rows = []
        for case in sorted(failures):
            row = [case]
            for name in by_arm:
                failed = sum(
                    not run.get("success")
                    for run in by_arm[name]
                    if run.get("testCase", {}).get("description") == case
                )
                row.append(f"{failed}/{runs_per_case[(name, case)]}" if failed else "")
            rows.append(row)
        print("\n## Failed runs per case, outside the baseline\n")
        print(table(["Case", *by_arm], rows))


def summarize_proxy_log(path):
    entries = [json.loads(line) for line in Path(path).read_text().splitlines()]
    formats = Counter()
    for entry in entries:
        if entry["method"] != "GET":
            continue
        accept = (entry.get("accept") or "").split(",")[0].strip() or "(none)"
        served = (entry.get("content_type") or "").split(";")[0]
        formats[(entry.get("site", "full"), accept, served, entry["status"])] += 1
    print("\n## Guide requests seen by the proxy\n")
    print(
        f"{len(entries)} requests, "
        f"{sum(e['method'] == 'POST' and urlsplit(e['url']).path == '/mcp' for e in entries)} "
        "to the MCP server.\n"
    )
    print(
        table(
            ["Site", "First Accept type", "Served as", "Status", "GET requests"],
            [[*key, count] for key, count in sorted(formats.items())],
        )
    )


def main():
    parser = argparse.ArgumentParser(description="Summarize an agent readiness run.")
    parser.add_argument(
        "results", nargs="+", help="promptfoo JSON output, one file per repeat or run"
    )
    parser.add_argument(
        "--proxy-log", action="append", help="the proxy's requests.jsonl"
    )
    parser.add_argument(
        "--override",
        action="append",
        default=[],
        help="promptfoo JSON output whose arms replace the same arms in the results, "
        "like a rerun of one arm",
    )
    args = parser.parse_args()
    overrides = [result for path in args.override for result in load_results(path)]
    replaced = {arm(result) for result in overrides}
    results = [
        result
        for path in args.results
        for result in load_results(path)
        if arm(result) not in replaced
    ]
    summarize(results + overrides)
    for path in args.proxy_log or []:
        summarize_proxy_log(path)


if __name__ == "__main__":
    main()
