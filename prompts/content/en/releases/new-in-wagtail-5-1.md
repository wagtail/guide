# New in Wagtail 5.1

Page URL: https://guide.wagtail.org/en-latest/releases/new-in-wagtail-5-1/

> Here are highlights from Wagtail 5.0. For more details, view the full v5.0 release notes.

Here are highlights from Wagtail 5.1. For more details, view the full [v5.1 release notes](https://docs.wagtail.org/en/latest/releases/5.1.html).

## **Read-only panels**

Field panels can now be marked as read-only, so that they are displayed in the admin but cannot be edited.

## **AVIF image support**

Wagtail now supports [AVIF](https://en.wikipedia.org/wiki/AVIF), a modern image format. We encourage all Wagtail users to consider using it to improve the performance of the sites and reduce their carbon footprint.

## Accessibility improvements

Wagtail now uses its modern tooltip and dropdown components across more of the interface, which addresses long-standing accessibility issues for keyboard, screen reader, and speech recognition users across:

-   Page listings actions under the “More” dropdown.
-   Bulk actions under the “More” dropdown.
-   Chooser buttons in forms

## Dark mode improvements

Following our [last release](/en-latest/releases/new-in-wagtail-5-0/), we’ve made tweaks to our new dark theme across the CMS.

-   Update link/document rich text tooltips for consistency with the inline toolbar
-   Increase the contrast between the rich text / StreamField block picker and the page in dark mode
-   Add support for presenting the userbar (Wagtail button) in dark mode
-   Ensure taggit field type-ahead options show correctly in the dark mode theme

## General UI improvements

-   Auto-select the StreamField block when only one block type is declared
-   Adopt optimised Wagtail logo in the admin interface
-   Move comment notifications toggle to the comments side panel
