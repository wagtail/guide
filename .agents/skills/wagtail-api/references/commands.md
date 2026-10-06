# `wt` command reference

One line per command. `REF` = page id or URL path (resolved through the find
endpoint). `TYPE` = Django model label such as `blog.BlogPage`. `K:V` =
`--field KEY:VALUE`, repeatable, parsed as described in SKILL.md.

## Global flags (before `api`)

```
wt [--url URL] [--token TOKEN] [--json | --human] [-v] [--dry-run] api …
wt --version          # CLI version, plus Wagtail/Django versions when detected
wt --help             # CLI help, plus ./manage.py --help when present
```

- Output is JSON when stdout is not a TTY, human tables otherwise; `--json`
  / `--human` force it. `schema show` is always JSON.
- `--dry-run` prints `METHOD url`, params, and the JSON body, sends nothing.
  Path REFs are left unresolved in dry-run output.
- `-v` logs `> METHOD url` and `< status` to stderr.

## Auth and setup

```
wt api whoami                                   # user, profile, groups
wt api init [--url URL] [--token TOKEN]         # prompts unless both given; writes ~/.wagtail-cli.toml
```

## Schema

```
wt api schema list                              # {"types":[{"name","label"}...]}
wt api schema show TYPE                         # {"read":{…},"create":{…},"patch":{…}} JSON schemas
```

The generic page entry (`wagtailcore.Page`) only has a usable `read`
schema; use a concrete type for `create`/`patch`. A field listed under
`read` but missing from `create`/`patch` is read-only for the API.

## Pages

```
wt api pages list [--type TYPE]... [--child-of ID|root] [--descendant-of ID|root]
                  [--ancestor-of ID] [--translation-of ID] [--locale CODE] [--site NAME|HOST|ID]
                  [--search Q] [--search-operator and|or] [--order FIELD|-FIELD|random]
                  [--limit N] [--offset N]
wt api pages find [--id N] [--path /blog/] [--site S]      # → {"location": ".../pages/<id>/"}
wt api pages get ID [--version draft|live] [--html]          # live by default
wt api pages create TYPE --parent REF --title T [--slug S] [--field K:V]... [--publish]
wt api pages update ID [--title T] [--slug S] [--field K:V]... [--publish] [--yes]   # PATCH
wt api pages delete ID [--yes]                               # hard delete, incl. descendants
wt api pages publish ID
wt api pages unpublish ID
wt api pages copy ID --destination REF [--slug S] [--title T] [--recursive/--no-recursive] [--keep-live/--no-keep-live]
wt api pages move ID --destination REF                       # becomes last child of destination
wt api pages revert ID --revision N                          # new draft from that revision
wt api pages create-alias ID --destination REF
wt api pages convert-alias ID
wt api pages copy-for-translation ID --locale CODE
wt api pages revisions list ID [--limit N] [--offset N]      # newest first
wt api pages revisions get ID REVISION_ID
```

List filters: selecting exactly one `--type` allows ordering by that type's
own fields. `--child-of` and `--descendant-of` cannot be combined. `--order
random` cannot be combined with `--offset`. `--search` requires page search
to be enabled on the site.

Page list items are compact: `id`, `title`, `meta.{type, detail_url,
html_url, locale, slug, first_published_at}`. `get` adds the type's readable
`api_fields` and more `meta` (seo, menus, parent, alias source).

## Images

```
wt api images list [--search Q] [--search-operator and|or] [--order F] [--limit N] [--offset N]
wt api images get ID
wt api images create FILE --title T [--field K:V]...        # multipart; K:V are extra form fields (e.g. collection_id:1, description:…)
wt api images update ID [--title T] [--field K:V]... [--yes] # JSON PATCH, metadata only (title, description, focal_point_*, collection_id)
wt api images delete ID [--yes]
```

Tags are readable but not writable. Custom image models may require
`collection_id` on create even if the schema marks it optional.

## Documents

```
wt api documents list [--search Q] [--search-operator and|or] [--order F] [--limit N] [--offset N]
wt api documents get ID
wt api documents create FILE --title T [--field K:V]...     # multipart
wt api documents update ID [--title T] [--field K:V]... [--yes]
wt api documents delete ID [--yes]
```

## Snippets

```
wt api snippets list TYPE [--locale CODE] [--translation-of ID] [--search Q]
                         [--search-operator and|or] [--order F] [--limit N] [--offset N]
wt api snippets get TYPE PK
wt api snippets create TYPE [--field K:V]...
wt api snippets update TYPE PK [--field K:V]... [--yes]     # PATCH
wt api snippets delete TYPE PK [--yes]
wt api snippets publish TYPE PK                             # DraftStateMixin only
wt api snippets unpublish TYPE PK                           # DraftStateMixin only
wt api snippets revert TYPE PK --revision N                 # RevisionMixin only
wt api snippets copy-for-translation TYPE PK --locale CODE  # TranslatableMixin only
wt api snippets revisions list TYPE PK [--limit N] [--offset N]
wt api snippets revisions get TYPE PK REVISION_ID
```

A model is only exposed if it declares at least one `APIField`; `wt api
schema list` shows which. PKs may be integers, UUIDs, or strings.

## Sites

```
wt api sites list [--limit N] [--offset N]
wt api sites get ID
wt api sites create --field hostname:H --field root_page_id:N [--field port:443] [--field site_name:S] [--field is_default_site:true]
wt api sites update ID --field K:V... [--yes]               # PUT: resend hostname + root_page_id
wt api sites delete ID [--yes]
```

## Locales

```
wt api locales list [--limit N] [--offset N]
wt api locales get ID
wt api locales create --field language_code:fr
wt api locales update ID --field language_code:fr [--yes]   # PUT
wt api locales delete ID [--yes]                            # refused if still in use or last locale
```

## Redirects

```
wt api redirects list [--order F] [--limit N] [--offset N]  # no search
wt api redirects find [--id N] [--path /old/]               # → {"location": ".../redirects/<id>/"}
wt api redirects get ID
wt api redirects create --field old_path:/old/ [--field redirect_page_id:N | --field redirect_link:URL]
                        [--field is_permanent:true] [--field site_id:N]
wt api redirects update ID --field K:V... [--yes]           # PUT: resend old_path
wt api redirects delete ID [--yes]
```

## Project scaffolding and delegation

```
wt start NAME [DIRECTORY] [--template T] [-e EXT]... [-n FILE]... [-x DIR]... [--settings S] [--pythonpath P]
wt <django-command> [args...]             # → ./manage.py <cmd> (cwd) or django-admin <cmd> (DJANGO_SETTINGS_MODULE)
```
