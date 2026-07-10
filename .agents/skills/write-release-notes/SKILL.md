---
name: write-release-notes
description: Write a "New in Wagtail X.Y" release page for the User Guide, derived from the developer release notes.
license: MIT
metadata:
    audience: maintainers
    internal: true
    disable-model-invocation: true
---

## Overview

Generate a CMS-user-facing release page from the official Wagtail developer release notes. The output is a Markdown file ready for review and screenshot insertion, following the [release notes guidance](../../../docs/style-guide.md#release-notes-guidance) in the style guide.

Usage:

-   `/write-release-notes for v7.4`
-   `/write-release-notes for the latest release`

## Methodology

### Goals

-   Produce a single Markdown file at `prompts/content/en/releases/new-in-wagtail-<X-Y>.md`, following the page template, structure, exclusion rules, and tone defined in the style guide.
-   Translate the developer release notes into plain language for content editors, moderators, and administrators who use Wagtail but don't write code for it.
-   Suggest other documentation changes and internal links to existing or newly-introduced docs.

### Guardrails

-   Don't invent feature names, version numbers, contributors, release dates, or screenshot URLs — pull them from the developer release notes or leave a `<!-- TODO: screenshot - alt: ... -->` placeholder for the user to fill in.
-   Don't open a PR or commit. The skill ends with a file on disk for the user to review and add screenshots to.

### Inputs

To detect from the context or request from the user if unclear:

-   **Target version** as `X.Y` (e.g. `7.4`). Default: ask the user, or resolve "latest" via the [release schedule](https://github.com/wagtail/wagtail/wiki/Release-schedule).
-   **Existing draft**. If the output file already exists, read it first and treat it as a starting point — preserve human edits (custom phrasing, screenshot URLs already filled in) rather than overwriting blindly.

### Reference data sources

Always fetch the latest information from the canonical sources rather than relying on local caches.

-   **Style guide**: [Release notes guidance](../../../docs/style-guide.md#release-notes-guidance) — the source of truth for page structure, tone, what to include/exclude, and how to translate developer jargon.
-   **Developer release notes**: `https://docs.wagtail.org/en/latest/releases/<X.Y>.html.md`.
-   **Recent precedents**: `prompts/content/en/releases/new-in-wagtail-<previous>.md` — read at least the two most recent for tone calibration.
-   **User guide pages worth linking to**: search `prompts/content/en/` for destinations matching each new feature. Feel free to suggest documentation changes to link to.

### Reporting

After writing the file, report:

-   The output path and the release notes URL fetched.
-   Each headline feature included, with one-line rationale.
-   Each developer-notes item that was deliberately excluded, grouped by reason (security / maintenance / deprecation / developer-only API / unclear user value).
-   Every `<!-- TODO: screenshot -->` marker, with suggested alt text.
-   Every internal link suggestion to documentation that needs to be created.
-   Suggested follow-ups: user guide pages under `prompts/content/en/` that may need updates to acknowledge the new features.

## Steps

### 1. Resolve the target version and gather sources

-   [ ] Confirm the target version with the user, or resolve "latest" via the [release schedule](https://github.com/wagtail/wagtail/wiki/Release-schedule).
-   [ ] Compute the output filename: `prompts/content/en/releases/new-in-wagtail-<X-Y>.md` (dash separator, not dot). Read it if it already exists.
-   [ ] Fetch the developer release notes Markdown source. Detect LTS designation by looking for "(LTS)" in the page title.
-   [ ] Read the [Release notes guidance](../../../docs/style-guide.md#release-notes-guidance) section of the style guide and the two most recent precedent files.

### 2. Categorize every item from the developer release notes

For each entry under "What's new", "Other features", and "Bug fixes", apply the [include/exclude rules](../../../docs/style-guide.md#what-to-include-and-exclude) from the style guide:

-   [ ] **Headline section**: significant features with CMS-user value, each becoming an H2.
-   [ ] **Other-improvements bullet**: smaller user-visible changes.
-   [ ] **Excluded**: record the reason for the report.

### 3. Draft the page

-   [ ] Follow the guidance from the style guide. Preserve the closing call-to-action paragraph wording from past release pages as a starter.
-   [ ] For each headline H2, write 1–2 sentences from the user's perspective, translating developer wording per the [Content style](../../../docs/style-guide.md#content-style) guidance.
-   [ ] Include a screenshot placeholder near the top of every headline section:

    ```html
    <!-- TODO: screenshot - suggested alt: "<long descriptive alt text>" -->
    ```

-   [ ] Build "Other UI improvements" as a short bullet list ordered by user impact.
-   [ ] Add "Feedback requests" only if the developer notes link to an active discussion or feedback channel.
-   [ ] For LTS releases, add a single sentence to the opening paragraph noting LTS status.

### 4. Write the file and report

-   [ ] Save to the output path. Preserve any pre-existing human edits when merging.
-   [ ] Lint the file by reading it back: H1 appears once, every H2 has at least one paragraph, every screenshot placeholder has suggested alt text, the closing call-to-action paragraph matches the established wording, and `<X.Y>` placeholders are all replaced.
-   [ ] Report per the "Reporting" section above.
