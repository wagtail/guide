# New in Wagtail 6.2

Page URL: https://guide.wagtail.org/en-latest/releases/new-in-wagtail-6-2/

> Highlights from the new admin features in Wagtail 6.2

Here are highlights from Wagtail 6.2. For more details, view the full [v6.2 release notes](https://docs.wagtail.org/en/stable/releases/6.2.html).

## Content metrics

![Content metrics in Wagtail 6.2 in the side panel](https://guide-media.wagtail.org/images/Content_metrics_in_Wagtail_6.2.width-900.png)

The page editor’s Checks panel now displays two content metrics: word count, and reading time. They are calculated based on the contents of the page preview. Where possible, the calculation only takes into account the "main" content area of the page. This avoids navigation menus and footer information elements being used in the word count.

The Checks panel has also been redesigned to accommodate a wider breadth of types of checks, and interactive checks, in future releases.

This feature was implemented thanks to a [feature sponsorship](https://wagtail.org/sponsor/) by The Motley Fool.

## Concurrent editing notifications

![Concurrent editing warning dialog to prevent unintentional overrides](https://guide-media.wagtail.org/images/Concurrent_editing_warning_dialog_to_prevent_u.width-900.png)

When multiple users concurrently work on the same content, Wagtail now displays notifications to inform them of potential editing conflicts. Those notifications initially appear as user avatars in the page header, each with a status tooltip.

---

Concurrent editing notifications are available for pages, and snippets. Specific messaging about conflicting versions is only available for pages and snippets with support for saving revisions with a version history.

## Alt text accessibility check

![Accessibility checker dialog with two issues found, one alt text, one about headings](https://guide-media.wagtail.org/images/Alt_text_accessibility_checker.width-900.png)

The built-in accessibility checker now includes a new rule about quality of alt text, which tests alt text for the presence of known bad patterns such as file extensions and underscores. This rule is enabled by default, but can be disabled if necessary.

## Universal listings designs for report views

![Wagtail 6.2 site history report with new listing and filter interface](https://guide-media.wagtail.org/images/Wagtail_6.2_site_history_report_with_new_listi.width-900.png)

All built-in and custom [reports](/en-latest/concepts/reports/) now use the new listing visual design and filtering features introduced in all other areas of the admin interface over past releases.

## **Other user interface refinements**

Here are additional changes to the user interface across the CMS:

-   Redirects forms now use the same page layout as other forms in the CMS
-   Listing views no longer show links to editing forms for users without appropriate permissions
-   Editing views no longer show the delete button if permissions prevent deletion
-   Increased visibility of draft page titles in listings
-   New design for locale labels in listings
-   Address layout issues in the title cell of universal listings
-   Going below or above the minimum and maximum block counts now shows a warning
