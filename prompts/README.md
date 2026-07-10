# Website prompts

We use LLMs to help manage the site’s contents and experiment with the [Wagtail AI](content/https://wagtail.org/wagtail-ai/) package. The main goals are:

-   Increased automation for site upkeep. The site and its contents is very time-consuming to maintain, as it has to keep up with updates to Wagtail.
-   Increased reusability of the contents. We want the content to be simple to access in its original format but also reusable for custom guides.
-   Dogfooding with real-world content. Being able to work on Wagtail features that are only testable with real-world data and use cases.

In addition to AI integrations within Django/Wagtail, the project also uses [Promptfoo](https://www.promptfoo.dev/docs/intro/) to test its prompts with eval suites.

## llms.txt prompts

Use Promptfoo to check whether the project’s llms.txt content helps in answering common questions about the site.

```bash
promptfoo eval -c prompts/evals/llms-txt/llms-txt.yaml
```

## Wagtail AI prompts

```bash
promptfoo eval -c prompts/evals/page-meta.yaml
```

## Website contents

We version the site’s contents to simplify experimentation with different AI prompts. Run `./prompts/content/fetch_content.py && npm run format` to retrieve the latest copy.

### Versioned content

<!-- TOKEN_COUNTS_START -->

Token counts (gpt-oss-120b):

| File                                                                                                                  | Tokens |
| --------------------------------------------------------------------------------------------------------------------- | -----: |
| [llms.txt](content/en/llms.txt)                                                                                       |   2064 |
| [llms-full.txt](content/en/llms-full.txt)                                                                             |  35806 |
| [markdown.md](content/en/markdown.md)                                                                                 |    261 |
| [getting-started.md](content/en/getting-started.md)                                                                   |     49 |
| [getting-started/overview.md](content/en/getting-started/overview.md)                                                 |    528 |
| [how-to-guides.md](content/en/how-to-guides.md)                                                                       |     52 |
| [how-to-guides/find-your-way-around.md](content/en/how-to-guides/find-your-way-around.md)                             |   1745 |
| [how-to-guides/manage-pages.md](content/en/how-to-guides/manage-pages.md)                                             |   3425 |
| [how-to-guides/manage-documents.md](content/en/how-to-guides/manage-documents.md)                                     |    722 |
| [how-to-guides/manage-images.md](content/en/how-to-guides/manage-images.md)                                           |    947 |
| [how-to-guides/manage-snippets.md](content/en/how-to-guides/manage-snippets.md)                                       |    867 |
| [how-to-guides/manage-forms.md](content/en/how-to-guides/manage-forms.md)                                             |    653 |
| [how-to-guides/manage-collections.md](content/en/how-to-guides/manage-collections.md)                                 |    830 |
| [how-to-guides/manage-redirects.md](content/en/how-to-guides/manage-redirects.md)                                     |    735 |
| [how-to-guides/manage-users-and-roles.md](content/en/how-to-guides/manage-users-and-roles.md)                         |    679 |
| [how-to-guides/configure-workflows-for-moderation.md](content/en/how-to-guides/configure-workflows-for-moderation.md) |    997 |
| [how-to-guides/promote-search-results.md](content/en/how-to-guides/promote-search-results.md)                         |    723 |
| [concepts.md](content/en/concepts.md)                                                                                 |     74 |
| [concepts/wagtail-interfaces.md](content/en/concepts/wagtail-interfaces.md)                                           |   1007 |
| [concepts/pages.md](content/en/concepts/pages.md)                                                                     |    687 |
| [concepts/reports.md](content/en/concepts/reports.md)                                                                 |    798 |
| [concepts/users-status.md](content/en/concepts/users-status.md)                                                       |    319 |
| [concepts/page-status.md](content/en/concepts/page-status.md)                                                         |    551 |
| [concepts/accessibility-features.md](content/en/concepts/accessibility-features.md)                                   |   2189 |
| [concepts/scheduled-publishing.md](content/en/concepts/scheduled-publishing.md)                                       |    971 |
| [reference.md](content/en/reference.md)                                                                               |     61 |
| [reference/browser-compatibility.md](content/en/reference/browser-compatibility.md)                                   |    479 |
| [reference/content-checks.md](content/en/reference/content-checks.md)                                                 |    835 |
| [reference/account-settings.md](content/en/reference/account-settings.md)                                             |    873 |
| [releases.md](content/en/releases.md)                                                                                 |     49 |
| [releases/new-in-wagtail-7-4.md](content/en/releases/new-in-wagtail-7-4.md)                                           |   1278 |
| [releases/new-in-wagtail-7-3.md](content/en/releases/new-in-wagtail-7-3.md)                                           |   1036 |
| [releases/new-in-wagtail-7-2.md](content/en/releases/new-in-wagtail-7-2.md)                                           |    765 |
| [releases/new-in-wagtail-7-1.md](content/en/releases/new-in-wagtail-7-1.md)                                           |   1162 |
| [releases/new-in-wagtail-7-0.md](content/en/releases/new-in-wagtail-7-0.md)                                           |    542 |
| [releases/new-in-wagtail-6-4.md](content/en/releases/new-in-wagtail-6-4.md)                                           |    751 |
| [releases/new-in-wagtail-6-3.md](content/en/releases/new-in-wagtail-6-3.md)                                           |    806 |
| [releases/new-in-wagtail-6-2.md](content/en/releases/new-in-wagtail-6-2.md)                                           |    667 |
| [releases/new-in-wagtail-6-1.md](content/en/releases/new-in-wagtail-6-1.md)                                           |    722 |
| [releases/new-in-wagtail-6-0.md](content/en/releases/new-in-wagtail-6-0.md)                                           |    910 |
| [releases/new-in-wagtail-5-2.md](content/en/releases/new-in-wagtail-5-2.md)                                           |    769 |
| [releases/new-in-wagtail-5-1.md](content/en/releases/new-in-wagtail-5-1.md)                                           |    406 |
| [releases/new-in-wagtail-5-0.md](content/en/releases/new-in-wagtail-5-0.md)                                           |    469 |
| [releases/new-in-wagtail-4-2.md](content/en/releases/new-in-wagtail-4-2.md)                                           |    878 |
| [releases/new-in-wagtail-4-1.md](content/en/releases/new-in-wagtail-4-1.md)                                           |   1909 |
| [about.md](content/en/about.md)                                                                                       |    427 |

<!-- TOKEN_COUNTS_END -->
