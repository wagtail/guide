"""Existing cases -> Harbor jobs -> existing Promptfoo graders."""

import argparse
import copy
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from fnmatch import fnmatch
from importlib.metadata import version
from pathlib import Path
from urllib.request import Request, urlopen

import yaml
from harbor.models.job.config import JobConfig

SCRIPTS = Path(__file__).resolve().parent
HERE = SCRIPTS.parent
SOURCE = HERE.parent / "agent-readiness"
CACHE = Path.home() / ".cache/guide-agent-eval/harbor"
sys.path.insert(0, str(SOURCE / "graders"))
from check_cases import check


def read(path):
    return yaml.safe_load(Path(path).read_text())


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def source_hash():
    files = [SOURCE / "tests.yaml", SOURCE / "default-test.yaml"]
    files += sorted((SOURCE / "graders").glob("*.py"))
    return hashlib.sha256(b"".join(p.read_bytes() for p in files)).hexdigest()


def credentials(entry, keys):
    """Load only the selected provider's credential; never serialize values."""
    result = {}
    for name, path in entry["credentials"].items():
        value = keys
        for component in path:
            value = value.get(component, {}) if isinstance(value, dict) else None
        value = os.environ.get(name) or value
        if name == "TAVILY_API_KEY" and not value:
            # Read only a literal assignment, without executing the shell file.
            extra = Path.home() / ".extra"
            for line in extra.read_text().splitlines() if extra.exists() else []:
                line = line.strip().removeprefix("export ").strip()
                if line.startswith("TAVILY_API_KEY="):
                    parts = shlex.split(line, comments=True)
                    if len(parts) != 1 or any(c in parts[0] for c in ("$", "`")):
                        raise ValueError("TAVILY_API_KEY must be a literal assignment")
                    value = parts[0].split("=", 1)[1]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Missing {name} for {entry['id']}")
        result[name] = value
    return result


def catalog():
    request = Request(
        "https://api.neuralwatt.com/v1/models",
        headers={"User-Agent": "guide-agent-readiness/1.0"},
    )
    with urlopen(request, timeout=30) as response:
        return {m["id"]: m for m in json.load(response)["data"]}


def latest_version(harness):
    urls = {
        "claude-code": "https://registry.npmjs.org/@anthropic-ai/claude-code/latest",
        "codex": "https://registry.npmjs.org/@openai/codex/latest",
        "opencode": "https://registry.npmjs.org/opencode-ai/latest",
        "vibe": "https://pypi.org/pypi/mistral-vibe/json",
    }
    if harness == "cursor-cli":
        # Harbor's Cursor installer always installs latest, ignoring version.
        # Leave it unset so Harbor records the actually installed version.
        return None
    with urlopen(
        Request(urls[harness], headers={"User-Agent": "guide-agent-readiness/1.0"}),
        timeout=30,
    ) as response:
        data = json.load(response)
    return data.get("version") or data["info"]["version"]


def agent_config(entry, arm, pricing):
    kwargs = copy.deepcopy(
        {
            **entry.get("kwargs", {}),
            **read(HERE / "config/arms.yaml")[entry["harness"]][arm],
        }
    )
    agent = {
        "name": entry["harness"],
        "model_name": entry["model"],
        "env": {key: "${" + key + "}" for key in entry["credentials"]},
        "kwargs": kwargs,
    }
    agent["env"].update(entry.get("env", {}))
    if arm == "native+mcp":
        agent["mcp_servers"] = [
            {
                "name": "wagtail-guide",
                "transport": "streamable-http",
                "url": "https://guide.wagtail.org/mcp",
            }
        ]
    extension = {
        ("claude-code", "baseline"): "NoToolsClaude",
        ("claude-code", "web"): "WebClaude",
        ("vibe", "baseline"): "NoToolsVibe",
        ("vibe", "native"): "CurrentVibe",
        ("vibe", "native+mcp"): "CurrentVibe",
    }.get((entry["harness"], arm))
    if extension:
        agent.pop("name")
        agent["import_path"] = f"tool_controls:{extension}"
    if entry["harness"] == "vibe":
        agent["include_logs"] = ["vibe.txt", "vibe-export/export.json"]
    if entry.get("version"):
        kwargs["version"] = entry["version"]
    if entry["harness"] == "opencode":
        model = entry["model"].split("/", 1)[1]
        config = kwargs.setdefault("opencode_config", {})
        config.update({"autoupdate": False, "share": "disabled"})
        config["provider"] = {
            "neuralwatt": {
                "npm": "@ai-sdk/openai-compatible",
                "name": "Neuralwatt",
                "options": {
                    "baseURL": "https://api.neuralwatt.com/v1",
                    "apiKey": "{env:NEURALWATT_API_KEY}",
                },
                "models": {
                    model: {
                        "name": model,
                        **({"cost": pricing} if pricing is not None else {}),
                    }
                },
            }
        }
        agent["env"]["OPENCODE_ENABLE_EXA"] = "1"
        agent["env"]["OPENCODE_WEBSEARCH_PROVIDER"] = "exa"
        if entry.get("search_provider") == "tavily":
            if "TAVILY_API_KEY" not in entry["credentials"]:
                raise ValueError("Tavily search requires a TAVILY_API_KEY credential")
            if arm == "baseline":
                raise ValueError("Tavily search cannot be enabled in a no-tools arm")
            # OpenCode v1 has no built-in Tavily provider. Use its native remote
            # MCP configuration; Harbor 0.25 drops MCP headers at the top level.
            config.setdefault("mcp", {})["tavily"] = {
                "type": "remote",
                "url": "https://mcp.tavily.com/mcp/",
                "oauth": False,
                "headers": {"Authorization": "Bearer {env:TAVILY_API_KEY}"},
            }
            permissions = {"websearch": False}
            permissions.update(
                {
                    f"tavily_tavily_{tool}": tool == "search"
                    for tool in ("search", "extract", "crawl", "map", "research")
                }
            )
            config.setdefault("tools", {}).update(permissions)
            config.setdefault("permission", {}).update(
                {
                    tool: "allow" if enabled else "deny"
                    for tool, enabled in permissions.items()
                }
            )
            agent["env"].pop("OPENCODE_ENABLE_EXA")
            agent["env"].pop("OPENCODE_WEBSEARCH_PROVIDER")
    return agent


def prepare(args):
    if problems := check():
        raise ValueError("\n".join(problems))
    entries = [
        e
        for e in read(args.matrix)["entries"]
        if fnmatch(e["id"], args.entry)
        and (args.entry != "*" or e.get("default", True))
    ]
    cases = [
        c
        for c in read(SOURCE / "tests.yaml")
        if any(fnmatch(c["description"], pattern) for pattern in args.case.split(","))
    ]
    if not entries or not cases:
        raise ValueError("No matching entries or cases")
    remote = catalog() if any(e["harness"] == "opencode" for e in entries) else {}
    versions = {
        h: latest_version(h)
        for h in sorted({e["harness"] for e in entries if not e.get("version")})
    }
    for entry in entries:
        entry.setdefault("version", versions.get(entry["harness"]))
    root = args.directory.resolve()
    if root.is_relative_to(HERE.parents[2]):
        raise ValueError(
            "Keep generated tasks, jobs and answers outside the repository"
        )
    root.mkdir(parents=True, exist_ok=False)
    tasks = root / "tasks"
    for case in cases:
        task = tasks / case["description"]
        (task / "environment").mkdir(parents=True)
        (task / "instruction.md").write_text(case["vars"]["prompt"])
        (task / "task.toml").write_text(
            'version = "1.0"\n[agent]\ntimeout_sec = '
            + str(args.timeout)
            + "\n[environment]\ncpus = 1\nmemory_mb = 2048\n"
        )
        (task / "environment/Dockerfile").write_text(
            "FROM node:26-bookworm-slim\nENV UV_PYTHON=3.12\nRUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv curl git procps unzip ca-certificates && rm -rf /var/lib/apt/lists/*\nWORKDIR /workspace\n"
        )
    jobs, unavailable = [], []
    for entry in entries:
        pricing = None
        if entry["harness"] == "opencode":
            model = entry["model"].split("/", 1)[1]
            if model not in remote:
                if not entry.get("allow_unlisted_model"):
                    raise ValueError(f"Model not in Neuralwatt catalog: {model}")
                print(f"Preview model {model}: candidate pricing is unknown")
            else:
                price = remote[model]["metadata"]["pricing"]
                pricing = {
                    "input": price["input_per_million"],
                    "output": price["output_per_million"],
                    "cache_read": price["cached_input_per_million"],
                }
        for arm in args.arms.split(","):
            if arm not in read(HERE / "config/arms.yaml")[entry["harness"]]:
                unavailable.append(
                    f"{entry['id']}/{arm}: unsupported by this Harbor integration"
                )
                continue
            name = f"{entry['id']}--{arm}"
            config = {
                "job_name": name,
                "jobs_dir": str(root / "jobs"),
                "n_attempts": args.repeat,
                "n_concurrent_trials": args.concurrency,
                "retry": {"max_retries": 0},
                "environment": {"type": "docker"},
                "verifier": {"disable": True},
                "agents": [agent_config(entry, arm, pricing)],
                "datasets": [{"path": str(tasks)}],
            }
            JobConfig.model_validate(config)
            write(root / f"{name}.json", config)
            jobs.append({"name": name, "entry": entry, "arm": arm, "pricing": pricing})
    write(
        root / "manifest.json",
        {
            "created_at": datetime.now(UTC).isoformat(),
            "harbor_version": version("harbor"),
            "source_hash": source_hash(),
            "cases": cases,
            "repeat": args.repeat,
            "jobs": jobs,
            "unavailable": unavailable,
        },
    )
    print(
        f"Prepared {len(jobs)} jobs × {len(cases)} cases × {args.repeat} repeats at {root}"
    )
    for item in unavailable:
        print(item)


def run(args):
    root = args.directory.resolve()
    manifest = read(root / "manifest.json")
    keys = read(args.keys)
    jobs = [j for j in manifest["jobs"] if fnmatch(j["name"], args.job)]
    if not jobs:
        raise ValueError("No matching jobs")
    # Validate every selected credential before starting any paid runs.
    secrets = [credentials(j["entry"], keys) for j in jobs]
    for job, auth in zip(jobs, secrets, strict=True):
        env = {
            k: v
            for k, v in os.environ.items()
            if not any(s in k.upper() for s in ("KEY", "TOKEN", "SECRET", "PASSWORD"))
        }
        env.update(auth)
        env["PYTHONPATH"] = str(SCRIPTS)
        subprocess.run(
            ["harbor", "run", "--config", str(root / f"{job['name']}.json")],
            env=env,
            check=True,
        )


def grade(args):
    root = args.directory.resolve()
    manifest = read(root / "manifest.json")
    if manifest["source_hash"] != source_hash():
        raise ValueError(
            "Cases or graders changed since prepare; restore them before grading"
        )
    defaults = read(SOURCE / "default-test.yaml")
    defaults["assert"][-1]["value"] = f"file://{SCRIPTS / 'replay.py'}:get_assert"
    tests = []
    cases = {c["description"]: c for c in manifest["cases"]}
    for job in manifest["jobs"]:
        for result in sorted((root / "jobs" / job["name"]).glob("*/result.json")):
            trial = read(result)
            case = copy.deepcopy(cases[trial["task_name"]])
            case["vars"].update({"trial_path": str(result), "arm": job["arm"]})
            case["metadata"].update(
                {"job": job["name"], "arm": job["arm"], "entry": job["entry"]["id"]}
            )
            case["description"] = f"{job['name']}/{trial['trial_name']}"
            tests.append(case)
    if not tests:
        raise ValueError("No Harbor trial results to grade")
    write(
        root / "grading.json",
        {
            "description": "Harbor agent readiness (replayed answers)",
            "prompts": ["{{prompt}}"],
            "providers": [f"file://{SCRIPTS / 'replay.py'}"],
            "defaultTest": defaults,
            "tests": tests,
            "evaluateOptions": {"maxConcurrency": 3},
        },
    )
    (root / "empty").mkdir(exist_ok=True)
    modules = root / "node_modules"
    if not modules.exists():
        modules.symlink_to(HERE.parents[2] / "node_modules", target_is_directory=True)
    env = {
        **os.environ,
        "EVAL_AGENTS_FIXTURES": str(root),
        "PROMPTFOO_PYTHON": sys.executable,
    }
    env.update(
        credentials(
            {
                "id": "judge",
                "credentials": {"ANTHROPIC_API_KEY": ["ANTHROPIC_API_KEY"]},
            },
            read(args.keys),
        )
    )
    result = subprocess.run(
        [
            "npx",
            "promptfoo",
            "eval",
            "-c",
            str(root / "grading.json"),
            "--no-cache",
            "--output",
            str(root / "grades.json"),
        ],
        env=env,
    )
    if result.returncode not in (0, 100):
        raise subprocess.CalledProcessError(result.returncode, result.args)


def doctor(args):
    keys = read(args.keys)
    for entry in read(args.matrix)["entries"]:
        try:
            credentials(entry, keys)
            status = "credential available"
        except ValueError as error:
            status = str(error)
        print(f"{entry['id']}: {entry['model']} — {status}")
    print("Docker:", shutil.which("docker") or "missing")
    print(
        "Promptfoo SDK:",
        "installed"
        if (HERE.parents[2] / "node_modules/@anthropic-ai/claude-agent-sdk").exists()
        else "run just eval-agents-init",
    )
    if shutil.which("cursor-agent"):
        models = subprocess.run(
            ["cursor-agent", "--list-models"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        for line in models.stdout.splitlines():
            if any(name in line.lower() for name in ("grok-4.7", "argon", "wonder")):
                print(line)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=["doctor", "prepare", "run", "grade", "report"]
    )
    parser.add_argument("directory", nargs="?", type=Path, default=CACHE / "experiment")
    parser.add_argument("--keys", type=Path, default=Path.home() / "dev/.keys.yml")
    parser.add_argument("--matrix", type=Path, default=HERE / "config/matrix.yaml")
    parser.add_argument("--entry", default="*")
    parser.add_argument("--case", default="*", help="Comma-separated case name globs")
    parser.add_argument("--job", default="*")
    parser.add_argument("--arms", default="native,baseline")
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--concurrency", type=int, default=1)
    args = parser.parse_args()
    if min(args.repeat, args.timeout, args.concurrency) < 1:
        parser.error("repeat, timeout and concurrency must be positive")
    if args.command == "report":
        from report import report

        report(args.directory)
    else:
        {"doctor": doctor, "prepare": prepare, "run": run, "grade": grade}[
            args.command
        ](args)


if __name__ == "__main__":
    main()
