# New in Wagtail 6.4

Page URL: https://guide.wagtail.org/en-latest/releases/new-in-wagtail-6-4/

Here are highlights from Wagtail 6.4. For more details 👉️ view the full [v6.4 release notes](https://docs.wagtail.org/en/stable/releases/6.4.html).

### Previews for StreamField Blocks

![Block chooser in StreamField, with a block being previewed](https://guide-media.wagtail.org/images/block_chooser_and_preview_focus.width-900.png)

Previews for StreamField blocks are now available. Once configured by a developer, previews appear in the block chooser next to the available options to help editors make informed decisions when selecting blocks. Blocks also supporting having a description, to document their usage alongside or instead of the preview.

### Alt text management enhancements

![Alt text accessibility checker](https://guide-media.wagtail.org/images/Alt_text_accessibility_checker.width-900.png)

Improvements to alt text handling include:

-   **Default alt text for Image block**: When selecting a new image, Wagtail’s default Image block now automatically populates its contextual alt text using the image's description if set. This can also be configured by developers to retrieve alt text from a different field than the description.
-   **Alt text quality check**: Alt text quality checks are now enabled by default, picking up common problem patterns like file names in alt text

### Drag-and-drop reordering for StreamField

StreamField blocks now support drag-and-drop reordering of items within a field. This enhancement simplifies content changes, particularly for fields containing a large number of items. To use this feature, collapse the block or keep it open – then use the drag handle to move the block up or down.

![Authors block with two Authors child items each containing a People field The first blocks controls to the right are highlighted in red](https://guide-media.wagtail.org/images/Authors_block_with_two_Authors_child_items_eac.width-900.png)

This is also supported for other types of orderable content, such as form fields in the Wagtail form builder or items in promoted search results.

### Search terms report

![Search terms report, with 4 terms displayed](https://guide-media.wagtail.org/images/Search_terms_report.width-900.png)

For users of [promoted search results](https://guide.wagtail.org/en-latest/how-to-guides/promote-search-results/), a new search terms report is available in the admin interface. This report provides:

-   A list of terms searched by website users.
-   Count of search occurrences for each term.

This feature allows for better insights into user behavior and adjustments to search promotions.

### Additional user interface improvements

Other updates in this release include:

-   Better default headings and labels added for InlinePanel orderable items.
-   Translation of time zone options in the Account view across all supported languages.
-   Explicit labeling for the "server time zone" option in account settings.
-   Scrolling improvements in the page editor to always keep text visible while typing at the bottom of the screen.
-   Correct placement of comment buttons near date/time fields.
-   Breadcrumbs enabled in revisions compare view, generic template views, and the Account view.

---

To learn about future enhancements ahead of time 👉️ check out the [Wagtail roadmap](https://wagtail.org/roadmap/), our [newsletter](https://wagtail.org/newsletter/), or read [Keeping up with upcoming changes in Wagtail](https://wagtail.org/blog/keeping-up-with-upcoming-changes-in-wagtail/).
