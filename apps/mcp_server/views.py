import json
import logging
import threading

import anyio
from asgiref.sync import async_to_sync
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from mcp.server.transport_security import TransportSecuritySettings
from mcp_types import CLIENT_INFO_META_KEY

from .server import current_request, server

logger = logging.getLogger(__name__)

# Django's own response headers are computed from the body.
SKIPPED_RESPONSE_HEADERS = {b"content-length"}

# Seconds before giving up on the SDK. A safety net in case it ever waits on
# `receive()` for a stream, which JSON responses without subscriptions don't
# do: it can't interrupt service code, which runs on the request's thread.
REQUEST_TIMEOUT = 20

# `streamable_http_app()` both builds a session manager and stores it on the
# server, so building and reading it must not interleave across threads.
# Building the manager directly would avoid the lock and the unused Starlette
# app, but needs the SDK's private `server._lowlevel_server`.
session_manager_lock = threading.Lock()


def get_session_manager(request):
    """
    A fresh stateless session manager for this request.

    A manager's `run()` can only be entered once, and under WSGI every request
    runs in its own event loop, so managers can't be shared across requests.
    """
    # `get_host()` already enforces ALLOWED_HOSTS. Allowing only our own
    # origin rejects requests from other sites' pages in the browser.
    host = request.get_host()
    security = TransportSecuritySettings(
        allowed_hosts=[host],
        allowed_origins=[f"{request.scheme}://{host}"],
    )
    with session_manager_lock:
        server.streamable_http_app(
            stateless_http=True,
            json_response=True,
            transport_security=security,
        )
        return server.session_manager


def get_scope(request):
    """Minimal ASGI HTTP scope for the request, as the SDK expects."""
    headers = [
        (name.lower().encode("latin-1"), value.encode("latin-1"))
        for name, value in request.headers.items()
        if name.lower() != "host"
    ]
    # The host Django validated, which is also the one the SDK checks against.
    headers.append((b"host", request.get_host().encode("latin-1")))
    return {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": request.method,
        "scheme": request.scheme,
        "path": request.path,
        "raw_path": request.path.encode(),
        "query_string": request.META.get("QUERY_STRING", "").encode("latin-1"),
        "root_path": "",
        "headers": headers,
        "client": (request.META.get("REMOTE_ADDR", ""), 0),
    }


def get_dict(data, key):
    value = data.get(key)
    return value if isinstance(value, dict) else {}


def log_usage(request, status):
    """
    Log what the request does and which client sent it, without arguments.

    Clients send their name in `initialize` before 2026-07-28, and with every
    request since.
    """
    try:
        message = json.loads(request.body)
    except ValueError:
        message = None
    if not isinstance(message, dict):
        message = {}
    params = get_dict(message, "params")
    client_info = get_dict(params, "clientInfo") or get_dict(
        get_dict(params, "_meta"), CLIENT_INFO_META_KEY
    )
    logger.info(
        "MCP method=%s name=%s status=%s protocol=%s client=%s/%s user_agent=%r",
        message.get("method"),
        params.get("name"),
        status,
        request.headers.get("MCP-Protocol-Version"),
        client_info.get("name"),
        client_info.get("version"),
        request.headers.get("User-Agent"),
    )


async def dispatch(request, session_manager):
    """Run the request through the SDK, collecting its ASGI response."""
    body_sent = False
    # Unless the SDK responds before the timeout.
    response = {"status": 504, "headers": [], "body": b""}

    async def receive():
        # Deliver the body once, then wait: the client is still connected
        # until we respond. The SDK cancels this wait once it's done, whereas
        # reporting a disconnect would make it drop requests it handles as
        # streams, such as `subscriptions/listen`.
        nonlocal body_sent
        if body_sent:
            await anyio.sleep_forever()
        body_sent = True
        return {"type": "http.request", "body": request.body, "more_body": False}

    async def send(message):
        if message["type"] == "http.response.start":
            response["status"] = message["status"]
            response["headers"] = message.get("headers", [])
        elif message["type"] == "http.response.body":
            response["body"] += message.get("body", b"")

    with anyio.move_on_after(REQUEST_TIMEOUT):
        async with session_manager.run():
            await session_manager.handle_request(get_scope(request), receive, send)
    return response


@csrf_exempt
@require_POST
def mcp_view(request):
    """
    Public MCP endpoint, over stateless Streamable HTTP with JSON responses.

    CSRF-exempt: the endpoint is anonymous and read-only, so there are no
    cookie-based credentials to forge.
    """
    # The protocol answers some errors with a 404, which LocaleMiddleware
    # would otherwise redirect to a language-prefixed URL. It only does so for
    # URLconfs with `i18n_patterns`, which this app's own URLconf doesn't use.
    request.urlconf = "apps.mcp_server.urls"

    session_manager = get_session_manager(request)
    token = current_request.set(request)
    try:
        result = async_to_sync(dispatch)(request, session_manager)
    finally:
        current_request.reset(token)

    log_usage(request, result["status"])
    response = HttpResponse(result["body"], status=result["status"])
    for name, value in result["headers"]:
        if name.lower() not in SKIPPED_RESPONSE_HEADERS:
            response[name.decode("latin-1")] = value.decode("latin-1")
    return response
