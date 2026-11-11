"""Read-only Neuralwatt usage export and conservative historical task attribution."""

import argparse
import csv
import hashlib
import json
import logging
import math
import time
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta
from pathlib import Path
from statistics import mean, median
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import yaml

HERE = Path(__file__).resolve().parent
CACHE = Path.home() / ".cache/guide-agent-eval/harbor"
LOG = logging.getLogger(__name__)


def timestamp(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def load_trials(path: Path) -> list[dict]:
    return [
        r
        for line in path.read_text().splitlines()
        if (r := json.loads(line))["model"].startswith("neuralwatt/")
    ]


def save(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n")


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.unlink(missing_ok=True)
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fetch(args: argparse.Namespace) -> None:
    """Resumable complete pagination; credentials never enter files or logs."""
    trials = load_trials(args.trials)
    windows = defaultdict(list)
    for trial in trials:
        if interval := trial.get("agent_execution"):
            windows[trial["model"].split("/", 1)[1]].append(interval)
    key = yaml.safe_load(args.keys.read_text())["neuralwatt_keys"][
        "deepseek-v4.1-flash"
    ]
    args.cache.mkdir(parents=True, exist_ok=True)
    last_call = 0.0
    for model, intervals in sorted(windows.items()):
        # Include delayed accounting near timeouts, without assigning by time alone.
        start = datetime.fromtimestamp(
            min(timestamp(i["started_at"]) for i in intervals), UTC
        ) - timedelta(minutes=5)
        end = datetime.fromtimestamp(
            max(timestamp(i["finished_at"]) for i in intervals), UTC
        ) + timedelta(minutes=5)
        folder = args.cache / model
        folder.mkdir(exist_ok=True)
        query = {
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "model": model,
            "limit": 200,
        }
        if (folder / "query.json").exists():
            if json.loads((folder / "query.json").read_text()) != query:
                raise ValueError("Cached query differs; use a fresh cache directory")
        else:
            save(folder / "query.json", query)
        cursor, page = None, 0
        seen_cursors = set()
        while True:
            path = folder / f"page-{page:05d}.json"
            if path.exists():
                result = json.loads(path.read_text())
            else:
                parameters = {**query, **({"cursor": cursor} if cursor else {})}
                url = "https://api.neuralwatt.com/v1/usage/requests?" + urlencode(
                    parameters
                )
                for attempt in range(8):
                    time.sleep(max(0, 3.4 - (time.monotonic() - last_call)))
                    last_call = time.monotonic()
                    try:
                        with urlopen(
                            Request(url, headers={"Authorization": "Bearer " + key}),
                            timeout=60,
                        ) as response:
                            result = json.load(response)
                        break
                    except HTTPError as exc:
                        if exc.code not in (429, 500, 502, 503, 504):
                            raise RuntimeError(f"Usage API HTTP {exc.code}") from None
                        delay = float(exc.headers.get("Retry-After", 2**attempt))
                        LOG.warning("Usage API HTTP %s; waiting %.1fs", exc.code, delay)
                        time.sleep(delay)
                else:
                    raise RuntimeError("Usage API retries exhausted")
                save(path, result)
                LOG.info(
                    "%s page %s: %s requests", model, page, len(result["requests"])
                )
            if (
                timestamp(result["period"]["start"]) != start.timestamp()
                or timestamp(result["period"]["end"]) != end.timestamp()
            ):
                raise ValueError("API did not honor the requested UTC period")
            if result.get("cursor") != cursor:
                raise ValueError("Cached page cursor mismatch")
            if not result["has_more"]:
                save(folder / "complete.json", {"pages": page + 1, "query": query})
                break
            cursor = result["next_cursor"]
            if not cursor or cursor in seen_cursors:
                raise ValueError("Missing or repeated pagination cursor")
            seen_cursors.add(cursor)
            page += 1


def native_turns(trial: dict) -> list[dict]:
    """Only read content-free step-finish fields; never open credential databases."""
    path = Path(trial["trial_path"]).parent / "agent/opencode.txt"
    turns = {}
    if not path.exists():
        return []
    with path.open() as stream:
        for line in stream:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("type") != "step_finish":
                continue
            part = event.get("part") or {}
            tokens = part.get("tokens") or {}
            if not tokens or not event.get("timestamp"):
                continue
            cache = tokens.get("cache") or {}
            message = part.get("messageID") or part.get("id")
            if not message:
                continue
            turn = {
                "trial_id": trial["id"],
                "model": trial["model"].split("/", 1)[1],
                "timestamp": event["timestamp"] / 1000,
                "prompt_tokens": tokens.get("input", 0)
                + cache.get("read", 0)
                + cache.get("write", 0),
                "cached_tokens": cache.get("read", 0),
                "completion_tokens": tokens.get("output", 0)
                + tokens.get("reasoning", 0),
                "request_id": part.get("request_id"),
            }
            key = (event.get("sessionID"), message)
            if key in turns and turns[key] != turn:
                raise ValueError("Conflicting duplicate native token event")
            turns[key] = turn
    return list(turns.values())


def token_key(row: dict) -> tuple:
    return tuple(
        row.get(k) for k in ("prompt_tokens", "cached_tokens", "completion_tokens")
    )


def match_requests(
    turns: list[dict], requests: list[dict], tolerance: float = 3.0
) -> tuple[dict, dict]:
    """Accept only mutually unique joins; never split a request across tasks."""
    index = defaultdict(list)
    ids = {}
    for i, request in enumerate(requests):
        if request["request_id"] in ids:
            raise ValueError("Duplicate request ID")
        ids[request["request_id"]] = i
        index[(request["requested_model"], token_key(request))].append(i)
    candidates, owners = {}, defaultdict(list)
    for i, turn in enumerate(turns):
        if turn.get("request_id"):
            pool = [ids[turn["request_id"]]] if turn["request_id"] in ids else []
        else:
            pool = index[(turn["model"], token_key(turn))]
        compatible = [
            j
            for j in pool
            if requests[j]["requested_model"] == turn["model"]
            and token_key(requests[j]) == token_key(turn)
            and abs(timestamp(requests[j]["created_at"]) - turn["timestamp"])
            <= tolerance
        ]
        candidates[i] = compatible
        for j in compatible:
            owners[j].append(i)
    matches = {
        i: js[0]
        for i, js in candidates.items()
        if len(js) == 1 and len(owners[js[0]]) == 1
    }
    return matches, candidates


def energy(request: dict) -> tuple[float | None, str]:
    """Return reported Wh, preserving zero and separating estimates/missingness."""
    method = request.get("attribution_method") or "unknown"
    joules, kwh = request.get("energy_joules"), request.get("energy_kwh")
    value = (
        joules / 3600 if joules is not None else kwh * 1000 if kwh is not None else None
    )
    if value is None or not math.isfinite(value) or value < 0:
        return None, "missing"
    estimated = "estimated" in method or "fallback" in method or "compaction" in method
    return (
        value,
        "estimated"
        if estimated
        else "reported_non_estimate"
        if method != "unknown"
        else "unknown_method",
    )


def regime(request: dict) -> str:
    day = request["created_at"][:10]
    return (
        "pre_change"
        if day < "2026-11-06"
        else "change_day_uncertain"
        if day == "2026-11-06"
        else "post_change"
    )


def read_requests(cache: Path) -> list[dict]:
    rows = {}
    for folder in sorted(p for p in cache.iterdir() if p.is_dir()):
        complete = json.loads((folder / "complete.json").read_text())
        for page in range(complete["pages"]):
            data = json.loads((folder / f"page-{page:05d}.json").read_text())
            if page == complete["pages"] - 1 and data["has_more"]:
                raise ValueError("Incomplete usage pagination")
            for r in data["requests"]:
                previous = rows.setdefault(r["request_id"], r)
                if previous != r:
                    raise ValueError("Conflicting request records")
    return list(rows.values())


def other_trials(trials: list[dict]) -> list[dict]:
    """Other local executions compete for matches, but are not published as tasks."""
    known = {str(Path(t["trial_path"]).resolve()) for t in trials}
    extra = []
    for path in CACHE.glob("**/result.json"):
        if str(path.resolve()) in known:
            continue
        try:
            result = json.loads(path.read_text())
        except (ValueError, OSError):
            continue
        model = ((result.get("agent_info") or {}).get("model_info") or {}).get(
            "name", ""
        )
        if not model or not model.startswith("neuralwatt/"):
            continue
        extra.append(
            {
                "id": "outside:" + hashlib.sha256(str(path).encode()).hexdigest()[:16],
                "model": model,
                "trial_path": str(path),
                "agent_execution": result.get("agent_execution"),
            }
        )
    return extra


def cohort(trial: dict) -> tuple:
    return tuple(trial[k] for k in ("phase", "harness", "model", "arm"))


def window_assignments(
    trials: list[dict], requests: list[dict], assigned: set[int]
) -> tuple[list[dict], Counter]:
    """Illustrative time attribution; unknown account traffic remains a limitation."""
    windows = defaultdict(list)
    for trial in trials:
        interval = trial.get("agent_execution")
        if interval and interval.get("started_at") and interval.get("finished_at"):
            windows[trial["model"].split("/", 1)[1]].append(
                (
                    timestamp(interval["started_at"]),
                    timestamp(interval["finished_at"]),
                    trial,
                )
            )
    allocations, excluded = [], Counter()
    for j, request in enumerate(requests):
        if j in assigned:
            continue
        when = timestamp(request["created_at"])
        eligible = [
            trial
            for start, end, trial in windows[request["requested_model"]]
            if start <= when <= end
        ]
        if not eligible:
            excluded["no_eligible_window"] += 1
        elif any(t["id"].startswith("outside:") for t in eligible):
            excluded["outside_task_competes"] += 1
        elif len({cohort(t) for t in eligible}) > 1:
            excluded["different_cohorts_overlap"] += 1
        else:
            allocations.append(
                {
                    "request_index": j,
                    "trace_id": eligible[0]["id"] if len(eligible) == 1 else "",
                    "cohort": cohort(eligible[0]),
                    "eligible_tasks": len(eligible),
                    "match_method": "time_only"
                    if len(eligible) == 1
                    else "group_only_time",
                }
            )
    return allocations, excluded


def analyze(args: argparse.Namespace) -> None:
    trials = load_trials(args.trials)
    requests = read_requests(args.cache)
    extras = other_trials(trials)
    LOG.info(
        "Attributing %s usage rows to %s inventory tasks; %s outside tasks compete",
        len(requests),
        len(trials),
        len(extras),
    )
    turns = [turn for trial in trials + extras for turn in native_turns(trial)]
    matches, candidates = match_requests(turns, requests)
    by_trial, allocations = defaultdict(list), []
    for i, turn in enumerate(turns):
        by_trial[turn["trial_id"]].append(i)
        if i not in matches or turn["trial_id"].startswith("outside:"):
            continue
        r = requests[matches[i]]
        wh, kind = energy(r)
        allocations.append(
            {
                "trace_id": turn["trial_id"],
                "request_fingerprint": hashlib.sha256(
                    r["request_id"].encode()
                ).hexdigest()[:16],
                "match_method": "request_id_tokens_time"
                if turn.get("request_id") == r["request_id"]
                else "unique_model_tokens_time",
                "finish_delta_seconds": round(
                    turn["timestamp"] - timestamp(r["created_at"]), 6
                ),
                **{
                    k: r[k]
                    for k in ("prompt_tokens", "cached_tokens", "completion_tokens")
                },
                "energy_wh": wh,
                "energy_kind": kind,
                "attribution_method": r.get("attribution_method"),
                "reporting_regime": regime(r),
            }
        )
    # Remaining account traffic is never silently assigned using timestamps alone.
    unassigned = defaultdict(list)
    allocated_indices = set(matches.values())
    for j, r in enumerate(requests):
        if j not in allocated_indices:
            unassigned[r["requested_model"]].append(timestamp(r["created_at"]))
    for times in unassigned.values():
        times.sort()
    window_matches, window_excluded = window_assignments(
        trials + extras, requests, allocated_indices
    )
    window_ledger, time_by_task = [], defaultdict(list)
    for match in window_matches:
        request = requests[match["request_index"]]
        wh, kind = energy(request)
        row = {
            "trace_id": match["trace_id"],
            "request_fingerprint": hashlib.sha256(
                request["request_id"].encode()
            ).hexdigest()[:16],
            **dict(
                zip(("phase", "harness", "model", "arm"), match["cohort"], strict=True)
            ),
            "match_method": match["match_method"],
            "eligible_tasks": match["eligible_tasks"],
            "energy_wh": wh,
            "energy_kind": kind,
            "attribution_method": request.get("attribution_method"),
            "reporting_regime": regime(request),
        }
        window_ledger.append(row)
        if row["trace_id"]:
            time_by_task[row["trace_id"]].append(row)
    rows = []
    for trial in trials:
        indices = by_trial[trial["id"]]
        matched = [requests[matches[i]] for i in indices if i in matches]
        energies = [energy(r) for r in matched]
        values = [wh for wh, _ in energies if wh is not None]
        regimes = sorted({regime(r) for r in matched})
        interval = trial.get("agent_execution")
        times = unassigned[trial["model"].split("/", 1)[1]]
        unmatched_window = (
            bisect_right(times, timestamp(interval["finished_at"]) + 2)
            - bisect_left(times, timestamp(interval["started_at"]) - 2)
            if interval
            else None
        )
        covered = (
            bool(indices)
            and len(matched) == len(indices)
            and len(values) == len(matched)
            and unmatched_window == 0
            and not trial["execution_error"]
        )
        time_values = [
            r["energy_wh"]
            for r in time_by_task[trial["id"]]
            if r["energy_wh"] is not None
        ]
        rows.append(
            {
                **{
                    k: trial[k]
                    for k in (
                        "id",
                        "phase",
                        "harness",
                        "model",
                        "arm",
                        "case",
                        "passed",
                        "execution_error",
                    )
                },
                "reporting_regime": "+".join(regimes) or "unknown",
                "recorded_turns": len(indices),
                "matched_requests": len(matched),
                "ambiguous_turns": sum(
                    i not in matches and bool(candidates[i]) for i in indices
                ),
                "unmatched_turns": sum(not candidates[i] for i in indices),
                "unassigned_account_requests_in_window": unmatched_window,
                "energy_requests": len(values),
                "reported_non_estimate_requests": sum(
                    k == "reported_non_estimate" for _, k in energies
                ),
                "estimated_requests": sum(k == "estimated" for _, k in energies),
                "missing_energy_requests": sum(k == "missing" for _, k in energies),
                "attributed_energy_wh": sum(values) if values else None,
                "time_only_requests": len(time_by_task[trial["id"]]),
                "time_only_energy_wh": sum(time_values) if time_values else None,
                "matched_plus_time_energy_wh": sum(values + time_values)
                if values or time_values
                else None,
                "covered_task": covered,
                "covered_task_energy_wh": sum(values) if covered else None,
            }
        )
    grouped = defaultdict(list)
    for row in rows:
        for key in (
            (
                "cohort",
                row["phase"],
                row["harness"],
                row["model"],
                row["arm"],
                "all-regimes-illustrative",
            ),
            (
                "regime",
                row["phase"],
                row["harness"],
                row["model"],
                row["arm"],
                row["reporting_regime"],
            ),
        ):
            grouped[key].append(row)
    stats = []
    for key, group in sorted(grouped.items()):
        complete = [
            r["covered_task_energy_wh"]
            for r in group
            if r["covered_task_energy_wh"] is not None
        ]
        known = [
            r["attributed_energy_wh"]
            for r in group
            if r["attributed_energy_wh"] is not None
        ]
        passes = sum(r["passed"] for r in group)
        stats.append(
            {
                **dict(
                    zip(
                        (
                            "scope",
                            "phase",
                            "harness",
                            "model",
                            "arm",
                            "reporting_regime",
                        ),
                        key,
                        strict=True,
                    )
                ),
                "attempts": len(group),
                "passes": passes,
                "attempts_with_attributed_energy": len(known),
                "covered_tasks": len(complete),
                "partial_or_unknown_tasks": len(group) - len(complete),
                "matched_requests": sum(r["matched_requests"] for r in group),
                "estimated_requests": sum(r["estimated_requests"] for r in group),
                "missing_energy_requests": sum(
                    r["missing_energy_requests"] for r in group
                ),
                "attributed_total_wh": sum(known) if known else None,
                "mean_attributed_attempt_wh": mean(known) if known else None,
                "median_attributed_attempt_wh": median(known) if known else None,
                "covered_total_wh": sum(complete) if complete else None,
                "mean_covered_task_wh": mean(complete) if complete else None,
                "median_covered_task_wh": median(complete) if complete else None,
                "partial_attributed_wh_per_published_pass": sum(known) / passes
                if passes and known
                else None,
            }
        )
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "ENERGY_TRIALS.csv", rows)
    write_csv(args.output / "ENERGY_GROUPS.csv", stats)
    write_csv(args.output / "ENERGY_REQUESTS.csv", allocations)
    write_csv(args.output / "ENERGY_WINDOW_REQUESTS.csv", window_ledger)
    batches, window_by_cohort = defaultdict(list), defaultdict(list)
    for row in rows:
        batches[cohort(row)].append(row)
    for row in window_ledger:
        window_by_cohort[cohort(row)].append(row)
    window_stats = []
    for key, group in sorted(batches.items()):
        strict_values = [
            r["attributed_energy_wh"]
            for r in group
            if r["attributed_energy_wh"] is not None
        ]
        supplement = window_by_cohort[key]
        timed = [
            r["energy_wh"]
            for r in supplement
            if r["match_method"] == "time_only" and r["energy_wh"] is not None
        ]
        grouped_values = [
            r["energy_wh"]
            for r in supplement
            if r["match_method"] == "group_only_time" and r["energy_wh"] is not None
        ]
        values = strict_values + timed + grouped_values
        total = sum(values) if values else None
        window_stats.append(
            {
                **dict(zip(("phase", "harness", "model", "arm"), key, strict=True)),
                "attempts": len(group),
                "strict_matched_requests": sum(r["matched_requests"] for r in group),
                "strict_attributed_wh": sum(strict_values) if strict_values else None,
                "time_only_requests": sum(
                    r["match_method"] == "time_only" for r in supplement
                ),
                "time_only_wh": sum(timed) if timed else None,
                "group_only_requests": sum(
                    r["match_method"] == "group_only_time" for r in supplement
                ),
                "group_only_wh": sum(grouped_values) if grouped_values else None,
                "window_attributed_total_wh": total,
                "mean_window_attributed_wh_per_attempt": total / len(group)
                if total is not None
                else None,
                "strict_fraction_of_window_attributed_wh": sum(strict_values) / total
                if total
                else None,
                "estimated_requests": sum(r["estimated_requests"] for r in group)
                + sum(r["energy_kind"] == "estimated" for r in supplement),
                "missing_energy_requests": sum(
                    r["missing_energy_requests"] for r in group
                )
                + sum(r["energy_kind"] == "missing" for r in supplement),
            }
        )
    write_csv(args.output / "ENERGY_WINDOW_GROUPS.csv", window_stats)
    summary = {
        "trials_sha256": hashlib.sha256(args.trials.read_bytes()).hexdigest(),
        "inventory_tasks": len(trials),
        "outside_competing_tasks": len(extras),
        "usage_requests": len(requests),
        "native_turns": sum(r["recorded_turns"] for r in rows),
        "matched_inventory_requests": len(allocations),
        "matched_outside_requests": sum(
            turns[i]["trial_id"].startswith("outside:") for i in matches
        ),
        "unassigned_account_requests": len(requests) - len(allocated_indices),
        "covered_tasks": sum(r["covered_task"] for r in rows),
        "tasks_with_energy": sum(r["attributed_energy_wh"] is not None for r in rows),
        "attributed_total_wh": sum(r["energy_wh"] or 0 for r in allocations),
        "methods": dict(Counter(r["attribution_method"] for r in allocations)),
        "kinds": dict(Counter(r["energy_kind"] for r in allocations)),
        "regimes": dict(Counter(r["reporting_regime"] for r in allocations)),
        "exact_id_matches": sum(
            r["match_method"] == "request_id_tokens_time" for r in allocations
        ),
        "window_supplement_requests": len(window_ledger),
        "window_supplement_methods": dict(
            Counter(r["match_method"] for r in window_ledger)
        ),
        "window_supplement_wh": sum(r["energy_wh"] or 0 for r in window_ledger),
        "window_unallocated": dict(window_excluded),
    }
    save(args.cache / "attribution-summary.json", summary)
    LOG.info("%s", json.dumps(summary))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("fetch", "analyze"))
    parser.add_argument(
        "--trials",
        type=Path,
        default=CACHE / "trace-analysis-followups-2026-11-11/trials.jsonl",
    )
    parser.add_argument("--cache", type=Path, default=CACHE / "energy-2026-11-11")
    parser.add_argument("--keys", type=Path, default=Path.home() / "dev/.keys.yml")
    parser.add_argument("--output", type=Path, default=HERE)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if args.action == "fetch":
        fetch(args)
    else:
        analyze(args)


if __name__ == "__main__":
    main()
