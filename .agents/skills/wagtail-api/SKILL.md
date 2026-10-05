---
name: wagtail-api
description: Operate a Wagtail site from the terminal with the Wagtail CLI (`wt api`, from the wagtail-cli package) rather than hand-written HTTP calls. Use it whenever a task involves publishing, creating, editing, moving, copying, unpublishing, deleting, translating or listing content on a Wagtail site, uploading images or documents, inspecting a site's content model, the Wagtail v3 API, `wt` / `wagtail-cli`, `WAGTAIL_CLI_*` variables, `.wagtail-cli.toml`, a `wagtail_…` token, or scaffolding and running a Wagtail project, even when the user does not name the CLI. For reading Wagtail documentation, use the wagtail-docs skill.
metadata:
  short-description: Operate a Wagtail site via its API, with the Wagtail CLI
---

# Wagtail API CLI client

`wt api` is a scriptable client for the Wagtail v3 API. This file is enough for most tasks.

- Read [references/commands.md](references/commands.md) for a fuller overview of all flags
- Read [references/writing-content.md](references/writing-content.md) before building a payload beyond a title.
- See also the [full documentation](https://wagtail.github.io/wagtail-cli/)
- [LLM-friendly documentation sitemap](https://wagtail.github.io/wagtail-cli/llms.txt)
- [Full LLMs documentation sitemap](https://wagtail.github.io/wagtail-cli/llms-full.txt)

## Before you start

Users normally will not say where the site is or how to log in. `wt` reads `WAGTAIL_CLI_BASE_URL` / `WAGTAIL_CLI_TOKEN`, then `./.wagtail-cli.toml`, then `~/.wagtail-cli.toml`, so just run:

```bash
wt --json api whoami
```

- Exit 0 means you are set.
- Exit 2 "Not configured" means the user must provide the API base URL (like `https://cms.example.com/api/v3/`) and a token, via those variables or `wt api init`; ask rather than guessing a URL or searching for tokens.
- Exit 3 is an unreachable URL
- Exit 4 a bad token.

Tokens carry the permissions of the user they belong to. In a Wagtail project with the API enabled, `wt api_tokens create --user=<name>` mints one.

## Working efficiently

- Put global flags before `api`: `wt --json --dry-run api pages create …`.
- Use `--json` and `jq` if available and this output is more readable to you.
- Pass `--limit` on lists (server cap is 20 by default, above it is a 400; page with `--offset`).
- Use `--select id,title,meta.html_url` when you only need identifiers or URLs. It keeps the response compact without using `jq`.
- Check a type's write schema once, then trust it unless you are actively modifying it: `wt --json api schema show blog.BlogPage | jq '.create.required, (.create.properties | keys)'`.
- `--dry-run` shows the request without sending it. On `update`, dry-run without `--publish` or you only see the publish call.
- Skip `--help` for things covered here.
- For an operation's exact generated API reference, `wt docs api "POST /pages/"` (see the wagtail-docs skill).

## Command map

| Group                                                      | Operations                                                                                                                                    |
| ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `wt api whoami`, `wt api init`                             | auth check; save URL + token                                                                                                                  |
| `wt api schema list \| show TYPE`                          | content types; read/create/patch JSON schemas                                                                                                 |
| `wt api pages …`                                           | list, find, get, create, update, delete, publish, unpublish, copy, move, revert, create-alias, convert-alias, copy-for-translation, revisions |
| `wt api images …`, `wt api documents …`                    | list, get, create (upload), update (metadata), delete                                                                                         |
| `wt api snippets TYPE …`                                   | list, get, create, update, delete, publish, unpublish, revert, copy-for-translation, revisions                                                |
| `wt api sites …`, `wt api locales …`, `wt api redirects …` | CRUD; `redirects find --path`                                                                                                                 |
| `wt start NAME [DIR]`                                      | scaffold a project                                                                                                                            |
| `wt <other>`                                               | forwarded to `./manage.py` or `django-admin`                                                                                                  |

## Rules that are easy to get wrong

1. **Unwritable fields are silently dropped.**
   - A create/update succeeds even if you pass a field missing from `create`/`patch` properties; the response just shows it empty.
   - Check the schema, and read the result back.
   - This can only be fixed with model code changes (`APIField("name", writable=True)`).
2. **`update` and `delete` need `--yes`**
   - When run off a TTY, or they exit 2.
   - Actions (`publish`, `unpublish`, `move`, `copy`, `revert`, …) run without a prompt.
3. **Page references.**
   - `--parent` and `--destination` take an id or a URL path like `/blog/`.
   - List filters (`--child-of`, `--descendant-of`, `--ancestor-of`) take an id or `root`.
   - Path to id: `wt --json api pages find --path /blog/` (the `location` ends in `/pages/<id>/`).
4. **Live vs draft.** `find --path` only resolves live pages (404 = draft).
   - Authenticated `list`/`get` include drafts and expose no `live` flag, so use `find --path` or the public URL to tell.
   - There is no anonymous mode; an unauthenticated `curl "$WAGTAIL_CLI_BASE_URL/pages/?child_of=4"` lists live pages only.
5. **`pages get` returns the live version.**
   - It accepts either an ID or a URL path such as `/blog/`.
   - path lookup is resolved inside the same CLI invocation.
   - `--version draft` gives the latest revision (the help text says the opposite).
   - `--html` renders rich text as display HTML.
6. **Create is a draft unless `--publish`.**
   - `update --publish` PATCHes then publishes.
   - A 422 on `slug` is a sibling collision; pass a unique `--slug`.
7. **StreamField and child relations are replaced whole on update.** Read, edit the full list, resend.
8. **Markdown input only works for top-level page rich-text fields.** Many `body` fields are StreamFields; build blocks instead (see the reference).
9. **A 422 naming a child relation** usually means the type requires at least one row; supply it (see the reference).
10. **Sites, locales, redirects update with PUT:** resend every required field (`hostname` + `root_page_id`, `language_code`, `old_path`).
11. **Deletes are permanent** and take descendants along. Prefer `unpublish` when the user only wants something off the site.
12. **Image and document `update` cannot replace the file.**

For `--field` value parsing, rich text, StreamField blocks, child relations, uploads, snippets and worked recipes, read [references/writing-content.md](references/writing-content.md).

## Errors

Errors print `Error (<status>): <title>: <detail>` plus the RFC 7807 body on stderr. A 422's `errors` array names the field.

Exit codes:

- 2 usage (missing `--yes`, unconfigured)
- 3 network
- 4 bad token
- 5 no permission,
- 6 not found (wrong id, unknown type, draft looked up by path)
- 7 validation

Using `-v` logs the HTTP exchange.

## Reporting back

By default, say what changed and how to find it: ids, titles, public URLs, live or draft, and anything you had to decide on the user's behalf.

Commands and payloads are usually noise unless the user asks or something failed.
