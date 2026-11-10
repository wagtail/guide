"""Replay ATIF answers into the original graders without calling candidates."""

import json
import sys
from pathlib import Path


def get_assert(output, context):
    # Normal import avoids Promptfoo's Python 3.12 dataclass loader bug.
    sys.path.insert(
        0, str(Path(__file__).resolve().parent.parent / "agent-readiness/graders")
    )
    from trace_columns import get_assert as original

    response = context.get("providerResponse") or {}
    metadata = response.get("metadata") or {}
    calls = metadata.get("toolCalls", [])
    tavily = any(c.get("name") == "tavily_tavily_search" for c in calls)
    if tavily:
        # Keep raw call identities in the saved replay; translate only the
        # existing trace grader's input. Answer assertions remain unchanged.
        context = {
            **context,
            "providerResponse": {
                **response,
                "metadata": {
                    **metadata,
                    "toolCalls": [
                        {**c, "name": "websearch"}
                        if c.get("name") == "tavily_tavily_search"
                        else c
                        for c in calls
                    ],
                },
            },
        }
    result = original(output, context)
    if tavily:
        result["named_scores"]["mcp_used"] = 1.0
    # Code-mode scripts can hide nested actions; don't imply full trace coverage.
    result["named_scores"]["opaque_tool_calls"] = sum(
        c.get("name") in ("exec", "js_repl") for c in calls
    )
    return result


def text(content):
    if isinstance(content, str):
        return content
    return "\n".join(
        p.get("text", "") for p in content or [] if p.get("type") == "text"
    )


def guide_mcp_call(name, arguments):
    """Resolve Cursor's wrapper using its recorded server/tool identifiers."""
    if (
        name == "mcpToolCall"
        and arguments.get("serverIdentifier") == "wagtail-guide"
        and arguments.get("toolName") in ("search_docs", "fetch_docs_page")
        and isinstance(arguments.get("args"), dict)
    ):
        return f"mcp__wagtail-guide__{arguments['toolName']}", arguments["args"]
    return name, arguments


def normalize(call):
    """Use the existing Claude trace vocabulary for other Harbor agents."""
    aliases = {
        "webFetchToolCall": "WebFetch",
        "webSearchToolCall": "WebSearch",
        "shellToolCall": "Bash",
        "bash": "Bash",
        "exec_command": "Bash",
        "shell_command": "Bash",
        "shell": "Bash",
        "web_fetch": "WebFetch",
        "web_search": "WebSearch",
        "connector_web_search.web_search": "WebSearch",
    }
    call = {**call, "input": dict(call["input"])}
    call["name"], call["input"] = guide_mcp_call(call["name"], call["input"])
    call["name"] = aliases.get(call["name"], call["name"])
    if call["name"] == "web_search_call":
        call["name"] = "WebFetch" if call["input"].get("url") else "WebSearch"
    if call["name"] == "Bash" and "command" not in call["input"]:
        call["input"]["command"] = call["input"].get("cmd", "")
    return call


def empty_vibe_discovery(call):
    """Vibe retains discovery even when every usable tool is disabled."""
    if call["name"] != "search_tool_functions":
        return False
    try:
        state = json.loads(call["output"])
        output = state["output"]
        return (
            state["status"] == "completed"
            and output["toolCount"] == 0
            and output["connectorNoticeCount"] == 0
            and not state.get("outputText")
        )
    except (ValueError, KeyError, TypeError):
        return False


def call_api(prompt, options, context):
    result_path = Path(context["vars"]["trial_path"])
    result = json.loads(result_path.read_text())
    if result.get("exception_info"):
        return {"error": result["exception_info"]["exception_type"]}
    path = result_path.parent / "agent/trajectory.json"
    if not path.exists():
        return {"error": "Harbor did not produce an ATIF trajectory"}
    steps = json.loads(path.read_text())["steps"]
    last = next(
        (
            s
            for s in reversed(steps)
            if s["source"] == "agent" and (s.get("tool_calls") or text(s["message"]))
        ),
        {},
    )
    if last.get("tool_calls"):
        return {"error": "Trajectory ended with a tool call, without a final answer"}
    answer = next(
        (
            text(s["message"])
            for s in reversed(steps)
            if s["source"] == "agent" and not s.get("tool_calls") and text(s["message"])
        ),
        "",
    )
    outputs = {
        r["source_call_id"]: text(r.get("content"))
        for s in steps
        for r in (s.get("observation") or {}).get("results", [])
        if r.get("source_call_id")
    }
    calls = [
        {
            "name": c["function_name"],
            "input": c["arguments"],
            "output": outputs.get(c["tool_call_id"], ""),
        }
        for s in steps
        for c in s.get("tool_calls") or []
    ]
    harness = result["agent_info"]["name"]
    if context["vars"].get("arm") == "baseline" and any(
        not (harness == "vibe" and empty_vibe_discovery(c)) for c in calls
    ):
        return {"error": f"Invalid no-tools arm: observed {len(calls)} tool calls"}
    if harness != "opencode":
        calls = [normalize(c) for c in calls]
    if (
        harness == "codex"
        and context["vars"].get("arm") == "web"
        and any(c["name"] not in ("WebSearch", "WebFetch") for c in calls)
    ):
        return {"error": "Invalid Codex web-only arm: observed non-web tool calls"}
    usage = result.get("agent_result") or {}
    response = {"output": answer, "metadata": {"harness": harness, "toolCalls": calls}}
    if usage.get("cost_usd") is not None:
        response["cost"] = usage["cost_usd"]
    return response
