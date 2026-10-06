---
name: wagtail-docs
description: >-
  Use when the user or agent needs to read, search, or look up Wagtail
  documentation or the Wagtail v3 API reference. Prefer this over curl or
  WebFetch for any docs.wagtail.org content, and over guessing how a Wagtail
  feature, setting, model, hook or API endpoint works.
metadata:
  short-description: Read and search the Wagtail documentation from the terminal
allowed-tools:
  - Bash(wt docs *)
  - Bash(wt --version)
---

Use `wt docs` instead of fetching [docs.wagtail.org](https://docs.wagtail.org/) with `curl` or `WebFetch`. It prints pages as Markdown, and defaults to the docs for the locally installed Wagtail version (falling back to `stable`).

If `wt` is missing, install it with `uv tool install wagtail-cli`.

## Read a page by its docs path

```bash
# Whole-site table of contents.
wt docs
# Path reference as it appears in the docs index.
wt docs topics/pages
# Another example: release notes.
wt docs releases/8.0
# Or you can provide the full URL.
wt docs https://docs.wagtail.org/en/latest/topics/streamfield.html
```

Pages can be long: use `--outline` to see only a page's headings before reading one section in full, or pipe through `head` or `grep -A`.

## Search by keyword

```bash
wt docs search "custom base page models"
# Or as JSON output:
wt docs search "custom base page models" --json
```

Results show title, path and a snippet. Read the page you want with the path.

## Look up the v3 API reference

```bash
wt docs api                           # index of every operation
wt docs api "POST /pages/"            # one operation, exact
wt docs api get documents             # method and /api/v3/ prefix optional
```

Project-specific endpoints are not in this reference; they only exist in that project's own `<API root>/docs/`.

## Pin a version

We attempt to detect the locally installed Wagtail version and use the corresponding documentation by default, but this can also be overridden.

```bash
wt docs --version 7.2 topics/images
wt docs --version latest search "workflows"
```
