"""Observable retrieval friction and citation provenance, never inferred waste."""

from collections import Counter, defaultdict
from statistics import mean, median
from urllib.parse import urlsplit

from trace_analysis import csv_rows, urls

ERRORS = {"failed", "denied", "error_text"}
SEARCH = {"search", "mcp_search"}
METRICS = {
    "retrieval_calls": "Visible direct search/fetch or literal curl calls; not nested opaque actions.",
    "failed_retrieval_calls": "Retrieval calls with recorded failure, denial or recognized error text.",
    "unresolved_retrieval_calls": "Retrieval calls without a recognized return/error state.",
    "repeated_query_calls": "Search calls repeating the same tool and visible query from an earlier step; query truncated at 500 characters.",
    "repeated_target_calls": "Calls requesting at least one identical page from an earlier step, regardless of result.",
    "repeat_after_return_calls": "Calls requesting a page with an earlier returned fetch; not proof of redundancy.",
    "retry_after_error_calls": "Calls requesting a page with an earlier failed fetch; a recovery attempt, not necessarily waste.",
    "search_output_pages": "Unique URLs visible in returned search output, including snippets/navigation; not all necessarily ranked results.",
    "requested_pages": "Unique literal requested pages, regardless of status.",
    "returned_pages": "Unique page targets of returned calls; not proof of usable page content or HTTP success.",
    "returned_pages_not_cited": "Returned page targets absent from the final answer's URLs; useful background retrieval may be uncited.",
    "search_pages_requested_later": "Search-output pages requested in a strictly later step.",
    "search_pages_cited": "Search-output pages also named in the final answer.",
    "citation_pages": "Unique explicit HTTP(S) URL pages in the complete replayed answer.",
    "citations_returned": "Answer URL pages matching a returned fetch target; provenance only, not entailment.",
    "citations_search_only": "Answer URL pages visible in search output, with no matching returned fetch target.",
    "citations_other_output_only": "Answer URL pages visible only in other tool output, with no returned fetch or search match.",
    "citations_prompt_only": "Answer URL pages visible only in the prompt.",
    "citations_not_observed": "Answer URL pages absent from visible successful retrieval and prompt; not necessarily hallucinated.",
    "calls_before_reference_return": "Outer calls in steps before first returned fetch matching a frozen reference URL; URL-only proxy, null when no match.",
}


def page(url):
    """Keep versions and representations separate; no assumed redirects."""
    parsed = urlsplit(url)
    return (parsed.hostname or "").lower() + (parsed.path.rstrip("/") or "/")


def measure(record, events):
    identity = {
        key: record[key]
        for key in ("id", "phase", "harness", "model", "arm", "case", "passed")
    }
    row = {
        **identity,
        "trace_present": record["trace_present"],
        "answer_present": record["answer_present"],
        "opaque_calls": sum(e["kind"] == "opaque" for e in events),
        "native_calls_without_atif": record["native_calls_without_atif"],
        **dict.fromkeys(METRICS),
    }
    if not record["trace_present"]:
        return row, []
    counts = Counter()
    requested, returned, failed, queries = set(), set(), set(), set()
    search_pages, other_pages, search_followed = set(), set(), set()
    references = {page(u) for u in record["reference_urls"]}
    first_reference = None
    origins = defaultdict(list)
    for step in sorted({e["step"] for e in events}):
        group = [e for e in events if e["step"] == step]
        for event in group:
            targets = {page(u) for u in event["urls"]}
            retrieval = (
                event["kind"] in SEARCH | {"fetch", "mcp_fetch"}
                or event["curl_request"]
            )
            if retrieval:
                counts["retrieval_calls"] += 1
                counts["failed_retrieval_calls"] += event["status"] in ERRORS
                counts["unresolved_retrieval_calls"] += event["status"] not in (
                    ERRORS | {"returned"}
                )
            query = (event["tool"], event["query"].strip().lower())
            counts["repeated_query_calls"] += (
                event["kind"] in SEARCH and bool(query[1]) and query in queries
            )
            counts["repeated_target_calls"] += bool(targets & requested)
            counts["repeat_after_return_calls"] += bool(targets & returned)
            counts["retry_after_error_calls"] += bool(targets & failed)
            search_followed.update(targets & search_pages)
            if (
                first_reference is None
                and event["status"] == "returned"
                and targets & references
            ):
                first_reference = step
        # A same-step call cannot establish provenance for another same-step call.
        for event in group:
            targets = {page(u) for u in event["urls"]}
            requested.update(targets)
            if event["kind"] in SEARCH and event["query"]:
                queries.add((event["tool"], event["query"].strip().lower()))
            if event["status"] in ERRORS:
                failed.update(targets)
            if event["status"] != "returned":
                continue
            returned.update(targets)
            output = {page(u) for u in event["output_urls"]}
            (search_pages if event["kind"] in SEARCH else other_pages).update(output)
            for target in targets | output:
                origins[target].append(event["id"])
    for key in METRICS:
        row[key] = counts[key]
    row.update(
        search_output_pages=len(search_pages),
        requested_pages=len(requested),
        returned_pages=len(returned),
        search_pages_requested_later=len(search_followed),
        calls_before_reference_return=sum(e["step"] < first_reference for e in events)
        if first_reference is not None
        else None,
    )
    citation_rows = []
    answer_metrics = [k for k in METRICS if k.startswith("citation")]
    answer_metrics += ["returned_pages_not_cited", "search_pages_cited"]
    if not record["answer_present"]:
        row.update(dict.fromkeys(answer_metrics))
        return row, citation_rows
    citations = {page(u): u for u in record["answer_urls"]}
    prompt = {page(u) for u in urls(record["prompt"])}
    for target, url in sorted(citations.items()):
        provenance = (
            "returned"
            if target in returned
            else "search_only"
            if target in search_pages
            else "other_output_only"
            if target in other_pages
            else "prompt_only"
            if target in prompt
            else "not_observed"
        )
        row["citations_" + provenance] += 1
        citation_rows.append(
            {
                **identity,
                "url": url,
                "provenance": provenance,
                "evidence_events": " ".join(origins[target]),
                "semantic_support": "not_assessed",
                "opaque_calls": row["opaque_calls"],
            }
        )
    row.update(
        citation_pages=len(citations),
        returned_pages_not_cited=len(returned - citations.keys()),
        search_pages_cited=len(search_pages & citations.keys()),
    )
    return row, citation_rows


def summarize_retrieval(directory, records, events):
    by_trial = defaultdict(list)
    for event in events:
        by_trial[event["trial_id"]].append(event)
    rows, citations = [], []
    for record in records:
        row, links = measure(record, by_trial[record["id"]])
        rows.append(row)
        citations.extend(links)
    csv_rows(directory / "retrieval-trials.csv", rows)
    csv_rows(directory / "citation-provenance.csv", citations)
    csv_rows(
        directory / "retrieval-definitions.csv",
        [{"metric": key, "definition": value} for key, value in METRICS.items()],
    )
    groups = {("all", "all", "all", "all", "all"): rows}
    for row in rows:
        for key in (
            ("phase", row["phase"], "all", "all", "all"),
            ("arm", row["phase"], row["harness"], row["model"], row["arm"]),
        ):
            groups.setdefault(key, []).append(row)
    statistics = []
    for key, group in sorted(groups.items()):
        for metric in METRICS:
            values = [r[metric] for r in group if r[metric] is not None]
            n = len(values)
            statistics.append(
                {
                    **dict(zip(("scope", "phase", "harness", "model", "arm"), key)),
                    "metric": metric,
                    "attempts": len(group),
                    "eligible": n,
                    "unknown_or_no_match": len(group) - n,
                    "total": sum(values),
                    "traces_with_metric": sum(v > 0 for v in values),
                    "traces_with_metric_percent": 100 * sum(v > 0 for v in values) / n
                    if n
                    else None,
                    "mean_per_eligible_trace": mean(values) if n else None,
                    "median_per_eligible_trace": median(values) if n else None,
                }
            )
    csv_rows(directory / "retrieval-statistics.csv", statistics)
    return rows, citations, statistics
