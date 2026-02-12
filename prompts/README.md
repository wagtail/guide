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

| File                                                                                                                         | Tokens |
| ---------------------------------------------------------------------------------------------------------------------------- | -----: |
| [llms.txt](content/en-latest/llms.txt)                                                                                       |   2168 |
| [llms-full.txt](content/en-latest/llms-full.txt)                                                                             |  36705 |
| [markdown.md](content/en-latest/markdown.md)                                                                                 |    271 |
| [getting-started.md](content/en-latest/getting-started.md)                                                                   |     51 |
| [getting-started/overview.md](content/en-latest/getting-started/overview.md)                                                 |    534 |
| [how-to-guides.md](content/en-latest/how-to-guides.md)                                                                       |     54 |
| [how-to-guides/find-your-way-around.md](content/en-latest/how-to-guides/find-your-way-around.md)                             |   1751 |
| [how-to-guides/manage-pages.md](content/en-latest/how-to-guides/manage-pages.md)                                             |   3362 |
| [how-to-guides/manage-documents.md](content/en-latest/how-to-guides/manage-documents.md)                                     |    738 |
| [how-to-guides/manage-images.md](content/en-latest/how-to-guides/manage-images.md)                                           |    959 |
| [how-to-guides/manage-snippets.md](content/en-latest/how-to-guides/manage-snippets.md)                                       |    881 |
| [how-to-guides/manage-forms.md](content/en-latest/how-to-guides/manage-forms.md)                                             |    657 |
| [how-to-guides/manage-collections.md](content/en-latest/how-to-guides/manage-collections.md)                                 |    844 |
| [how-to-guides/manage-redirects.md](content/en-latest/how-to-guides/manage-redirects.md)                                     |    743 |
| [how-to-guides/manage-users-and-roles.md](content/en-latest/how-to-guides/manage-users-and-roles.md)                         |    701 |
| [how-to-guides/configure-workflows-for-moderation.md](content/en-latest/how-to-guides/configure-workflows-for-moderation.md) |   1011 |
| [how-to-guides/promote-search-results.md](content/en-latest/how-to-guides/promote-search-results.md)                         |    729 |
| [concepts.md](content/en-latest/concepts.md)                                                                                 |     76 |
| [concepts/wagtail-interfaces.md](content/en-latest/concepts/wagtail-interfaces.md)                                           |   1037 |
| [concepts/pages.md](content/en-latest/concepts/pages.md)                                                                     |    697 |
| [concepts/reports.md](content/en-latest/concepts/reports.md)                                                                 |    834 |
| [concepts/users-status.md](content/en-latest/concepts/users-status.md)                                                       |    329 |
| [concepts/page-status.md](content/en-latest/concepts/page-status.md)                                                         |    561 |
| [concepts/accessibility-features.md](content/en-latest/concepts/accessibility-features.md)                                   |   2205 |
| [concepts/scheduled-publishing.md](content/en-latest/concepts/scheduled-publishing.md)                                       |    979 |
| [reference.md](content/en-latest/reference.md)                                                                               |     63 |
| [reference/browser-compatibility.md](content/en-latest/reference/browser-compatibility.md)                                   |    481 |
| [reference/content-checks.md](content/en-latest/reference/content-checks.md)                                                 |    746 |
| [reference/account-settings.md](content/en-latest/reference/account-settings.md)                                             |    871 |
| [releases.md](content/en-latest/releases.md)                                                                                 |     51 |
| [releases/new-in-wagtail-7-3.md](content/en-latest/releases/new-in-wagtail-7-3.md)                                           |   1039 |
| [releases/new-in-wagtail-7-2.md](content/en-latest/releases/new-in-wagtail-7-2.md)                                           |    766 |
| [releases/new-in-wagtail-7-1.md](content/en-latest/releases/new-in-wagtail-7-1.md)                                           |   1170 |
| [releases/new-in-wagtail-7-0.md](content/en-latest/releases/new-in-wagtail-7-0.md)                                           |    544 |
| [releases/new-in-wagtail-6-4.md](content/en-latest/releases/new-in-wagtail-6-4.md)                                           |    753 |
| [releases/new-in-wagtail-6-3.md](content/en-latest/releases/new-in-wagtail-6-3.md)                                           |    808 |
| [releases/new-in-wagtail-6-2.md](content/en-latest/releases/new-in-wagtail-6-2.md)                                           |    671 |
| [releases/new-in-wagtail-6-1.md](content/en-latest/releases/new-in-wagtail-6-1.md)                                           |    726 |
| [releases/new-in-wagtail-6-0.md](content/en-latest/releases/new-in-wagtail-6-0.md)                                           |    916 |
| [releases/new-in-wagtail-5-2.md](content/en-latest/releases/new-in-wagtail-5-2.md)                                           |    771 |
| [releases/new-in-wagtail-5-1.md](content/en-latest/releases/new-in-wagtail-5-1.md)                                           |    410 |
| [releases/new-in-wagtail-5-0.md](content/en-latest/releases/new-in-wagtail-5-0.md)                                           |    471 |
| [releases/new-in-wagtail-4-2.md](content/en-latest/releases/new-in-wagtail-4-2.md)                                           |    884 |
| [releases/new-in-wagtail-4-1.md](content/en-latest/releases/new-in-wagtail-4-1.md)                                           |   1911 |
| [about.md](content/en-latest/about.md)                                                                                       |    429 |
| [about/contributing.md](content/en-latest/about/contributing.md)                                                             |   2092 |

<!-- TOKEN_COUNTS_END -->
