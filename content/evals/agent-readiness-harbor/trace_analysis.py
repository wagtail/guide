"""Offline trace inventory and native Harbor semantic review; no candidate reruns."""

import argparse
import csv
import hashlib
import json
import re
import shlex
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from urllib.parse import urlsplit, urlunsplit

from replay import guide_mcp_call
from report import seconds
from runner import CACHE, HERE, read

sys.path.insert(0, str(HERE.parent / "agent-readiness/graders"))
from trace_columns import URL_PATTERN, normalize_url, surface

ALIASES = {
    "WebSearch": "search",
    "websearch": "search",
    "webSearchToolCall": "search",
    "connector_web_search.web_search": "search",
    "web_search": "search",
    "WebFetch": "fetch",
    "webfetch": "fetch",
    "webFetchToolCall": "fetch",
    "connector_web_search.open_url": "fetch",
    "web_fetch": "fetch",
    "Bash": "shell",
    "bash": "shell",
    "shellToolCall": "shell",
    "exec_command": "shell",
    "shell_command": "shell",
    "file_system.bash": "shell",
    "Read": "local",
    "read": "local",
    "Grep": "local",
    "grep": "local",
    "Glob": "local",
    "glob": "local",
    "grepToolCall": "local",
    "readToolCall": "local",
    "globToolCall": "local",
    "ToolSearch": "discovery",
    "getMcpToolsToolCall": "discovery",
    "search_tool_functions": "discovery",
    "Agent": "delegate",
    "Task": "delegate",
    "task": "delegate",
    "exec": "opaque",
    "js_repl": "opaque",
}
ERROR = re.compile(
    r"^(?:Error\b|StatusCode:|Request failed|Permission denied|code-mode host is disabled)",
    re.I,
)
SECRET = re.compile(
    r'(?i)(?:bearer\s+[\w.~+/-]+=*|sk-[\w-]{16,}|(?:api[_-]?key|token|password)\s*[:=]\s*["\']?[^\s,"\'}]+)'
)


def load(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n")


def jsonl(path, values):
    with path.open("w") as f:
        for value in values:
            f.write(json.dumps(value, ensure_ascii=True) + "\n")


def text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(p.get("text", "") for p in value if isinstance(p, dict))
    return json.dumps(value) if value is not None else ""


def clean(value, limit=1000):
    value = text(value)
    for raw in URL_PATTERN.findall(value):
        safe = urls(raw)
        value = value.replace(raw, safe[0] if safe else "[INVALID URL]")
    return SECRET.sub("[REDACTED]", value)[:limit]


def sanitized(value):
    """Sanitize leaves before JSON serialization, preserving structure and types."""
    if isinstance(value, dict):
        return {key: sanitized(v) for key, v in value.items()}
    if isinstance(value, list):
        return [sanitized(v) for v in value]
    return clean(value, len(value) + 100) if isinstance(value, str) else value


def curl_targets(command):
    """Conservatively recognize literal curl operands, not header/echo URLs."""
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return [], False
    groups, group = [], []
    for token in tokens + [";"]:
        if token and all(c in ";&|" for c in token):
            groups.append(group)
            group = []
        else:
            group.append(token)
    takes_value = {
        "-H",
        "--header",
        "-A",
        "--user-agent",
        "-o",
        "--output",
        "-d",
        "--data",
        "--data-raw",
        "--data-binary",
        "--data-urlencode",
        "-u",
        "--user",
        "-x",
        "--proxy",
        "-e",
        "--referer",
        "-w",
        "--write-out",
        "--connect-timeout",
        "--max-time",
        "-m",
        "--retry",
        "--cacert",
        "--cert",
        "--key",
        "-X",
        "--request",
        "--resolve",
        "-b",
        "--cookie",
        "-c",
        "--cookie-jar",
    }
    targets, found = [], False
    no_value = {
        "--silent",
        "--show-error",
        "--fail",
        "--location",
        "--head",
        "--insecure",
        "--compressed",
        "--include",
        "--globoff",
        "--no-buffer",
    }
    for group in groups:
        if not group or group[0] != "curl":
            continue
        found = True
        if "\n" in command:
            continue
        group_targets = []
        index = 1
        while index < len(group):
            token = group[index]
            if token in takes_value:
                index += 2
                continue
            if token == "--url" and index + 1 < len(group):
                index += 1
                token = group[index]
            if token.startswith(("http://", "https://")):
                group_targets.extend(urls(token))
            elif token.startswith("--url="):
                group_targets.extend(urls(token.split("=", 1)[1]))
            elif (
                token.startswith("-")
                and token not in no_value
                and not (
                    token.startswith("-")
                    and not token.startswith("--")
                    and set(token[1:]) <= set("sSIfLkNig")
                )
            ):
                # Unknown options may consume a following URL as data.
                return [], True
            index += 1
        targets.extend(group_targets)
    return list(dict.fromkeys(targets)), found


def local_command(command):
    """Lower-bound detection of workspace commands, excluding curl pipelines."""
    if curl_targets(command)[1]:
        return False
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return False
    return any(
        token in ("ls", "pwd", "find", "rg", "grep", "cat")
        and (index == 0 or tokens[index - 1] in (";", "&&", "||"))
        for index, token in enumerate(tokens)
    )


def urls(value):
    if isinstance(value, dict):
        return list(dict.fromkeys(u for v in value.values() for u in urls(v)))
    if isinstance(value, list):
        return list(dict.fromkeys(u for v in value for u in urls(v)))
    if isinstance(value, str) and value.lstrip().startswith(("{", "[")):
        try:
            return urls(json.loads(value))
        except ValueError:
            pass
    found = []
    for raw in URL_PATTERN.findall(text(value).replace("\\/", "/")):
        try:
            p = urlsplit(raw.rstrip(".,;:}\\"))
            if p.hostname:
                # Query strings, userinfo and fragments may contain credentials.
                found.append(urlunsplit((p.scheme, p.hostname, p.path or "/", "", "")))
        except ValueError:
            continue
    return list(dict.fromkeys(found))


def status(observation, native=None):
    if native:
        return (
            "failed"
            if native == "error"
            else "returned"
            if native == "completed"
            else "unobserved"
        )
    if observation is None:
        return "unobserved"
    extra = observation.get("extra") or {}
    raw = (extra.get("tool_result_metadata") or {}).get("raw_tool_result") or {}
    if extra.get("tool_result_is_error") or (
        isinstance(raw, dict) and raw.get("is_error")
    ):
        return "failed"
    body = text(observation.get("content"))
    try:
        obj = json.loads(body)
    except (ValueError, TypeError):
        obj = {}
    if isinstance(obj, dict):
        if obj.get("success") is False:
            return "failed"
        if obj.get("status") in ("error", "failed", "denied") or obj.get("error"):
            return "failed"
        if obj.get("decision") in ("deny", "denied"):
            return "denied"
        if obj.get("status") == "completed" or "success" in obj:
            return "returned"
    if ERROR.match(body.strip()):
        return "error_text"
    return "returned" if body.strip() else "unobserved"


def opencode_statuses(trial):
    """Supplement missing ATIF error states, without reading credential databases."""
    path = trial / "agent/opencode.txt"
    result = {}
    if path.exists():
        for line in path.open():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("type") == "tool_use":
                part = event.get("part") or {}
                if part.get("callID"):
                    result[part["callID"]] = (part.get("state") or {}).get("status")
    return result


def extract_events(steps, trial_id, native=None):
    observations = {
        o["source_call_id"]: o
        for s in steps
        for o in (s.get("observation") or {}).get("results", [])
        if o.get("source_call_id")
    }
    result, seen = [], set()
    for step in steps:
        for index, call in enumerate(step.get("tool_calls") or []):
            cid = call["tool_call_id"]
            if cid in seen:
                continue
            seen.add(cid)
            args = call.get("arguments") or {}
            if not isinstance(args, dict):
                args = {"unparsed": text(args)}
            name = call["function_name"]
            resolved_name, args = guide_mcp_call(name, args)
            kind = ALIASES.get(name, "other")
            if name == "web_search_call":
                kind = "fetch" if args.get("url") else "search"
            if (
                resolved_name.endswith(("__search_docs", "_search_docs"))
                or name == "tavily_tavily_search"
            ):
                kind = "mcp_search"
            if resolved_name.endswith(("__fetch_docs_page", "_fetch_docs_page")):
                kind = "mcp_fetch"
            obs = observations.get(cid)
            state = status(obs, (native or {}).get(cid))
            command = text(args.get("command") or args.get("cmd") or args.get("input"))
            shell_targets, is_curl = (
                curl_targets(command) if kind == "shell" else ([], False)
            )
            targets = (
                urls(args.get("url", "")) if kind in ("fetch", "mcp_fetch") else []
            )
            if (
                kind == "mcp_fetch"
                and resolved_name.removeprefix("mcp__").startswith(
                    ("wagtail-guide_", "wagtail_guide_")
                )
                and str(args.get("url", "")).startswith("/")
            ):
                targets = urls("https://guide.wagtail.org" + args["url"])
            if kind == "shell":
                targets = shell_targets
            body = text((obs or {}).get("content"))
            try:
                state_body = json.loads(body)
            except ValueError:
                state_body = {}
            discovery = (
                state_body.get("output", {}) if isinstance(state_body, dict) else {}
            )
            query = (
                args.get("query")
                or args.get("searchTerm")
                or args.get("search_term")
                or ""
            )
            result.append(
                {
                    "id": f"{trial_id}:s{step['step_id']}:{index}",
                    "trial_id": trial_id,
                    "step": step["step_id"],
                    "call_id": cid,
                    "tool": name,
                    "kind": kind,
                    "status": state,
                    "observation_present": obs is not None,
                    "query": clean(query, 500),
                    "urls": targets,
                    "surfaces": [surface(u) for u in targets],
                    "output_urls": urls(body) if state == "returned" else [],
                    "output_characters": len(body),
                    "discovery_tool_count": discovery.get("toolCount")
                    if isinstance(discovery, dict)
                    else None,
                    "discovery_connector_count": discovery.get("connectorNoticeCount")
                    if isinstance(discovery, dict)
                    else None,
                    "script_search_request": kind == "opaque"
                    and bool(re.search(r"search_query\s*:|web_?search\s*\(", command)),
                    "script_fetch_request": kind == "opaque"
                    and bool(re.search(r"\bopen\s*:|web_?fetch\s*\(", command)),
                    "script_urls": urls(command) if kind == "opaque" else [],
                    "curl_request": is_curl,
                    "shell_targets_unresolved": is_curl and not targets,
                    "local_inspection": kind == "local"
                    or (kind == "shell" and local_command(command)),
                    "markdown_requested": (
                        name == "webfetch"
                        and args.get("format", "markdown") == "markdown"
                    )
                    or (kind == "shell" and "text/markdown" in command),
                    "argument_excerpt": clean(command, 800)
                    if kind in ("shell", "opaque")
                    else "",
                    "error_signal": clean(body, 180)
                    if state in ("failed", "denied", "error_text")
                    else "",
                }
            )
    return result


def techniques(events, prompt):
    flags = Counter()
    seen, search_seen = set(), set()
    prompt_urls = {normalize_url(u) for u in urls(prompt)}
    queries, fetched = set(), set()
    previous_failure = False
    origins = {}
    search_origins = {}
    by_id = {e["id"]: e for e in events}
    for step in sorted({e["step"] for e in events}):
        group = [e for e in events if e["step"] == step]
        flags["parallel_tool_group"] |= len(group) > 1
        for e in group:
            flags["search_requested"] |= (
                e["kind"] in ("search", "mcp_search") or e["script_search_request"]
            )
            flags["script_search_requested"] |= e["script_search_request"]
            flags["script_fetch_requested"] |= e["script_fetch_request"]
            flags["fetch_requested"] |= bool(e["urls"]) or e["script_fetch_request"]
            flags["opaque_calls"] |= e["kind"] == "opaque"
            flags["local_inspection"] |= e["local_inspection"]
            flags["curl_requested"] |= e["curl_request"]
            flags["shell_targets_unresolved"] |= e["shell_targets_unresolved"]
            flags["markdown_requested"] |= e["markdown_requested"]
            flags["delegation_requested"] |= e["kind"] == "delegate"
            flags["mcp_requested"] |= e["kind"].startswith("mcp_")
            flags["tool_error"] |= e["status"] in ("failed", "denied", "error_text")
            flags["missing_observations"] |= not e["observation_present"]
            flags["continued_after_error"] |= previous_failure
            if e["query"]:
                q = e["query"].lower().strip()
                flags["repeated_query"] |= q in queries
                queries.add(q)
            for u in e["urls"]:
                key = normalize_url(u)
                source_id = search_origins.get(key) or origins.get(key)
                source_urls = (
                    by_id[source_id]["output_urls"] if source_id else urls(prompt)
                )
                e.setdefault("url_provenance", []).append(
                    {
                        "url": u,
                        "origin": "earlier_search_output"
                        if key in search_seen
                        else "earlier_tool_output"
                        if key in seen
                        else "prompt"
                        if key in prompt_urls
                        else "not_visible",
                        "source_event": source_id,
                        "match": "exact_sanitized_url"
                        if u in source_urls
                        else "normalized_page"
                        if key in seen | prompt_urls
                        else None,
                    }
                )
                flags[surface(u) + "_requested"] = 1
                flags["visible_link_following"] |= key in seen
                flags["search_result_following"] |= key in search_seen
                flags["url_not_previously_visible"] |= key not in seen | prompt_urls
                flags["repeated_fetch"] |= key in fetched
                fetched.add(key)
        # Calls listed in the same step may run concurrently. Only earlier steps
        # establish visible-link provenance, never an arbitrary within-step order.
        for e in group:
            visible = {normalize_url(u) for u in e["output_urls"]}
            seen.update(visible)
            for key in visible:
                origins.setdefault(key, e["id"])
            if e["kind"] in ("search", "mcp_search"):
                search_seen.update(visible)
                for key in visible:
                    search_origins.setdefault(key, e["id"])
        previous_failure |= any(
            e["status"] in ("failed", "denied", "error_text") for e in group
        )
    flags["multiple_queries"] = len(queries) > 1
    navigation = [
        e
        for e in events
        if e["kind"] in ("search", "fetch", "mcp_search", "mcp_fetch", "opaque")
        or e["urls"]
    ]
    first = (
        [e for e in navigation if e["step"] == navigation[0]["step"]]
        if navigation
        else []
    )
    flags["mixed_first_navigation"] = (
        len(first) > 1 and len({(e["kind"], tuple(e["surfaces"])) for e in first}) > 1
    )
    flags["search_first"] = bool(first) and all(
        e["kind"] in ("search", "mcp_search") for e in first
    )
    flags["homepage_first"] = bool(first) and all(
        e["surfaces"] == ["homepage"] for e in first
    )
    flags["no_observed_calls"] = not events
    return {k: bool(v) for k, v in flags.items()}


def controls(config):
    kwargs = config["agent"].get("kwargs") or {}
    allowed = (
        "allowed_tools",
        "disallowed_tools",
        "permission_mode",
        "append_system_prompt",
        "web_search",
    )
    result = {k: kwargs[k] for k in allowed if k in kwargs}
    if config["agent"].get("mcp_servers"):
        result["mcp_servers"] = [
            {k: server[k] for k in ("name", "transport", "url") if k in server}
            for server in config["agent"]["mcp_servers"]
        ]
    for name, keys in [
        ("config", ("developer_instructions", "features", "tools")),
        ("opencode_config", ("permission", "tools")),
    ]:
        if isinstance(kwargs.get(name), dict):
            result[name] = {k: kwargs[name][k] for k in keys if k in kwargs[name]}
    return result


def csv_rows(path, rows):
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def grouped(records, fields, features):
    groups = defaultdict(list)
    for record in records:
        groups[tuple(record[f] for f in fields)].append(record)
    result = []
    for key, group in sorted(groups.items()):
        visible = [r for r in group if r["trace_present"]]
        timings = [r["agent_seconds"] for r in group if r["agent_seconds"] is not None]
        result.append(
            {
                **dict(zip(fields, key, strict=True)),
                "attempts": len(group),
                "traces_present": len(visible),
                "passes": sum(r["passed"] for r in group),
                "median_agent_seconds": median(timings) if timings else None,
                **{
                    f: sum(r["techniques"].get(f, False) for r in visible)
                    for f in features
                },
            }
        )
    return result


def extract(args):
    args.output.mkdir(parents=True, exist_ok=True)
    records, all_events, instructions, seen = [], [], {}, set()
    for source in read(args.config)["sources"]:
        root = Path(source["path"]).expanduser().resolve()
        roots = (
            [root]
            if (root / "manifest.json").exists()
            else [Path(j["directory"]) for j in load(root / "plan.json")["jobs"]]
        )
        for directory in roots:
            manifest = load(directory / "manifest.json")
            cases = {c["description"]: c for c in manifest["cases"]}
            jobs = {j["name"]: j for j in manifest["jobs"]}
            for grade in load(directory / "grades.json")["results"]["results"]:
                path = Path(grade["testCase"]["vars"]["trial_path"]).resolve()
                if path in seen:
                    raise ValueError(f"Duplicate trial input: {path}")
                seen.add(path)
                result = load(path)
                trial_id = hashlib.sha256(str(path).encode()).hexdigest()[:16]
                name = grade["testCase"]["metadata"]["job"]
                job, case = jobs[name], cases[result["task_name"]]
                trace = path.parent / "agent/trajectory.json"
                steps = load(trace)["steps"] if trace.exists() else []
                events = extract_events(
                    steps,
                    trial_id,
                    opencode_statuses(path.parent)
                    if job["entry"]["harness"] == "opencode"
                    else None,
                )
                flags = (
                    techniques(events, case["vars"]["prompt"]) if trace.exists() else {}
                )
                system = [text(s["message"]) for s in steps if s["source"] == "system"]
                instruction = {
                    "arm": job["arm"],
                    "controls": controls(result["config"]),
                    "agent_implementation": result["config"]["agent"].get("import_path")
                    or result["config"]["agent"].get("name"),
                    "system_visibility": "recorded" if system else "not_recorded",
                    "recorded_system_messages": system,
                }
                ihash = hashlib.sha256(
                    json.dumps(instruction, sort_keys=True).encode()
                ).hexdigest()
                instructions[ihash] = instruction
                system_excerpt = "\n".join(
                    line
                    for message in system
                    for line in message.splitlines()
                    if re.search(
                        r"brows|search|tools?|documentation|internet", line, re.I
                    )
                )
                source_path = manifest.get("retry_sources", {}).get(
                    result["config"]["task"]["source"]
                )
                answer = next(
                    (
                        text(s["message"])
                        for s in reversed(steps)
                        if s["source"] == "agent"
                        and not s.get("tool_calls")
                        and text(s["message"])
                    ),
                    "",
                )
                record = {
                    "id": trial_id,
                    "trial_path": str(path),
                    "phase": source["phase"],
                    "original_trial": str(Path(source_path).resolve())
                    if source_path
                    else None,
                    "job": name,
                    "harness": job["entry"]["harness"],
                    "model": job["entry"]["model"],
                    "arm": job["arm"],
                    "case": result["task_name"],
                    "framing": case["metadata"]["framing"],
                    "task_type": case["metadata"]["task"],
                    "prompt": case["vars"]["prompt"],
                    "passed": bool(grade["success"]),
                    "grade_error": clean(
                        (grade.get("response") or {}).get("error", "")
                    ),
                    "execution_error": (result.get("exception_info") or {}).get(
                        "exception_type"
                    ),
                    "agent_seconds": seconds(result.get("agent_execution")),
                    "candidate_cost_usd": (result.get("agent_result") or {}).get(
                        "cost_usd"
                    ),
                    "trace_present": trace.exists(),
                    "event_count": len(events),
                    "instruction_hash": ihash,
                    "system_visibility": instruction["system_visibility"],
                    "agent_implementation": instruction["agent_implementation"],
                    "controls": instruction["controls"],
                    "recorded_system_excerpt": clean(system_excerpt, 4000),
                    "system_excerpt_truncated": len(system_excerpt) > 4000,
                    "answer_excerpt": clean(answer, 1200),
                    "techniques": flags,
                    "tool_counts": dict(Counter(e["tool"] for e in events)),
                    "status_counts": dict(Counter(e["status"] for e in events)),
                }
                records.append(record)
                all_events.extend(events)
    jsonl(args.output / "trials.jsonl", records)
    jsonl(args.output / "events.jsonl", all_events)
    # Full recorded instructions remain local; semantic staging uses excerpts.
    jsonl(
        args.output / "instructions.jsonl",
        [{"hash": k, **v} for k, v in instructions.items()],
    )
    features = sorted({f for r in records for f in r["techniques"]})
    for name, fields in [
        ("by-arm", ["phase", "harness", "model", "arm"]),
        ("by-framing", ["phase", "harness", "model", "arm", "framing"]),
        ("by-case", ["phase", "harness", "model", "arm", "case"]),
    ]:
        csv_rows(args.output / (name + ".csv"), grouped(records, fields, features))
    originals = {r["trial_path"]: r for r in records if r["phase"] == "initial"}
    pairs = []
    for record in records:
        if record["phase"] != "retry":
            continue
        original = originals[record["original_trial"]]
        assert (
            not original["passed"]
            and original["case"] == record["case"]
            and original["job"] == record["job"]
            and original["prompt"] == record["prompt"]
            and original["model"] == record["model"]
        )
        pairs.append(
            {
                "initial_id": original["id"],
                "retry_id": record["id"],
                "job": record["job"],
                "recovered": record["passed"],
                "both_traces_present": original["trace_present"]
                and record["trace_present"],
                "added_techniques": [
                    f
                    for f in features
                    if record["techniques"].get(f) and not original["techniques"].get(f)
                ],
                "removed_techniques": [
                    f
                    for f in features
                    if original["techniques"].get(f) and not record["techniques"].get(f)
                ],
            }
        )
    assert len({p["initial_id"] for p in pairs}) == len(pairs)
    jsonl(args.output / "retry-pairs.jsonl", pairs)
    dump(
        args.output / "inventory.json",
        {
            "attempts": len(records),
            "phases": dict(Counter(r["phase"] for r in records)),
            "traces_present": sum(r["trace_present"] for r in records),
            "events": len(all_events),
            "instruction_profiles": len(instructions),
            "source_config": str(args.config.resolve()),
            "retry_pairs": len(pairs),
            "features": features,
        },
    )
    print(
        f"Extracted {len(records)} attempts, {len(all_events)} tool events, {len(pairs)} retry pairs into {args.output}"
    )
    from trace_report import summarize

    summarize(args.output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=HERE / "trace-sources.yaml")
    parser.add_argument("--output", type=Path, default=CACHE / "trace-analysis")
    args = parser.parse_args()
    extract(args)


if __name__ == "__main__":
    main()
