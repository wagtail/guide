# New in Wagtail 7.0

Page URL: https://guide.wagtail.org/en-latest/releases/new-in-wagtail-7-0/

Here are highlights from Wagtail 7.0. For more details 👉️ view the full [v7.0 release notes](https://docs.wagtail.org/en/latest/releases/7.0.html).

## Deferred validation for drafts

Pages (and snippets with draft support) now allow users to save work-in-progress versions with more of the fields left empty, even if they might be marked as required. Validation is applied as normal when the page or snippet is published, scheduled, or submitted to a workflow. This is an important stepping stone towards future [auto-save support](https://github.com/wagtail/roadmap/issues/24), for which we are looking for a [feature sponsor](https://wagtail.org/sponsor/).

## New and improved pagination

All listing views and most choosers now use a more advanced pagination feature, so users can more easily navigate to a specific page.

![Pagination controls in redirects](https://guide-media.wagtail.org/images/Pagination_controls_in_redirects.width-900.png)

## Locale in listings and choosers

This release adds a new "Locale" column to the listings and choosers of translatable models, making it easier to filter and sort by locale.

![Locale in snippets listings](https://guide-media.wagtail.org/images/Locale_in_snippets_listings.width-900.png)

The current content's locale is applied in choosers by default, with the ability to clear the locale filter.

![Locale in page chooser](https://guide-media.wagtail.org/images/Locale_in_page_chooser.width-900.png)

## Additional user interface improvements

Here are smaller improvements which will make users’ lives better in the administration interface.

-   Pages can now be configured by developers to be private by default.
-   More of the rich text fields’ user interface labels are now translated.
-   The Keyboard shortcuts viewer under "Help" now documents the shortcut to add comments.

![Keyboard shortcuts panel within the Help menu](https://guide-media.wagtail.org/images/Keyboard_shortcuts_panel_within_the_Help_menu.width-900.png)

---

To learn about future enhancements ahead of time 👉️ check out the [Wagtail roadmap](https://wagtail.org/roadmap/), our [newsletter](https://wagtail.org/newsletter/), or read [Keeping up with upcoming changes in Wagtail](https://wagtail.org/blog/keeping-up-with-upcoming-changes-in-wagtail/).
