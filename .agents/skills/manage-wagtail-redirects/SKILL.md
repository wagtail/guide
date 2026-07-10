---
name: manage-wagtail-redirects
description: Manage Wagtail redirects (list, get, create, edit, delete) against a Wagtail site's v3 API, authenticating with a session cookie.
---

## Overview

Manage Wagtail redirects via the Wagtail v3 write/read API, authenticating with a
session cookie. All interactions go through the `manage_wagtail_redirects.py` script
in this skill directory, which talks to `/api/v3/redirects/`.

Usage:

-   `/manage-wagtail-redirects list the redirects on http://localhost:8000`
-   `/manage-wagtail-redirects create a redirect from /old to https://example.com on http://localhost:8000`
-   `Edit redirect #5 to point to https://example.org (site http://localhost:8000)`
-   `Delete the /potato redirect on http://localhost:8000`

## Requirements

-   [`uv`](https://docs.astral.sh/uv/) installed — the script is run with `uv run --script`
    and declares its own dependencies inline (PEP 723), so no virtualenv setup is needed.
-   A running Wagtail site with the v3 API enabled (endpoints under `/api/v3/redirects/`).
-   A valid `sessionid` session cookie for a Wagtail user with permission to manage redirects.
    The script never authenticates itself — it reuses the session the user already has.

## Inputs

Detect from context or request from the user if unclear:

-   **Wagtail site URL** (e.g. `http://localhost:8000`). No trailing slash needed.
-   **Session ID cookie** — the value of the `sessionid` cookie for an authenticated
    Wagtail admin user with redirect management permissions.

Treat the session cookie as a secret:

-   Never echo it back in chat, output, or files.
-   Pass it to the script via the `WAGTAIL_SESSION_ID` environment variable (preferred) or the
    `--session-id` flag — never bake it into a committed script.
-   Likewise the site URL may be passed via `WAGTAIL_URL` or `--url`.

## The script

Located at `./manage_wagtail_redirects.py` (this skill directory). Run it directly; `uv`
resolves dependencies automatically on first run:

```sh
./manage_wagtail_redirects.py --url http://localhost:8000 --session-id <SESSION_ID> list
```

Or, using environment variables (recommended so the cookie stays out of process args/argv):

```sh
WAGTAIL_URL=http://localhost:8000 WAGTAIL_SESSION_ID=<SESSION_ID> \
    ./manage_wagtail_redirects.py list
```

The script prints JSON to stdout on success, so parse it with that assumption. On error it
prints a human-readable message to stderr and exits non-zero.

## Subcommands

Run `./manage_wagtail_redirects.py --help` for the authoritative reference. Key flags:

### `list` — list redirects

```sh
./manage_wagtail_redirects.py list [--limit N] [--offset N]
```

Returns `{"items": [...], "count": N}` and paginates with `--limit`/`--offset`
(API default limit 20). If `count` exceeds fetched items, keep paging with `--offset`.

### `get <redirect_id>` — fetch one redirect

### `create` — create a redirect

```sh
./manage_wagtail_redirects.py create \
    --old-path /old-path \
    [--redirect-link https://example.com] \
    [--redirect-page-id 42] \
    [--redirect-page-route-path /some/route/] \
    [--site 1] \
    [--temporary]      # default is permanent (--permanent)
```

`--old-path` is required. Provide exactly one destination: `--redirect-link` (external URL)
or `--redirect-page-id` (Wagtail page). `--site` scopes the redirect to a site (default: all sites).

### `update <redirect_id>` — edit a redirect

```sh
./manage_wagtail_redirects.py update 5 --old-path /new-path --redirect-link https://example.org
```

Only the fields you pass are changed — the script fetches the existing redirect, merges your
changes on top, then performs a full PUT. This sidesteps the v3 API requiring the whole object
on `PUT`. `--old-path` cannot be unset (it is always required server-side).

### `delete <redirect_id>` — delete a redirect

Returns `{"deleted": true, "id": <redirect_id>}` on success (HTTP 204).

## Field reference (v3 API)

Read fields: `id`, `old_path`, `site_id`, `is_permanent`, `redirect_page_id`,
`redirect_page_route_path`, `redirect_link`, `automatically_created`, `created_at`.

Write fields (create/update): `old_path` (required), `site` (int|null — note the API writes
`site` but reads `site_id`; the `update` subcommand handles this translation for you),
`is_permanent` (default true), `redirect_page_id`, `redirect_page_route_path`, `redirect_link`.

## Workflow

1.  Confirm `WAGTAIL_URL`/`--url` and `WAGTAIL_SESSION_ID`/`--session-id`. Ask the user for
    either if missing — do not guess.
2.  For destructive actions (create / update / delete), show the user what you're about to do
    (the payload or the target redirect id) and confirm before executing, unless they've
    already described the exact change in their request.
3.  Prefer `list` first to locate a redirect by `old_path` when the user only knows the path,
    then operate on its `id`.
4.  After create/update/delete, verify with `get <id>` or `list`, and report the salient fields
    (`id`, `old_path`, destination, `is_permanent`, `site_id`).

## Guardrails

-   Never commit the session cookie or write it to any file under the repo.
-   Don't disable TLS verification or change auth mechanisms — reuse the user's session only.
-   If the API returns a 403 (`Permission denied`), stop and tell the user the session lacks
    redirect-management permissions; don't retry with modified headers.
-   If the API returns a 302/login redirect that resolves to the login page, the session is
    likely expired — ask the user for a fresh `sessionid` rather than continuing.
