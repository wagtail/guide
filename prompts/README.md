# Website prompts

We use LLMs to help manage the site’s contents and experiment with the [Wagtail AI](https://wagtail.org/wagtail-ai/) package. The main goals are:

- Increased automation for site upkeep. The site and its contents is very time-consuming to maintain, as it has to keep up with updates to Wagtail.
- Increased reusability of the contents. We want the content to be simple to access in its original format but also reusable for custom guides.
- Dogfooding with real-world content. Being able to work on Wagtail features that are only testable with real-world data and use cases.

## Website contents

We version the site’s contents to simplify experimentation with different AI prompts. Run `./prompts/content/fetch_content.py && npm run format` to retrieve the latest copy.

### Versioned content

<!-- TOKEN_COUNTS_START -->

Token counts (gpt-oss-120b):

| File                                                                                                                 | Tokens |
| -------------------------------------------------------------------------------------------------------------------- | -----: |
| [llms.txt](en-latest/llms.txt)                                                                                       |   2168 |
| [llms-full.txt](en-latest/llms-full.txt)                                                                             |  36705 |
| [markdown.md](en-latest/markdown.md)                                                                                 |    271 |
| [getting-started.md](en-latest/getting-started.md)                                                                   |     51 |
| [getting-started/overview.md](en-latest/getting-started/overview.md)                                                 |    534 |
| [how-to-guides.md](en-latest/how-to-guides.md)                                                                       |     54 |
| [how-to-guides/find-your-way-around.md](en-latest/how-to-guides/find-your-way-around.md)                             |   1751 |
| [how-to-guides/manage-pages.md](en-latest/how-to-guides/manage-pages.md)                                             |   3362 |
| [how-to-guides/manage-documents.md](en-latest/how-to-guides/manage-documents.md)                                     |    738 |
| [how-to-guides/manage-images.md](en-latest/how-to-guides/manage-images.md)                                           |    959 |
| [how-to-guides/manage-snippets.md](en-latest/how-to-guides/manage-snippets.md)                                       |    881 |
| [how-to-guides/manage-forms.md](en-latest/how-to-guides/manage-forms.md)                                             |    657 |
| [how-to-guides/manage-collections.md](en-latest/how-to-guides/manage-collections.md)                                 |    844 |
| [how-to-guides/manage-redirects.md](en-latest/how-to-guides/manage-redirects.md)                                     |    743 |
| [how-to-guides/manage-users-and-roles.md](en-latest/how-to-guides/manage-users-and-roles.md)                         |    701 |
| [how-to-guides/configure-workflows-for-moderation.md](en-latest/how-to-guides/configure-workflows-for-moderation.md) |   1011 |
| [how-to-guides/promote-search-results.md](en-latest/how-to-guides/promote-search-results.md)                         |    729 |
| [concepts.md](en-latest/concepts.md)                                                                                 |     76 |
| [concepts/wagtail-interfaces.md](en-latest/concepts/wagtail-interfaces.md)                                           |   1037 |
| [concepts/pages.md](en-latest/concepts/pages.md)                                                                     |    697 |
| [concepts/reports.md](en-latest/concepts/reports.md)                                                                 |    834 |
| [concepts/users-status.md](en-latest/concepts/users-status.md)                                                       |    329 |
| [concepts/page-status.md](en-latest/concepts/page-status.md)                                                         |    561 |
| [concepts/accessibility-features.md](en-latest/concepts/accessibility-features.md)                                   |   2205 |
| [concepts/scheduled-publishing.md](en-latest/concepts/scheduled-publishing.md)                                       |    979 |
| [reference.md](en-latest/reference.md)                                                                               |     63 |
| [reference/browser-compatibility.md](en-latest/reference/browser-compatibility.md)                                   |    481 |
| [reference/content-checks.md](en-latest/reference/content-checks.md)                                                 |    746 |
| [reference/account-settings.md](en-latest/reference/account-settings.md)                                             |    871 |
| [releases.md](en-latest/releases.md)                                                                                 |     51 |
| [releases/new-in-wagtail-7-3.md](en-latest/releases/new-in-wagtail-7-3.md)                                           |   1039 |
| [releases/new-in-wagtail-7-2.md](en-latest/releases/new-in-wagtail-7-2.md)                                           |    766 |
| [releases/new-in-wagtail-7-1.md](en-latest/releases/new-in-wagtail-7-1.md)                                           |   1170 |
| [releases/new-in-wagtail-7-0.md](en-latest/releases/new-in-wagtail-7-0.md)                                           |    544 |
| [releases/new-in-wagtail-6-4.md](en-latest/releases/new-in-wagtail-6-4.md)                                           |    753 |
| [releases/new-in-wagtail-6-3.md](en-latest/releases/new-in-wagtail-6-3.md)                                           |    808 |
| [releases/new-in-wagtail-6-2.md](en-latest/releases/new-in-wagtail-6-2.md)                                           |    671 |
| [releases/new-in-wagtail-6-1.md](en-latest/releases/new-in-wagtail-6-1.md)                                           |    726 |
| [releases/new-in-wagtail-6-0.md](en-latest/releases/new-in-wagtail-6-0.md)                                           |    916 |
| [releases/new-in-wagtail-5-2.md](en-latest/releases/new-in-wagtail-5-2.md)                                           |    771 |
| [releases/new-in-wagtail-5-1.md](en-latest/releases/new-in-wagtail-5-1.md)                                           |    410 |
| [releases/new-in-wagtail-5-0.md](en-latest/releases/new-in-wagtail-5-0.md)                                           |    471 |
| [releases/new-in-wagtail-4-2.md](en-latest/releases/new-in-wagtail-4-2.md)                                           |    884 |
| [releases/new-in-wagtail-4-1.md](en-latest/releases/new-in-wagtail-4-1.md)                                           |   1911 |
| [about.md](en-latest/about.md)                                                                                       |    429 |
| [about/contributing.md](en-latest/about/contributing.md)                                                             |   2092 |

<!-- TOKEN_COUNTS_END -->
