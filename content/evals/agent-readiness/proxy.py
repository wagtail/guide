"""
mitmproxy addon for the agent readiness eval (see `just eval-agents-proxy`).

The proxy listens on two ports, one per version of the site:

- `FULL_PORT` serves the guide as it is.
- `PLAIN_PORT` serves a plain site: the same pages without any of the guide's
  agent readiness features. Those files return 404, requests ask for HTML
  only, and pages lose their links and metadata for agents. Comparing an arm
  on each port shows what the features are worth.

On both ports, every request is logged as one JSON line, because the agent's
own trace doesn't show request headers: this is how we see Markdown content
negotiation, and the status codes agents get.
"""

import json
import os
import re
import time

from mitmproxy import http

FULL_PORT = 8899
PLAIN_PORT = 8898
LOG_PATH = os.environ["EVAL_PROXY_LOG"]

# Agent readiness files and endpoints, missing from the plain site.
PLAIN_BLOCKED_PATHS = re.compile(
    r"^/(llms\.txt|llms-full\.txt|\.well-known/.*|openapi\.json|mcp"
    r"|api/v3-preview/openapi\.json|.*/markdown/?)$"
)
# Markup for agents in pages: links to the files above, Markdown alternates,
# JSON-LD, and the script bundle that registers WebMCP tools.
PLAIN_STRIPPED_MARKUP = [
    re.compile(pattern, re.DOTALL)
    for pattern in [
        r"<link[^>]*(ai-catalog|api-catalog|text/markdown|openapi|llms)[^>]*>",
        r"<li>\s*<a[^>]*href=\"[^\"]*(markdown/|llms(-full)?\.txt)\"[^>]*>.*?</a>\s*</li>",
        r"<script type=\"application/ld\+json\">.*?</script>",
        r"<script[^>]*src=\"/static/main[^\"]*\"[^>]*></script>",
    ]
]
PLAIN_ROBOTS_LINES = re.compile(r"^(#.*contentsignals.*|Content-Signal:.*)\n", re.M)


def site(flow):
    """Which version of the site this request is for, from the port it used."""
    port = flow.client_conn.sockname[1]
    return "plain" if port == PLAIN_PORT else "full"


def request(flow):
    flow.metadata["accept"] = flow.request.headers.get("accept")
    if site(flow) != "plain":
        return
    if PLAIN_BLOCKED_PATHS.match(flow.request.path.split("?")[0]):
        flow.response = http.Response.make(
            404, b"<h1>Page not found</h1>", {"Content-Type": "text/html"}
        )
        return
    flow.request.headers["accept"] = "text/html"


def response(flow):
    if site(flow) == "plain" and flow.response.status_code != 404:
        content_type = flow.response.headers.get("content-type", "")
        if content_type.startswith("text/html"):
            html = flow.response.get_text()
            for pattern in PLAIN_STRIPPED_MARKUP:
                html = pattern.sub("", html)
            flow.response.set_text(html)
        elif flow.request.path == "/robots.txt":
            flow.response.set_text(PLAIN_ROBOTS_LINES.sub("", flow.response.get_text()))

    entry = {
        "ts": time.time(),
        "site": site(flow),
        "method": flow.request.method,
        "url": flow.request.pretty_url,
        "accept": flow.metadata.get("accept"),
        "user_agent": flow.request.headers.get("user-agent"),
        "status": flow.response.status_code,
        "content_type": flow.response.headers.get("content-type"),
    }
    with open(LOG_PATH, "a") as log:
        log.write(json.dumps(entry) + "\n")
