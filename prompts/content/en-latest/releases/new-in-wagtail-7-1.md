# New in Wagtail 7.1

Page URL: https://guide.wagtail.org/en-latest/releases/new-in-wagtail-7-1/

Here are highlights from Wagtail 7.1. For more details, view the full [v7.1 release notes](https://docs.wagtail.org/en/latest/releases/7.1.html).

## **Previews support for settings**

![Generic settings with preview](https://guide-media.wagtail.org/images/Generic_settings_with_preview.width-900.png)

You can now preview changes made to your site's settings in real time. This allows you to see how updates will look before applying them, for example for navigation items like main menus or footers.

## Media listings improvements

![Images listing with header and images list](https://guide-media.wagtail.org/images/Images_listing_with_header_and_images_list.width-900.png)

[Image listings](/en-latest/how-to-guides/manage-images/) now offer both grid and list layouts. The new list layout provides additional details including file names, collections, creation dates, and usage count (with support for ordering by count), allowing easier management of images.

[Document listings](/en-latest/how-to-guides/manage-documents/) now also display usage counts, helping you quickly identify how documents are used throughout your site.

![Documents listing with Search field in header Add document button and a Collections dropdown Underneath are 2 rows of documents with a header row above](https://guide-media.wagtail.org/images/Documents_listing_with_Search_field_in_header_.width-900_2st99KC.png)

Thank you to [Joel William](https://www.linkedin.com/in/joel-william-360228276/) for implementing those features as part of the [Google Summer of Code program](https://wagtail.org/blog/four-contributors-for-gsoc-2025/)!

## Collapsible blocks settings

![Collapsible block settings](https://guide-media.wagtail.org/images/Collapsible_block_settings.width-900.png)

Nested structured blocks in StreamField can now be collapsed or expanded, simplifying the editing interface when working with complex content structures. This makes it possible for developers to hide away some of a block’s configuration options, so CMS users can more easily scan the UI for important fields.

## Enhanced preview for headless setups

![Page editor for Bread and Circuses page The form to the left and to the right the Preview side panel is expanded showing the page as it would appear to users on Mobile devices](https://guide-media.wagtail.org/images/Page_editor_for_Bread_and_Circuses_page_The_fo.width-900_l88OI5D.png)

Live previews have better support for headless websites. Where configured, you can preview content using your headless frontend, benefiting from additional features like accessibility checks, content metrics, and scroll restoration.

## Expanded keyboard shortcuts

![Keyboard shortcuts dialog](https://guide-media.wagtail.org/images/Keyboard_shortcuts_dialog_alyQsTE.width-900.png)

Two new additional [keyboard shortcuts](/en-latest/concepts/accessibility-features/) have been introduced to simplify navigation within the Wagtail admin interface: [ to toggle the main sidebar, and ] to toggle the minimap in the page editor. Users can also disable keyboard shortcuts entirely in their profile settings if preferred. There are more shortcuts to come in future releases.

Thank you to [Dhruvi Patel](https://www.linkedin.com/in/dhruvi-patel-55043412a/) for implementing those features as part of the [Google Summer of Code program](https://wagtail.org/blog/four-contributors-for-gsoc-2025/)!

## Other UI improvements

-   Header breadcrumbs now save their expanded or collapsed state across navigation and refreshes.
-   Added an 'Edit' button to the success message after copying a page.
-   Restricted file dialog in the multiple image uploader to accepted image file types.
-   Bulk deletion actions for multiple pages now require a type-to-confirm step.
-   Active user states now displayed using intuitive check or cross icons.
-   Collapsed StreamField blocks now summarize additional field types (checkboxes, radio buttons).
-   Block previews now support translation.
-   Panel collapse button labels are now translatable.
-   AVIF image uploads through the image chooser now supported on Firefox.
-   Table cells in listings avoid breaking words unless specifically enabled.
-   "All items in listing" bulk actions for images/documents respect user permissions.
-   Listings clearly distinguish boolean values without relying on colors.
-   InlinePanel labels and headings have improved capitalization handling.
-   Commenting keyboard shortcuts more effectively move focus to existing comments.
-   Validation errors within StreamField blocks are now clearly marked.
-   Accessibility dialog positioning now adjusts based on the user bar location.
-   Locale-aware number columns introduced for clearer numeric listings.
-   Rich text fields now support minimum length validation.
-   Always show block types in StreamField UI

---

To learn about future enhancements ahead of time 👉️ check out the [Wagtail roadmap](https://wagtail.org/roadmap/), our [newsletter](https://wagtail.org/newsletter/), or read [Keeping up with upcoming changes in Wagtail](https://wagtail.org/blog/keeping-up-with-upcoming-changes-in-wagtail/). Or join [Wagtail Space 2025](https://wagtail.org/wagtail-space-2025/) this October!

## Feedback requests

Do you use Wagtail on a tablet or smartphone? Please let us know more about what you do and how well it works on our [mobile support discussion thread](https://github.com/wagtail/wagtail/discussions/13273).
