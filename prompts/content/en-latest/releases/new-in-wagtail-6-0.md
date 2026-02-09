# New in Wagtail 6.0

Page URL: https://guide.wagtail.org/en-latest/releases/new-in-wagtail-6-0/

Here are highlights from Wagtail 6.0. For more details, view the full [v6.0 release notes](https://docs.wagtail.org/en/latest/releases/6.0.html).

## **Universal listings**

![Wagtail 6.0 universal listings interface, with example of searching for a "bread" blog page](https://guide-media.wagtail.org/images/wagtail-6-filters-listing.width-900.png)

Following design improvements to page listings, Wagtail now provides a unified search and filtering interface for all listings. This will improve navigation capabilities, particularly for sites with a large number of pages or where content tends to use a flat structure. We also hope to roll out this interface across all areas of the CMS for a consistent experience.

In this release, the universal listing interface is available for [Pages](/en-latest/how-to-guides/manage-pages/), [Snippets](/en-latest/how-to-guides/manage-snippets/), and Forms. For pages, the UI includes the following filters out of the box:

-   Page type
-   Date updated
-   Owner
-   Edited by
-   Site
-   Has child pages
-   Locale

## **Right-to-left language support**

![Wagtail 6.0 right-to-left interface example, with the page editor and a page preview](https://guide-media.wagtail.org/images/wagtail-6-rtl.width-900.png)

The admin interface now supports right-to-left languages, such as Persian, Arabic, and Hebrew. Though there are still some areas that need improvement, all admin views will now be displayed in the correct direction.

For projects with users of right-to-left languages – there should be no need to customize the CMS for compatibility anymore.

## **Accessibility checker in page editor**

![Wagtail 6.0 accessibility checker demo, with 3 issues found relating to headings on the page](https://guide-media.wagtail.org/images/wagtail-6-accessibility-checker-light.width-900.png)

The built-in accessibility checker now displays as a side panel within page and snippet editors supporting preview. In this release, the new “Checks” side panel only shows accessibility-related issues for pages with the userbar enabled. In the future, it will be updated to support any content checks, across any page. For more information on future plans, see [Looking for sponsorship – Accessibility checks for site administrators](https://wagtail.org/blog/looking-for-sponsorship-accessibility-checks-for-site-administrators/) on the Wagtail blog.

## Polished dark mode

![Wagtail 6.0 in dark mode – with the same example as the accessibility checker](https://guide-media.wagtail.org/images/wagtail-6-accessibility-checker-dark.width-900.png)

Wagtail 6.0 comes with refinements to the dark theme within the admin interface. Dark themes are an important [accessibility](https://wagtail.org/accessibility/) feature, and they help with environmental [sustainability](https://wagtail.org/sustainability/) by reducing display power consumption for OLED devices.

## **Page types usage report**

![Wagtail 6.0 page types report, on a simple site with 9 page types and 30 pages](https://guide-media.wagtail.org/images/wagtail-6-page-types-usage-report.width-900.png)

The new Page types report provides a breakdown of the number of pages for each type. It helps answer questions such as:

-   Which page types do we have on our CMS?
-   How many pages of that page type do we have?
-   When was a page of that type last edited? By whom? Which page was that?

This feature was implemented thanks to a [feature sponsorship](https://wagtail.org/sponsor/) by Mozilla.

## **Accessibility improvements**

This release comes with a high number of accessibility improvements across the admin interface:

-   Better support to define header cells for tables
-   Keyboard support for table editing
-   Keyboard support in all action menus
-   Refinements in labels used by screen reader and speech recognition users

View our [Accessibility](https://wagtail.org/accessibility/) page for more information about the state of Wagtail accessibility.
