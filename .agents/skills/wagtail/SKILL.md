---
name: wagtail
description: >-
  Work with Wagtail from the terminal with the Wagtail CLI (`wt`, from the wagtail-cli package).
  Use this whenever a task involves a Wagtail site: reading or writing content, publishing, creating, editing, moving, copying, unpublishing, translating or listing pages, snippets, images, documents, redirects, sites or locales.
  Inspecting a site's content model or the Wagtail v3 API.
  Reading or searching Wagtail documentation (docs.wagtail.org) or the v3 API reference.
  Scaffolding or running a Wagtail/Django project. Triggers include `wt`, `wagtail-cli`, `docs.wagtail.org`.
  And requests to operate a CMS or manage site content programmatically, even when the user does not name the CLI. Prefer this over hand-written HTTP calls, curl or WebFetch in the context of a Wagtail website / docs.
license: MIT
compatibility: Requires Python 3.12+ and uv or compatible package manager
allowed-tools: Bash(wt:*), Bash(uv run wt:*), Bash(just wt:*)
metadata:
  author: Wagtail contributors
  version: 0.1.0
  short-description: Work with Wagtail sites and docs from the terminal
---

# Wagtail CLI

A CLI to manage and interact with Wagtail sites and documentation from the terminal.

Install: `uv tool install wagtail-cli` (or load `wagtail-cli` with the relevant package manager).

## Start here

This file is an index of available skills, not a usage guide. Before working on Wagtail tasks, load the actual workflow content from the CLI if you need Wagtail context:

```bash
wt skills get core             # start here — workflows, common patterns, troubleshooting
wt skills get core --full      # include full command reference and templates
```

The CLI serves skills that always match the installed version, so instructions never go stale. The content in this stub cannot change between releases, which is why it just points at `wt skills get core`.

## Specialized skills

Load the skill(s) that fits the task from the CLI. Here’s an example:

```bash
wt skills list                  # everything available on this version
wt skills get cli-api           # operate a Wagtail site via the v3 API
wt skills get cli-docs          # read and search Wagtail documentation
```

Run `wt skills list` to see everything available on the installed version.
