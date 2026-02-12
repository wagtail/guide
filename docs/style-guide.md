# Documentation style guide

This style guide defines the standard we are aiming for across the Wagtail User Guide. Use it as the default for all new content and when revising existing pages.

## Design goals

-   Content is clear, concise, and easy to scan.
-   Guidance is inclusive, respectful, and accessible to non-technical audiences.
-   Terminology and structure stay consistent across the whole guide.
-   Where possible, strive for [timeless documentation](https://developers.google.com/style/timeless-documentation). Use wording that survives UI and product changes.

## Tone of voice

We write in a **conversational-instructional** tone: friendly and approachable, focused on helping the reader accomplish a task or understand a concept.

-   We address the reader directly as "you" and "your" (second person).
-   We use "we" to represent the Wagtail project or the documentation team, never the reader. For example: "We calculate the number of words present in the plain text content."
-   Contractions are used freely: "it's", "you'll", "don't", "won't", "can't".
-   We avoid overly formal or academic phrasing. Sentences stay direct and plain.

### Celebratory micro-copy

Use a brief congratulatory line at the end of a complete multi-step procedure when it reinforces progress.

-   Keep it to one sentence.
-   Prefer warm, straightforward language.
-   Avoid jokes and pop-culture references in instructional content.
-   Release notes can be slightly more energetic, but clarity and factual accuracy come first.

## Target audience

The guide is written for **CMS users**: content editors, moderators, and administrators. People who use Wagtail but do not write code for it.

-   We do not assume technical knowledge. When a feature depends on developer configuration, we say so explicitly: "developers can configure available page types when building the site."
-   When a feature may look different due to site customization, we flag it: "It's also possible that features in the **Reports** section of your Admin interface are different from the default features. This is because Wagtail is highly customizable. If this is the case, contact your web developer for more information."
-   When we link to the Wagtail developer documentation, we frame it as a resource for a different audience or for the reader to pass along: "For developer documentation, see [Form builder in the developer docs](https://docs.wagtail.org/)."

## Content structure

The site uses a very simple structure where all pages are of the same type, though they end up being used differently.

### Content pages

All pages start with an opening paragraph, followed with sections of content. Sections and sub-sections consistently use heading levels, which are very useful for in-page navigation.

### Section index pages

Top-level section pages (Concepts, How-to guides, Getting started, Releases, Reference) are concise navigation entry points. Keep them small with a short orientation paragraph. The pages will auto-generate links to all child pages within their section.

### Screenshots

Screenshots are embedded inline with the relevant text. We use long, descriptive alt text that narrates the visual content of the image, for example:

Example alt text: "Breads page listing with expanded three dots Actions menu in the header showing seven different page actions. 'Add child page' is highlighted in red."

Screenshots are placed inline between explanatory paragraphs, directly after the text that describes what the screenshot shows.

### Horizontal separators

We use horizontal separators sparingly to separate major thematic breaks within a single page, such as between the main content and a closing call-to-action section.

## Links

The guide is heavily cross-referenced with inline links. On first or prominent mention, key terms like "Admin interface", "Sidebar", and "Explorer page" link to their definition pages. Repeat links only when it improves scanning in longer sections.

We use external links more sparingly, with a strong preference for official Wagtail resources: the `wagtail.org` marketing site, or the `docs.wagtail.org` developer documentation.

## Headings and titles

-   **H1** is used exactly once per page, for the page title.
-   **H2** is the primary sectioning level within a page.
-   **H3** is used for sub-sections within an H2.
-   Headings use sentence case: "Manage page history", not "Manage Page History".
-   Heading text is plain. Do not apply extra emphasis styling inside heading text.
-   Avoid adding links inside headings, they are harder to identify for screen reader users.
-   How-to guides use H2 for each major task: "Create new pages", "Edit existing pages", "Copy pages". Verb-first phrasing is the norm for task headings.

## UI references and examples

The guide does not contain programming code examples — it is written for CMS users, not developers.

### Button and menu labels

UI element names are formatted in **bold**: **Add**, **Save**, **Delete**, **Publish**, **Actions**.

### Navigation paths

Multi-step navigation paths use **bold** for each element and a right-angle separator:

> Go to **Settings > Workflows** from the Sidebar.

### Field names and status values

CMS field names and status/state values are formatted in _italics_: _Draft_, _Live_, _go-live at_, _expire at_, _root collection_, _Permanent_.

### Keyboard shortcuts

Keyboard shortcuts are presented with platform variants separated by a slash. Modifier keys use symbols for macOS and words for Windows:

-   **Ctrl + S** / **⌘ + S**
-   **Ctrl + Alt + M** / **⌘ + ⌥ + M**

## Terminology and language choices

### Spelling

### Canonical terms

We use these specific terms consistently across the guide:

| Term                | Usage                                                                       |
| ------------------- | --------------------------------------------------------------------------- |
| **Admin interface** | The entire Wagtail content management portal. Capitalized as a proper noun. |
| **Sidebar**         | The left-hand navigation menu. Always capitalized.                          |
| **Edit screen**     | Any screen from which you edit content (pages, snippets, images, etc.).     |
| **Explorer page**   | The page tree navigation view showing a page's children.                    |
| **Dashboard**       | The main hub you see after logging in. Always capitalized.                  |

Use these terms with consistent capitalization whenever they refer to these concepts.

### Modal verbs

-   Use **"can"** for capability: "You can access your settings by clicking on your username."
-   Use **"may"** for possibility or permission: "You may find that some fields are uneditable."
-   Reserve **"must"** for hard requirements.
-   Use **"should"** for recommendations.

### Referring to the reader

We say "you" and "your". We do not say "the user" when addressing the reader. "Users" as a noun refers to other people in the CMS (e.g., "users with the right permissions").

### Referring to developers

When something depends on developer configuration, we use phrases like:

-   "Developers configure available page types when building the site."
-   "Contact your web developer for more information."
-   "For developer documentation, see [link]."

### Customizability caveat

We document Wagtail’s default configuration, with no customizations. When a feature may differ from the defaults, we use a recognizable pattern: "This is because Wagtail is highly customizable. If this is the case, contact your web developer for more information."

## Warnings, notes, and edge cases

We occasionally format text as a "Note" or "Warning" as standalone paragraphs, directly after the relevant section.

-   **Note:** for supplementary information, caveats, or things the reader should keep in mind.
-   **Warning:** for destructive or irreversible actions, or information about security/data-loss risks.

Keep this special formatting to a minimum, when the noted information directly impacts task completion. For softer caveats, we introduce them with phrases like:

-   "It's also possible that…"
-   "Keep in mind that…"
-   "Note that…"

## Release notes guidance

The "New in Wagtail X.Y" pages are derived from the [developer docs release notes](https://docs.wagtail.org/en/stable/releases/index.html), converted to make them more suitable for an audience of CMS users. Their content diverges from the rest of the style guide in a few respects. They’re intended to represent a "point in time", not a timeless record.

They follow a set structure: one section per "headline feature" in the release notes that has value for CMS users, then one "Other UI improvements" section with new features and bug fixes that are relevant for those users but didn’t get highlighted in the developer notes. Optionally a "Feedback requests" section for specific calls to action. And finally, wrap up the content with evergreen calls to action related to awareness of future features: view the [Wagtail roadmap](https://wagtail.org/roadmap/), subscribe to the [Wagtail newsletter](https://wagtail.org/newsletter/).

Release notes should generally always come with updates to the rest of the documentation to acknowledge the new features. Link to those sections whenever possible. Consider also linking to explanatory content on the main wagtail.org site.

### Structure

-   Include screenshots or visual examples to illustrate every improvement.
-   Provide concise, user-friendly summaries (ideally one to two sentences per feature).
-   Link to full technical release notes where appropriate.

### Content style

-   Replace technical jargon with plain language, using a neutral tone overall.
-   Describe functionality clearly from the user's perspective.
-   Clearly state how changes benefit or affect the user's workflow or experience.
