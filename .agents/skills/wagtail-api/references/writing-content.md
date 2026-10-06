# Writing content through `wt`

How the Wagtail v3 API represents each kind of field, and how to express it
with `--field`. Read this before building a create/update payload that goes
beyond `--title`.

## 0. `--field` value parsing

`--field KEY:VALUE` is repeatable on `create`/`update`:

| Value                        | Sent as                                                   |
| ---------------------------- | --------------------------------------------------------- |
| `[…` or `{…`                 | parsed JSON (quote it in the shell)                       |
| `@file.md`                   | `{"format": "db_markdown", "content": "<file text>"}`     |
| `@file.json`                 | parsed JSON (StreamField bodies, child relations)         |
| `@file.html` / other `@file` | raw file text                                             |
| `@-`                         | stdin, raw                                                |
| anything else                | plain string (`title:Hello`, `date_published:2026-09-18`) |

Foreign keys use the id field the schema names, usually `<name>_id`.

## 1. Discover the shape first

```bash
wt --json api schema list                                    # type labels
wt --json api schema show blog.BlogPage | jq '.create.required'
wt --json api schema show blog.BlogPage | jq '.create.properties | to_entries[] | {key, type: .value.type}'
```

- `read` is what `get` returns; `create` and `patch` are what you may send.
  A field present in `read` but absent from `create`/`patch` is not writable
  (the project did not declare `APIField(..., writable=True)`).
- Schemas are generated from the project's models and panels, so the list is
  site-specific. StreamFields appear as `list[Any]`: the schema tells you the
  field exists but not the block types. Get block names from the project's
  `blocks.py`/models, from an existing page (`pages get ID | jq .body`), or
  from the developer.
- Validation on write is the same as the admin edit form: required fields,
  chooser IDs, block `clean()`, and permissions all apply.

## 2. Page payload anatomy

`wt api pages create TYPE --parent REF --title T` builds:

```json
{"meta": {"type": "blog.BlogPage", "parent_id": 3, "action": "publish"}, "title": "T", "slug": "…", …fields}
```

`--publish` adds `meta.action: publish`; otherwise the page is a draft. Slug
is generated from the title when omitted. `update` sends a PATCH with only
the fields you pass; `--publish` then calls the publish action.

Built-in writable page fields (when exposed): `title`, `slug`, `seo_title`,
`search_description`, `show_in_menus`. Plus the type's own writable
`api_fields`.

## 3. Scalars, dates, booleans, foreign keys

```bash
--field subtitle:"Second line"          # string
--field date_published:2026-09-18       # ISO date string
--field show_in_menus:true              # sent as the string "true"; the API coerces booleans
--field image_id:42                     # FK: use the id field name the schema lists
--field 'tags:["bread","rye"]'          # list (JSON because it starts with [)
```

If a value must be a JSON number/boolean rather than a string and the API
rejects the string form, wrap it in a JSON object file or use a `.json` file
for the whole field set of that request.

## 4. Rich text

Stored as Wagtail database HTML. Two input forms for **top-level page rich
text fields** (`RichTextField` on the page model):

| You pass                                                | Sent                                                                      |
| ------------------------------------------------------- | ------------------------------------------------------------------------- |
| `--field body:@post.md`                                 | `{"format":"db_markdown","content":"…"}` — Markdown converted server-side |
| `--field body:@post.html` or `--field body:'<p>Hi</p>'` | raw database HTML                                                         |

Markdown may reference Wagtail objects with `wagtail://` URLs:
`[About](wagtail://page?id=3)`, `[Policy](wagtail://document?id=7)`,
`![Alt](wagtail://image?id=42)`. Content not allowed by the field's
`features` is silently stripped, so read the page back if fidelity matters.

Reading: `pages get` returns database HTML by default; `--html` returns
display HTML with resolved URLs. The API also supports `markdown` /
`db_markdown` output formats, but the CLI only exposes `--html`.

The Markdown envelope is **not** supported for snippet rich text fields or
for rich text inside StreamField blocks; send database HTML strings there.

## 5. StreamField

A StreamField value is a JSON list of blocks:

```json
[
  { "type": "heading", "value": "Example" },
  {
    "type": "paragraph",
    "value": "<p>Database HTML for a RichTextBlock.</p>"
  },
  { "type": "image", "value": 42 },
  { "type": "quote", "value": { "text": "…", "attribution": "…" } },
  { "type": "gallery", "value": [42, 43] }
]
```

- `id` per block is optional on input (Wagtail generates UUIDs). Supply ids
  when you want them stable across updates.
- Block `value` by block kind: nested StreamBlock → list of `{type, value}`;
  StructBlock → object keyed by child names; ListBlock → plain list of child
  values; chooser blocks (image, page, document, snippet) → the object's id;
  RichTextBlock → database HTML string; leaf blocks → scalar.
- Unknown block type → 422.
- **Update replaces the whole list.** To change one block: `pages get ID
--version draft | jq .body > body.json`, edit, then
  `pages update ID --field body:@body.json --yes`.

Write it via a file to avoid shell quoting problems:

```bash
wt --json api pages create blog.BlogPage --parent /blog/ --title "Example" \
  --field body:@body.json --publish
```

## 6. Child relations (InlinePanel / ParentalKey)

Writable child relations appear in the schema as a list of child objects,
for example `blog_person_relationship: [{"person_id": 3}]`. Same
replace-as-a-whole rule as StreamField: when you send the list, children
whose `id` matches are edited, missing ones are deleted, new ones created.
Omit the field to leave it untouched.

```bash
--field 'blog_person_relationship:[{"person_id":3}]'
```

Some models make a child relation required (`min_num=1`); a 422 naming
that relation means you must supply at least one row.

**Read shape is not write shape.** `get` returns relations and foreign keys
as nested objects (`"person": {"id": 3, "meta": {...}}`, `"image": {"id":
42, ...}`), while `create`/`patch` expect the id fields the schema lists
(`person_id`, `image_id`). When you resubmit something you read, map each
row to `{"id": <row id>, "person_id": <person id>}` (keep `id` to edit the
row in place, drop it to create a new row). StreamField chooser blocks are
the exception: they read back and are written as the bare id (or the
block's custom API representation, which you must reduce back to an id).

## 7. Images and documents

Create is a multipart upload; extra `--field` values become form fields:

```bash
wt --json api images create hero.png --title "Hero" --field description:"A hero" --field collection_id:1
wt --json api documents create policy.pdf --title "Policy" --field collection_id:1
```

Responses include `id`, `title`, dimensions (images), `collection`, `tags`,
and download URLs. Use the `id` in chooser blocks, FK fields
(`image_id:42`), or `wagtail://image?id=42` links. `update` changes metadata
only (title, description, focal point, collection); tags are read-only; the
binary cannot be replaced.

## 8. Snippets

Snippet endpoints are per model label and always need a token. What you can
do depends on the model's mixins:

| Mixin               | Enables                                                           |
| ------------------- | ----------------------------------------------------------------- |
| `RevisionMixin`     | `revisions list/get`, `revert`                                    |
| `DraftStateMixin`   | drafts, `--field` writes create a revision, `publish`/`unpublish` |
| `TranslatableMixin` | `--locale`, `--translation-of`, `copy-for-translation`            |
| `LockableMixin`     | locks respected, no lock/unlock via API                           |
| `WorkflowMixin`     | not supported                                                     |

Calling `publish` on a model without `DraftStateMixin` fails; `create` and
`update` on such a model write directly. Snippet fields follow the same
`--field` rules, minus the Markdown envelope.

## 9. Sites, locales, redirects

Plain CRUD with `--field`. `update` is a PUT, so resend every required
field:

```bash
wt --json api sites create --field hostname:www.example.com --field port:443 \
  --field site_name:Example --field root_page_id:4 --field is_default_site:true
wt --json api sites update 2 --field hostname:www.example.com --field root_page_id:4 --field site_name:Renamed --yes
wt --json api locales create --field language_code:fr
wt --json api redirects create --field old_path:/old/ --field redirect_page_id:9 --field is_permanent:true
wt --json api redirects create --field old_path:/ext/ --field redirect_link:https://example.org/
```

Redirect fields: `old_path`, `site_id` (nullable), `is_permanent`,
`redirect_page_id`, `redirect_page_route_path`, `redirect_link`.

## 10. Drafts, publishing, revisions

- Every save through the API creates a revision attributed to the token's
  user. `revisions list` is newest first.
- `publish` publishes the latest revision; if that revision has a future
  `go_live_at`, it schedules instead. There is no API to set `go_live_at`
  itself beyond writing it as a field if the type exposes it.
- `revert --revision N` creates a new draft from revision N; follow with
  `publish` to make it live.
- `unpublish` keeps the page and its draft; `delete` removes it and its
  descendants permanently.
- Authenticated `list`/`get` see draft-only pages; anonymous requests do not.

## 11. Multi-site and translation

- `pages list --site HOST|NAME|ID` scopes to a site; `pages find --site` too.
- `copy-for-translation ID --locale fr` creates the initial translated copy
  (the API also supports `copy_parents`, `alias`, `recursive`, which the CLI
  does not expose yet; use `wt docs api "POST /pages/{page_id}/actions/copy_for_translation/"`
  if you need them via another client).
- `pages list --translation-of ID --locale fr` finds an existing translation.

## 12. Recipes

```bash
# Publish a Markdown post (rich-text body)
wt --json api pages create blog.BlogPage --parent /blog/ --title "Bread" --field body:@post.md --publish

# Markdown into a StreamField body: write blocks to a file, then send it
cat > body.json <<'JSON'
[{"type":"heading_block","value":{"heading_text":"Why a starter matters","size":"h2"}},
 {"type":"paragraph_block","value":"<p>A starter is a living culture.</p>"}]
JSON
wt --json api pages create blog.BlogPage --parent /blog/ --title "Starters" --field body:@body.json --publish

# Upload an image, then prepend an image block to an existing body
IMG=$(wt --json api images create hero.png --title "Hero" | jq .id)
wt --json api pages get 42 --version draft | jq --argjson img "$IMG" \
  '[{"type":"image","value":$img}] + .body' > body.json
wt --json api pages update 42 --field body:@body.json --publish --yes

# Redirect an old URL
wt --json api redirects create --field old_path:/old/ --field redirect_page_id:9 --field is_permanent:true

# Roll back to an earlier revision
wt --json api pages revisions list 42 --limit 5
wt --json api pages revert 42 --revision 41 && wt --json api pages publish 42

# Snippets (type label required; publish only if the model has DraftStateMixin)
wt --json api snippets create blog.Person --field first_name:Ada --field last_name:Lovelace
wt --json api snippets publish blog.Person 3
```
