# Website prompts

We use LLMs to help manage the site’s contents and experiment with the [Wagtail AI](content/https://wagtail.org/wagtail-ai/) package. The main goals are:

- Increased automation for site upkeep. The site and its contents is very time-consuming to maintain, as it has to keep up with updates to Wagtail.
- Increased reusability of the contents. We want the content to be simple to access in its original format but also reusable for custom guides.
- Dogfooding with real-world content. Being able to work on Wagtail features that are only testable with real-world data and use cases.

In addition to AI integrations within Django/Wagtail, the project also uses [Promptfoo](https://www.promptfoo.dev/docs/intro/) to test its prompts with eval suites.

## llms.txt prompts

Use Promptfoo to check whether the project’s llms.txt content helps in answering common questions about the site.

```bash
promptfoo eval -c content/evals/llms-txt/llms-txt.yaml
```

## Wagtail AI prompts

```bash
promptfoo eval -c content/evals/page-meta.yaml
```

## Website contents

We version the site’s contents to simplify experimentation with different AI prompts. Run `./content/fetch_content.py && npm run format` to retrieve the latest copy.

### Versioned content

<!-- TOKEN_COUNTS_START -->

Last updated: 2026-10-05, token counts (gpt-oss-120b):

| File                                                                                                                          | Tokens |
| ----------------------------------------------------------------------------------------------------------------------------- | -----: |
| [llms.txt](content/en/llms.txt)                                                                                               |   2601 |
| [index.md](content/en/index.md)                                                                                               |  34366 |
| [markdown.md](content/en/markdown.md)                                                                                         |    358 |
| [getting-started.md](content/en/getting-started.md)                                                                           |     85 |
| [getting-started/overview.md](content/en/getting-started/overview.md)                                                         |    590 |
| [how-to-guides.md](content/en/how-to-guides.md)                                                                               |     90 |
| [how-to-guides/find-your-way-around.md](content/en/how-to-guides/find-your-way-around.md)                                     |   1798 |
| [how-to-guides/manage-pages.md](content/en/how-to-guides/manage-pages.md)                                                     |   3463 |
| [how-to-guides/manage-documents.md](content/en/how-to-guides/manage-documents.md)                                             |    763 |
| [how-to-guides/manage-images.md](content/en/how-to-guides/manage-images.md)                                                   |    996 |
| [how-to-guides/manage-snippets.md](content/en/how-to-guides/manage-snippets.md)                                               |    907 |
| [how-to-guides/manage-forms.md](content/en/how-to-guides/manage-forms.md)                                                     |    672 |
| [how-to-guides/manage-collections.md](content/en/how-to-guides/manage-collections.md)                                         |    875 |
| [how-to-guides/manage-redirects.md](content/en/how-to-guides/manage-redirects.md)                                             |    783 |
| [how-to-guides/manage-users-and-roles.md](content/en/how-to-guides/manage-users-and-roles.md)                                 |    720 |
| [how-to-guides/configure-workflows-for-moderation.md](content/en/how-to-guides/configure-workflows-for-moderation.md)         |   1072 |
| [how-to-guides/promote-search-results.md](content/en/how-to-guides/promote-search-results.md)                                 |    779 |
| [concepts.md](content/en/concepts.md)                                                                                         |    127 |
| [concepts/wagtail-interfaces.md](content/en/concepts/wagtail-interfaces.md)                                                   |   1070 |
| [concepts/pages.md](content/en/concepts/pages.md)                                                                             |    762 |
| [concepts/reports.md](content/en/concepts/reports.md)                                                                         |    876 |
| [concepts/users-status.md](content/en/concepts/users-status.md)                                                               |    375 |
| [concepts/page-status.md](content/en/concepts/page-status.md)                                                                 |    597 |
| [concepts/accessibility-features.md](content/en/concepts/accessibility-features.md)                                           |   2193 |
| [concepts/scheduled-publishing.md](content/en/concepts/scheduled-publishing.md)                                               |    990 |
| [reference.md](content/en/reference.md)                                                                                       |     98 |
| [reference/browser-compatibility.md](content/en/reference/browser-compatibility.md)                                           |    519 |
| [reference/content-checks.md](content/en/reference/content-checks.md)                                                         |    936 |
| [reference/account-settings.md](content/en/reference/account-settings.md)                                                     |    914 |
| [releases.md](content/en/releases.md)                                                                                         |     87 |
| [releases/new-in-wagtail-8-0.md](content/en/releases/new-in-wagtail-8-0.md)                                                   |   1062 |
| [releases/new-in-wagtail-7-4.md](content/en/releases/new-in-wagtail-7-4.md)                                                   |   1339 |
| [releases/new-in-wagtail-7-3.md](content/en/releases/new-in-wagtail-7-3.md)                                                   |   1125 |
| [releases/new-in-wagtail-7-2.md](content/en/releases/new-in-wagtail-7-2.md)                                                   |    783 |
| [releases/new-in-wagtail-7-1.md](content/en/releases/new-in-wagtail-7-1.md)                                                   |   1190 |
| [releases/new-in-wagtail-7-0.md](content/en/releases/new-in-wagtail-7-0.md)                                                   |    568 |
| [releases/new-in-wagtail-6-4.md](content/en/releases/new-in-wagtail-6-4.md)                                                   |    769 |
| [releases/new-in-wagtail-6-3.md](content/en/releases/new-in-wagtail-6-3.md)                                                   |    850 |
| [releases/new-in-wagtail-6-2.md](content/en/releases/new-in-wagtail-6-2.md)                                                   |    711 |
| [releases/new-in-wagtail-6-1.md](content/en/releases/new-in-wagtail-6-1.md)                                                   |    746 |
| [releases/new-in-wagtail-6-0.md](content/en/releases/new-in-wagtail-6-0.md)                                                   |    936 |
| [releases/new-in-wagtail-5-2.md](content/en/releases/new-in-wagtail-5-2.md)                                                   |    795 |
| [releases/new-in-wagtail-5-1.md](content/en/releases/new-in-wagtail-5-1.md)                                                   |    461 |
| [releases/new-in-wagtail-5-0.md](content/en/releases/new-in-wagtail-5-0.md)                                                   |    524 |
| [releases/new-in-wagtail-4-2.md](content/en/releases/new-in-wagtail-4-2.md)                                                   |    962 |
| [releases/new-in-wagtail-4-1.md](content/en/releases/new-in-wagtail-4-1.md)                                                   |   1983 |
| [about.md](content/en/about.md)                                                                                               |    494 |
| [llms-full.txt](content/en/llms-full.txt)                                                                                     |  36874 |
| [.well-known/agent-skills/wagtail-guide-support/SKILL.md](content/en/.well-known/agent-skills/wagtail-guide-support/SKILL.md) |    286 |
| [.well-known/agent-skills/index.json](content/en/.well-known/agent-skills/index.json)                                         |    184 |

<!-- TOKEN_COUNTS_END -->
