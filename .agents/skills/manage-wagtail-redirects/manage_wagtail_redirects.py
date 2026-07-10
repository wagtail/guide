#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "httpx2>=2.5",
# ]
# ///
# ruff: noqa: T201
"""Manage Wagtail redirects via the v3 API (list / get / create / update / delete).

Authenticates with a Wagtail `sessionid` session cookie. Pass the site URL and
session id via flags (`--url`/`--session-id`) or environment variables
(`WAGTAIL_URL`/`WAGTAIL_SESSION_ID`).

Examples
--------
    WAGTAIL_URL=http://localhost:8000 WAGTAIL_SESSION_ID=abc123 \\
        ./manage_wagtail_redirects.py list

    ./manage_wagtail_redirects.py --url http://localhost:8000 \\
        --session-id abc123 create --old-path /old \\
        --redirect-link https://example.com

Run with `--help` for full usage.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, NoReturn

import httpx2

API_PREFIX = "/api/v3/redirects"
# Read field -> write field. Note the API reads `site_id` but writes `site`.
WRITE_FIELD_MAP: dict[str, str] = {
    "old_path": "old_path",
    "site_id": "site",
    "is_permanent": "is_permanent",
    "redirect_page_id": "redirect_page_id",
    "redirect_page_route_path": "redirect_page_route_path",
    "redirect_link": "redirect_link",
}


def die(message: str) -> NoReturn:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def resolve_credentials(args: argparse.Namespace) -> tuple[str, str]:
    url = args.url or os.environ.get("WAGTAIL_URL")
    session_id = args.session_id or os.environ.get("WAGTAIL_SESSION_ID")
    if not url:
        die("Wagtail site URL is required: pass --url or set WAGTAIL_URL.")
    if not session_id:
        die("Session id is required: pass --session-id or set WAGTAIL_SESSION_ID.")
    return url.rstrip("/"), session_id


def build_client(base_url: str, session_id: str) -> httpx2.Client:
    return httpx2.Client(
        base_url=base_url,
        cookies={"sessionid": session_id},
        headers={
            "Accept": "application/json",
            "Referer": base_url + "/",
        },
        follow_redirects=True,
        timeout=30.0,
    )


def check_response(resp: httpx2.Response) -> None:
    if resp.is_success:
        return
    # The v3 API returns RFC 7807 problem+json on validation/auth errors.
    detail: str
    if resp.status_code == 404:
        final = str(resp.url)
        detail = "not found"
        # If the i18n redirect landed on the login page, the session is expired.
        if "/login" in final or "login" in resp.text[:2000].lower():
            detail = (
                "not found (or session expired: the request was redirected to "
                "the login page — provide a fresh sessionid)"
            )
        die(f"API error: HTTP 404 Not Found ({final}) — {detail}")
    try:
        body = resp.json()
    except (ValueError, json.JSONDecodeError):
        # Non-JSON body (e.g. an HTML error page). Don't dump the whole thing.
        text = resp.text.strip()
        if len(text) > 500:
            text = text[:500] + " …(truncated)"
        detail = text or f"HTTP {resp.status_code} {resp.reason_phrase}"
        die(
            f"API error: HTTP {resp.status_code} {resp.reason_phrase} "
            f"({resp.url})\n  {detail}"
        )
    parts: list[str] = []
    title = body.get("title") or ""
    detail_main = body.get("detail") or ""
    errors = body.get("errors")
    if isinstance(errors, list):
        for err in errors:
            loc = err.get("loc")
            loc_str = ".".join(str(x) for x in loc) if isinstance(loc, list) else ""
            msg = err.get("msg") or ""
            parts.append(f"{loc_str}: {msg}".strip(": "))
    pieces = [p for p in (title, detail_main, *parts) if p]
    detail = " | ".join(pieces) or f"HTTP {resp.status_code}"
    die(
        f"API error: HTTP {resp.status_code} {resp.reason_phrase} "
        f"({resp.url})\n  {detail}"
    )


def emit(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_list(client: httpx2.Client, args: argparse.Namespace) -> None:
    params: dict[str, Any] = {}
    if args.limit is not None:
        params["limit"] = args.limit
    if args.offset is not None:
        params["offset"] = args.offset
    resp = client.get(API_PREFIX + "/", params=params)
    check_response(resp)
    data = resp.json()
    # Surface pagination hints for the caller.
    fetched = len(data.get("items", []))
    count = data.get("count")
    data["_pagination"] = {
        "fetched": fetched,
        "count": count,
        "limit": args.limit,
        "offset": args.offset or 0,
        "more": (count is not None and fetched + (args.offset or 0) < count),
    }
    emit(data)


def cmd_get(client: httpx2.Client, args: argparse.Namespace) -> None:
    resp = client.get(f"{API_PREFIX}/{args.redirect_id}/")
    check_response(resp)
    emit(resp.json())


def parse_common_fields(args: argparse.Namespace) -> dict[str, Any]:
    """Build the redirect payload fields shared by create/update."""
    payload: dict[str, Any] = {}
    if args.old_path is not None:
        payload["old_path"] = args.old_path
    if args.redirect_link is not None:
        payload["redirect_link"] = args.redirect_link
    if args.redirect_page_id is not None:
        payload["redirect_page_id"] = args.redirect_page_id
    if args.redirect_page_route_path is not None:
        payload["redirect_page_route_path"] = args.redirect_page_route_path
    if args.site is not None:
        payload["site"] = args.site
    if args.temporary:
        payload["is_permanent"] = False
    elif args.permanent:
        payload["is_permanent"] = True
    if args.no_site:
        payload["site"] = None
    if args.no_page:
        payload["redirect_page_id"] = None
    return payload


def cmd_create(client: httpx2.Client, args: argparse.Namespace) -> None:
    payload = parse_common_fields(args)
    if "old_path" not in payload:
        die("Create requires --old-path.")
    if "is_permanent" not in payload:
        payload["is_permanent"] = True
    payload.setdefault("redirect_link", "")
    payload.setdefault("redirect_page_route_path", "")
    resp = client.post(API_PREFIX + "/", json=payload)
    check_response(resp)
    emit(resp.json())


def existing_to_write_payload(existing: dict[str, Any]) -> dict[str, Any]:
    """Translate a read response into a valid write payload for PUT."""
    payload: dict[str, Any] = {}
    for read_key, write_key in WRITE_FIELD_MAP.items():
        if read_key in existing:
            payload[write_key] = existing[read_key]
    payload.setdefault("redirect_link", "")
    payload.setdefault("redirect_page_route_path", "")
    return payload


def cmd_update(client: httpx2.Client, args: argparse.Namespace) -> None:
    redirect_id = args.redirect_id
    resp = client.get(f"{API_PREFIX}/{redirect_id}/")
    check_response(resp)
    existing = resp.json()
    payload = existing_to_write_payload(existing)
    changes = parse_common_fields(args)
    if not changes:
        die("Update needs at least one field to change.")
    payload.update(changes)
    if not payload.get("old_path"):
        die("old_path is required and cannot be removed.")
    resp = client.put(f"{API_PREFIX}/{redirect_id}/", json=payload)
    check_response(resp)
    emit(resp.json())


def cmd_delete(client: httpx2.Client, args: argparse.Namespace) -> None:
    redirect_id = args.redirect_id
    resp = client.delete(f"{API_PREFIX}/{redirect_id}/")
    check_response(resp)
    emit({"deleted": True, "id": redirect_id})


def add_redirect_fields(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--old-path", metavar="PATH", help="Path to redirect from (e.g. /old)."
    )
    parser.add_argument(
        "--redirect-link",
        metavar="URL",
        help="External URL to redirect to.",
    )
    parser.add_argument(
        "--redirect-page-id",
        type=int,
        metavar="ID",
        help="ID of a Wagtail page to redirect to.",
    )
    parser.add_argument(
        "--redirect-page-route-path",
        metavar="ROUTE",
        help="A specific route path on the target page.",
    )
    parser.add_argument(
        "--site",
        type=int,
        metavar="ID",
        help="Scope the redirect to a site via its ID.",
    )
    parser.add_argument(
        "--no-site",
        action="store_true",
        help="Make the redirect apply to all sites (site = null).",
    )
    parser.add_argument(
        "--no-page",
        action="store_true",
        help="Clear redirect_page_id (use with --redirect-link).",
    )
    perm = parser.add_mutually_exclusive_group()
    perm.add_argument(
        "--permanent",
        action="store_true",
        help="Make the redirect permanent (HTTP 301).",
    )
    perm.add_argument(
        "--temporary",
        action="store_true",
        help="Make the redirect temporary (HTTP 302).",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="manage_wagtail_redirects.py",
        description=(
            "Manage Wagtail redirects via the v3 API, authenticating with a "
            "session cookie. Use WAGTAIL_URL / WAGTAIL_SESSION_ID env vars or "
            "--url / --session-id."
        ),
    )
    parser.add_argument("--url", help="Wagtail site URL (env: WAGTAIL_URL).")
    parser.add_argument(
        "--session-id",
        help="Value of the sessionid cookie (env: WAGTAIL_SESSION_ID).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List redirects.")
    p_list.add_argument("--limit", type=int, help="Max items (default API: 20).")
    p_list.add_argument("--offset", type=int, default=0, help="Pagination offset.")
    p_list.set_defaults(func=cmd_list)

    p_get = sub.add_parser("get", help="Fetch a single redirect.")
    p_get.add_argument("redirect_id", type=int)
    p_get.set_defaults(func=cmd_get)

    p_create = sub.add_parser("create", help="Create a redirect.")
    add_redirect_fields(p_create)
    p_create.set_defaults(func=cmd_create)

    p_update = sub.add_parser(
        "update",
        help=(
            "Edit a redirect. Only passed fields change (fetch-then-merge-then-PUT)."
        ),
    )
    p_update.add_argument("redirect_id", type=int)
    add_redirect_fields(p_update)
    p_update.set_defaults(func=cmd_update)

    p_delete = sub.add_parser("delete", help="Delete a redirect.")
    p_delete.add_argument("redirect_id", type=int)
    p_delete.set_defaults(func=cmd_delete)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    base_url, session_id = resolve_credentials(args)
    client = build_client(base_url, session_id)
    try:
        args.func(client, args)
    except httpx2.HTTPError as exc:
        die(f"HTTP transport error: {exc}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
