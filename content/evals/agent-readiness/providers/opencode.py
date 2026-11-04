"""
Promptfoo provider: run one OpenCode session per test, headless.

Runs `opencode run --format json` in a fresh empty directory, with a config
written from the provider's `config`, and turns OpenCode's JSON events into a
promptfoo response. Tool calls go in `metadata.toolCalls` with
`metadata.harness = "opencode"`, so `graders/trace_columns.py` can read them.

promptfoo's own OpenCode provider doesn't return tool calls, which the trace
columns need, so this one runs the CLI directly.

Provider config:
- `model`: `provider/model`, like `openai/gpt-5.4-mini`.
- `tools`: OpenCode tool names to allow, like `[webfetch, websearch]`.
  Everything else is denied.
- `mcp`: OpenCode `mcp` config, for arms with an MCP server.
- `env`: extra environment variables, like `HTTPS_PROXY` for the plain site.
- `run_timeout`: seconds before the run is stopped (default 300). OpenCode
  retries some provider errors without giving up, like a used-up free model
  quota. promptfoo's own `timeout`, in milliseconds, must be longer.
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import tempfile
from pathlib import Path
from typing import Any

DEFAULT_TIMEOUT = 300


def opencode_config(config: dict[str, Any]) -> dict[str, Any]:
    """The OpenCode config for one run: deny everything but the arm's tools."""
    permission: dict[str, str] = {"*": "deny"}
    for tool in config.get("tools") or []:
        permission[tool] = "allow"
    result: dict[str, Any] = {
        "$schema": "https://opencode.ai/config.json",
        "autoupdate": False,
        "share": "disabled",
        "permission": permission,
    }
    if config.get("mcp"):
        result["mcp"] = config["mcp"]
    return result


def parse_events(lines: list[str]) -> dict[str, Any]:
    """Collect the answer, tool calls, cost and errors from OpenCode's events."""
    tool_calls = []
    step_text: list[str] = []
    answer = ""
    cost = 0.0
    tokens = {"prompt": 0, "completion": 0, "total": 0}
    errors = []
    for line in lines:
        line = line.strip()
        if not line.startswith("{"):
            continue
        event = json.loads(line)
        part = event.get("part") or {}
        kind = event.get("type")
        if kind == "step_start":
            step_text = []
        elif kind == "text":
            step_text.append(part.get("text") or "")
            # The answer is the text of the last step that wrote any.
            answer = "".join(step_text)
        elif kind == "tool_use":
            state = part.get("state") or {}
            tool_calls.append(
                {
                    "name": part.get("tool", ""),
                    "input": state.get("input") or {},
                    "output": state.get("output") or state.get("error") or "",
                    "is_error": state.get("status") == "error",
                }
            )
        elif kind == "step_finish":
            cost += part.get("cost") or 0
            usage = part.get("tokens") or {}
            cache = usage.get("cache") or {}
            prompt = (usage.get("input") or 0) + (cache.get("read") or 0)
            completion = (usage.get("output") or 0) + (usage.get("reasoning") or 0)
            tokens["prompt"] += prompt
            tokens["completion"] += completion
            tokens["total"] += prompt + completion
        elif kind == "error":
            error = event.get("error") or {}
            errors.append((error.get("data") or {}).get("message") or json.dumps(error))
    return {
        "answer": answer.strip(),
        "tool_calls": tool_calls,
        "cost": cost,
        "tokens": tokens,
        "errors": errors,
    }


def opencode_binary() -> str:
    binary = os.environ.get("EVAL_AGENTS_OPENCODE") or shutil.which("opencode")
    if not binary:
        raise RuntimeError("OpenCode not found - run `just eval-agents-init`")
    return binary


def call_api(
    prompt: str, options: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    config = options.get("config") or {}
    fixtures = Path(os.environ["EVAL_AGENTS_FIXTURES"])
    timeout = config.get("run_timeout", DEFAULT_TIMEOUT)
    with tempfile.TemporaryDirectory(dir=fixtures, prefix="opencode-") as run_dir:
        run_dir = Path(run_dir)
        workdir = run_dir / "empty"
        workdir.mkdir()
        config_path = run_dir / "opencode.json"
        config_path.write_text(json.dumps(opencode_config(config)))
        env = {
            **os.environ,
            # Keep OpenCode away from your own config, sessions and plugins.
            # The model list cache is shared between runs.
            "XDG_CONFIG_HOME": str(run_dir / "config"),
            "XDG_DATA_HOME": str(run_dir / "data"),
            "XDG_STATE_HOME": str(run_dir / "state"),
            "XDG_CACHE_HOME": str(fixtures / "opencode-cache"),
            "OPENCODE_CONFIG": str(config_path),
            "OPENCODE_DISABLE_AUTOUPDATE": "1",
            # Exa search, so every run uses the same search backend.
            "OPENCODE_ENABLE_EXA": "1",
            "OPENCODE_WEBSEARCH_PROVIDER": "exa",
            **{key: str(value) for key, value in (config.get("env") or {}).items()},
        }
        command = [
            opencode_binary(),
            "run",
            "--format",
            "json",
            "--pure",
            "--model",
            config["model"],
            prompt,
        ]
        process = subprocess.Popen(
            command,
            cwd=workdir,
            env=env,
            # `opencode run` reads the message from stdin when it isn't a
            # terminal, and waits for it.
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
            result = parse_events(stdout.splitlines())
            return {"error": f"OpenCode timed out after {timeout}s", **metadata(result)}
    result = parse_events(stdout.splitlines())
    if result["errors"] or not result["answer"]:
        message = "; ".join(result["errors"]) or stderr.strip()[-500:] or "no answer"
        return {"error": f"OpenCode: {message}", **metadata(result)}
    return {"output": result["answer"], **metadata(result)}


def metadata(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "cost": result["cost"],
        "tokenUsage": result["tokens"],
        "metadata": {"harness": "opencode", "toolCalls": result["tool_calls"]},
    }
