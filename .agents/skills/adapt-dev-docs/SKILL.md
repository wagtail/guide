---
name: adapt-dev-docs
description: Write a new page for the User Guide, derived from the developer documentation.
license: MIT
metadata:
  audience: maintainers
  internal: true
  disable-model-invocation: true
---

## Overview

Generate a CMS-user-facing guide page from the official Wagtail developer documentation. The output is a Markdown file ready for review and screenshot insertion, following our [style guide](../../../docs/style-guide.md).

Usage:

- `/adapt-dev-docs https://docs.wagtail.org/en/stable/advanced_topics/api/v3/index.html.md`
- `/adapt-dev-docs /path/to/wagtail/docs/advanced_topics/api/v3/index.md`

## Methodology

### Goals

- Produce Markdown files under `content/en/`, following the page template, structure, exclusion rules, and tone defined in the style guide.
- Translate the developer documentation into plain language for content editors, moderators, and administrators who use Wagtail but don't write code for it.
- Suggest other documentation changes and internal links to existing or newly-introduced docs.

### Guardrails

- Don't invent feature names, version numbers, contributors, release dates, or screenshot URLs — pull them from the developer docs or leave a `<!-- TODO: screenshot - alt: ... -->` placeholder for the user to fill in.
- Don't open a PR or commit. The skill ends with a file on disk for the user to review and add screenshots to.

### Inputs

To detect from the context or request from the user if unclear:

- **Scope**, whether it's a section, a whole page, or multiple pages. Default: ask the user, or suggest a structure based on existing content.
- **Technical translation**, how to adapt certain terminology or sections in the developer documentation that may be too technical for the guide's audience but worth including.
- **Existing draft**. If a file with similar content already exists, read it first and treat it as a starting point — preserve human edits (custom phrasing, screenshot URLs already filled in) rather than overwriting blindly.

### Reference data sources

Always fetch the latest information from the canonical sources rather than relying on local caches.

- **Style guide**: [Release notes guidance](../../../docs/style-guide.md) — the source of truth for page structure, tone, what to include/exclude, and how to translate developer jargon.
- **Developer release notes**: `https://docs.wagtail.org/en/latest/releases/<X.Y>.html.md`.
- **Recent precedents**: `content/en/**` — find existing content that may have been similarly adapted from the developer docs, such as "concepts" pages or the release notes.
- **User guide pages worth linking to**: search `content/en/` for destinations matching the new content. Feel free to suggest documentation changes to link to.

### Reporting

After writing the file, report:

- The output path and the developer documentation URL fetched.
- Each substantial content included, with one-line rationale.
- Each developer-notes item that was deliberately excluded, grouped by reason (developer-only content / unclear user value).
- Every `<!-- TODO: screenshot -->` marker, with suggested alt text.
- Every internal link suggestion to documentation that needs to be created.
- Suggested follow-ups: user guide pages under `content/en/` that may need updates to acknowledge the new features.

## Steps

### 1. Resolve the developer documentation and gather sources

- [ ] Confirm the source developer documentation page(s) with the user.
- [ ] Compute the output structure under `content/en/**`. Read it if similar content already exists.
- [ ] Fetch the developer documentation Markdown source.
- [ ] Read the [Style guide](../../../docs/style-guide.md) and precedent files if any.

### 2. Draft the page

- [ ] Follow the guidance from the style guide.
- [ ] For each section to adapt, translate developer wording per the [Content style](../../../docs/style-guide.md#content-style) guidance.
- [ ] Include a screenshot placeholder where necessary:

  ```html
  <!-- TODO: screenshot - suggested alt: "<long descriptive alt text>" -->
  ```

### 3. Write the file(s) and report

- [ ] Save to the output path. Preserve any pre-existing human edits when merging.
- [ ] Lint the file by reading it back: H1 appears once, every H2 has at least one paragraph, every screenshot placeholder has suggested alt text.
- [ ] Report per the "Reporting" section above.
