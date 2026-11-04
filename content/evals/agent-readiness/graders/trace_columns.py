"""
Promptfoo assertion: record which agent readiness surfaces a run reached.

Reads the agent's tool calls from the provider response, classifies each into a
surface of the guide (llms.txt, Markdown mirror, MCP, agent skill, ...) and
returns them as named scores, so the promptfoo viewer and `summarize.py` can
report reach rates per arm. Column names follow the ora.ai / Vercel dataset
(https://github.com/agentready-org/standard/blob/main/data/traces.csv) where a
column exists there, so our numbers can be read next to theirs.

The assertion always passes: it measures what the agent did, not whether the
path was right. Give it `weight: 0` in the config so it doesn't affect scores.

Each agent harness names its tools differently. `normalize_claude` turns the
Claude Agent SDK's `toolCalls` into plain `Call`s; other harnesses only need
their own adapter.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

GUIDE_HOST = "guide.wagtail.org"
DEV_DOCS_HOST = "docs.wagtail.org"
# The guide's content copy is public on GitHub. Fetching it bypasses the site.
GITHUB_COPY = re.compile(
    r"^(github\.com|raw\.githubusercontent\.com)/wagtail/guide(/|$)", re.IGNORECASE
)
# Versioned guide URLs, like /en-4.2.x/ or /en-latest/. Search engines still
# return them, and they redirect to the current page.
VERSIONED_PATH = re.compile(r"^/([a-z]{2}(-[a-z]{2})?)-(\d+\.\d+\.x|latest)/")
# The editor manual that used to live in the developer docs, before the guide.
LEGACY_EDITOR_MANUAL = re.compile(r"docs\.wagtail\.org/\S*editor_manual")
URL_PATTERN = re.compile(r"https?://[^\s\"'<>()\[\]`]+")
LLMS_TXT = Path(__file__).resolve().parents[3] / "en" / "llms.txt"


@dataclass
class Call:
    """One tool call, independent of the agent harness."""

    kind: str  # "fetch", "search", "mcp_search", "mcp_fetch", "other"
    url: str = ""
    output: str = ""
    markdown_requested: bool = False
    error: bool = False


def normalize_claude(tool_calls: list[dict[str, Any]]) -> list[Call]:
    """Turn Claude Agent SDK `metadata.toolCalls` into `Call`s."""
    calls = []
    for tool_call in tool_calls:
        name = tool_call.get("name", "")
        tool_input = tool_call.get("input") or {}
        output = str(tool_call.get("output") or "")
        error = bool(tool_call.get("is_error"))
        if name == "WebFetch":
            calls.append(Call("fetch", tool_input.get("url", ""), output, error=error))
        elif name == "WebSearch":
            calls.append(Call("search", output=output))
        elif name.endswith("__search_docs"):
            calls.append(Call("mcp_search", output=output))
        elif name.endswith("__fetch_docs_page"):
            url = tool_input.get("url", "")
            if url.startswith("/"):
                url = f"https://{GUIDE_HOST}{url}"
            calls.append(Call("mcp_fetch", url, output, error=error))
        elif name == "Bash":
            command = tool_input.get("command", "")
            markdown = "text/markdown" in command
            calls.extend(
                Call("fetch", url, output, markdown_requested=markdown)
                for url in URL_PATTERN.findall(command)
            )
        else:
            calls.append(Call("other", output=output))
    return calls


def normalize_url(url: str) -> str:
    """Reduce a guide URL to its page, so HTML and Markdown URLs match."""
    parts = urlsplit(url.strip().rstrip(".,;:"))
    path = VERSIONED_PATH.sub(r"/\1/", parts.path or "/")
    path = path.removesuffix("/markdown/").removesuffix("/markdown")
    path = path.rstrip("/") + "/"
    return f"{parts.hostname or ''}{path}"


def surface(url: str) -> str:
    """Classify a URL into one of the surfaces we report on."""
    parts = urlsplit(url)
    host = parts.hostname or ""
    path = parts.path or "/"
    if host == DEV_DOCS_HOST:
        return "dev_docs"
    if GITHUB_COPY.match(f"{host}{path}"):
        return "github_copy"
    if host != GUIDE_HOST:
        return "external"
    if path in ("/", "/en/", "/en"):
        return "homepage"
    if path == "/llms.txt":
        return "llms_txt"
    if path == "/llms-full.txt":
        return "llms_full"
    if path.startswith("/.well-known/agent-skills"):
        return "skill"
    if path.startswith("/.well-known/"):
        return "well_known"
    if path == "/sitemap.xml":
        return "sitemap"
    if path == "/robots.txt":
        return "robots_txt"
    if path == "/openapi.json" or path.startswith("/api/"):
        return "openapi"
    if path == "/mcp":
        return "mcp_endpoint_path"
    if path.startswith("/search"):
        return "site_search"
    if path.rstrip("/").endswith("/markdown") or path.endswith(".md"):
        return "markdown_page"
    return "docs_page"


def llms_txt_listing() -> set[str]:
    """Pages listed in the versioned copy of llms.txt."""
    if not LLMS_TXT.exists():
        return set()
    return {normalize_url(url) for url in URL_PATTERN.findall(LLMS_TXT.read_text())}


def analyze(calls: list[Call], answer: str) -> dict[str, float]:
    """Compute the trace columns for one run."""
    fetches = [call for call in calls if call.kind in ("fetch", "mcp_fetch")]
    surfaces = [surface(call.url) for call in fetches]
    reached = set(surfaces)
    first_fetch = surfaces[0] if surfaces else ""

    def linked(target: str) -> int:
        """Times a URL of this surface was fetched after appearing in an output."""
        count = 0
        seen: set[str] = set()
        for call in calls:
            is_fetch = call.kind in ("fetch", "mcp_fetch")
            if is_fetch and surface(call.url) == target:
                count += normalize_url(call.url) in seen
            seen.update(normalize_url(url) for url in URL_PATTERN.findall(call.output))
        return count

    listing = llms_txt_listing()
    followed_listing = 0.0
    if "llms_txt" in reached:
        after = surfaces.index("llms_txt")
        followed_listing = float(
            any(normalize_url(call.url) in listing for call in fetches[after + 1 :])
        )

    fetched_pages = {normalize_url(call.url) for call in fetches}
    cited = [
        url
        for url in URL_PATTERN.findall(answer)
        if urlsplit(url).hostname == GUIDE_HOST
    ]
    cited_fetched = [url for url in cited if normalize_url(url) in fetched_pages]

    def is_versioned(url: str) -> bool:
        parts = urlsplit(url)
        return parts.hostname == GUIDE_HOST and bool(VERSIONED_PATH.match(parts.path))

    return {
        "homepage_reached": float("homepage" in reached),
        "docs_reached": float(bool({"docs_page", "markdown_page"} & reached)),
        "markdown_page_reached": float("markdown_page" in reached),
        "llms_txt_reached": float("llms_txt" in reached),
        "llms_full_reached": float("llms_full" in reached),
        "skill_reached": float("skill" in reached),
        "well_known_reached": float("well_known" in reached),
        "sitemap_reached": float("sitemap" in reached),
        "openapi_reached": float("openapi" in reached),
        "robots_txt_reached": float("robots_txt" in reached),
        "github_copy_reached": float("github_copy" in reached),
        "dev_docs_reached": float("dev_docs" in reached),
        "external_reached": float("external" in reached),
        "web_search_used": float(any(c.kind == "search" for c in calls)),
        "mcp_used": float(any(c.kind.startswith("mcp_") for c in calls)),
        "homepage_first_turn": float(first_fetch == "homepage"),
        "llms_txt_linked": float(linked("llms_txt")),
        "markdown_page_linked": float(linked("markdown_page")),
        "skill_linked": float(linked("skill")),
        "llms_followed_listing": followed_listing,
        "answer_cites_guide": float(bool(cited)),
        # As in the ora.ai dataset: the answer traces to a page the run fetched.
        "answer_grounded": float(bool(cited_fetched)),
        "citations_not_fetched": float(len(cited) - len(cited_fetched)),
        "versioned_url_reached": float(any(is_versioned(c.url) for c in fetches)),
        "answer_cites_versioned_url": float(any(is_versioned(url) for url in cited)),
        "legacy_editor_manual_reached": float(
            any(LEGACY_EDITOR_MANUAL.search(c.url) for c in fetches)
        ),
        "answer_cites_legacy_editor_manual": float(
            bool(LEGACY_EDITOR_MANUAL.search(answer))
        ),
        "tool_calls": float(len(calls)),
        "fetch_errors": float(sum(c.error for c in fetches)),
        "web_fetch_calls": float(sum(c.kind == "fetch" for c in calls)),
        "docs_pages_fetched": float(
            sum(s in ("docs_page", "markdown_page") for s in surfaces)
        ),
    }


def get_assert(output: str, context: dict[str, Any]) -> dict[str, Any]:
    metadata = (context.get("providerResponse") or {}).get("metadata") or {}
    tool_calls = metadata.get("toolCalls") or []
    calls = normalize_claude(tool_calls)
    columns = analyze(calls, output or "")
    # Shell use, for arms that allow curl: commands run, and commands refused
    # because they weren't plain curl.
    columns["curl_calls"] = float(
        sum(
            t.get("name") == "Bash"
            and "curl" in (t.get("input") or {}).get("command", "")
            for t in tool_calls
        )
    )
    columns["permission_denials"] = float(len(metadata.get("permissionDenials") or []))
    reached = sorted(
        name.removesuffix("_reached")
        for name, value in columns.items()
        if name.endswith("_reached") and value
    )
    return {
        "pass": True,
        "score": 1,
        "reason": f"{len(calls)} tool calls; reached: {', '.join(reached) or 'none'}",
        "named_scores": columns,
    }
