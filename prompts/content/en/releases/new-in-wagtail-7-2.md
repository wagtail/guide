# New in Wagtail 7.2

Page URL: https://guide.wagtail.org/en-latest/releases/new-in-wagtail-7-2/

Here are highlights from Wagtail 7.2. For more details, view the full [v7.2 release notes](https://docs.wagtail.org/en/latest/releases/7.2.html).

## Reordering support for snippets

![Snippets listing for countries with manual reordering support](https://guide-media.wagtail.org/images/Snippets_listing_for_countries_with_manual_reo.width-900.png)

Snippet listings now support reordering of items using drag-and-drop, similarly to pages. Once enabled by a developer, this becomes available in the listing’s "Actions". The order of items will then reflect on the website where enabled.

## Media listings improvements

![Images listing with header and images list](https://guide-media.wagtail.org/images/Images_listing_with_header_and_images_list_dsC.width-900.png)

Admin and document listings now support filtering by usage count. Image choosers now have both grid and list layouts, with a new toggle for users to switch between the two. The new toggle has also been added to standalone image listings for consistency.

## Readability score metric

![Page editor for "Bread and Circuses" page. The form to the left, and to the right the Checks side panel is expanded, showing different metrics about the page](https://guide-media.wagtail.org/images/Page_editor_for_22Bread_and_Circuses22_page._T.width-900.png)

Built-in [content checks](https://guide.wagtail.org/en-latest/reference/content-checks/) now include a readability score, based on length of words and sentences in the page content. The content metrics also now provide an explainer panel detailing how they are calculated.

## Quick access to first validation error

![Validation error message on page publish with go to first error shortcut button](https://guide-media.wagtail.org/images/Validation_error_message_on_page_publish_with_.width-900.png)

Error messages for form validation errors now contain a “Go to the first error” shortcut button. This speeds up navigating to address error messages, particularly for forms split between multiple tabs, where the errors can be hard to locate.

## Keyboard shortcuts improvements

![Keyboard shortcuts dialog](https://guide-media.wagtail.org/images/Keyboard_shortcuts_dialog_tWoC6ww.width-900.png)

We introduce two new shortcuts, ? to open the keyboard shortcuts dialog, and / to focus the search input in the sidebar. The keyboard shortcuts dialog has been reorganized into better categories. when keyboard shortcuts are disabled in user preferences, the “add comment” shortcut is also disabled, and messaging has been added to the keyboard shortcuts dialog to indicate the status of keyboard shortcuts and how to enable or disable them via user preferences.

---

To learn about future enhancements ahead of time 👉️ check out the [Wagtail roadmap](https://wagtail.org/roadmap/), our [weekly newsletter](https://wagtail.org/newsletter/), or read [Keeping up with upcoming changes in Wagtail](https://wagtail.org/blog/keeping-up-with-upcoming-changes-in-wagtail/).

## Other UI improvements

-   We now support calculating content metrics without opening the preview panel.
-   The rich text toolbar now always shows above form action buttons.
-   We now use more consistent sentence format for error message.

## Feedback requests

Do you use Wagtail on a tablet or smartphone? Please let us know more about what you do and how well it works on our [mobile support discussion thread](https://github.com/wagtail/wagtail/discussions/13273).
