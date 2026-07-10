# New in Wagtail 6.1

Page URL: https://guide.wagtail.org/en-latest/releases/new-in-wagtail-6-1/

Here are highlights from Wagtail 6.1. For more details, view the full [v6.1 release notes](https://docs.wagtail.org/en/stable/releases/6.1.html).

## Universal listings continued

![Documents listing with Search field in header Add document button and a Collections dropdown Underneath are 2 rows of documents with a header row above](https://guide-media.wagtail.org/images/Documents_listing_with_Search_field_in_header_.width-900_X1WPjE0.png)

Continuing work on the Universal Listings project, this release rolls out universal listing styles for the following views:

-   Image listings
-   Document listings
-   Site and locale listings
-   Page and snippet history views
-   Form builder submissions
-   Collections listings
-   Groups
-   Users
-   Workflow and task views
-   Search promotions index views
-   Redirects index

With this work, we hope to increase the consistency of the user experience across different parts of the CMS. The Universal Listings designs also improve the information density of the interface, and how well it works on sites with a lot of filtering options set up.

## **Information-dense admin interface**

![Editing interface for Welcome to the Wagtail Bakery, in snug mode](https://guide-media.wagtail.org/images/Editing_interface_for_Welcome_to_the_Wagtail_B.width-900.png)

Wagtail now provides a way for you to control the information density of the admin interface, via your [user profile preferences]().

The new setting allows switching between the “default” density and a new “snug” mode, which reduces the spacing and size of UI elements. To switch Snug mode on, go to your Account settings and under **Theme Preferences** change your **Density** preference from "Default" to "Snug".

This change will make it easier for users to tweak the CMS to their liking, so Wagtail works well for users who expect a dense interface, and those who prefer the more spacious defaults.

## **Keyboard shortcuts overview**

![Keyboard shortcuts dialog](https://guide-media.wagtail.org/images/Keyboard_shortcuts_dialog.width-900.png)

A new dialog is available from the help menu, providing an overview of keyboard shortcuts available in the Wagtail admin.

We hope to introduce more keyboard shortcuts in the future, and consistently document all of the shortcuts available in the CMS so keyboard users have a reference of all options.

### **Better guidance for password-protected content**

![Page privacy dialog with the Shared Password option selected](https://guide-media.wagtail.org/images/Page_privacy_dialog_with_the_Shared_Password_o.width-900.png)

Wagtail now includes extra guidance in its private pages and [private collections (documents)](/en-latest/how-to-guides/manage-collections/) forms, to warn users about the pitfalls of the “shared password” option. For projects with higher security requirements, it’s also now possible to disable the shared password option entirely.

## Other user interface refinements

Here are additional changes to the user interface across the CMS:

-   Add ability to bulk toggle permissions in the user group editing view, including shift+click for multiple selections
-   Use custom setting icons in setting editing views
-   Ensure re-ordering buttons work correctly when using a nested InlinePanel
-   Ensure dropdown content cannot get higher than the viewport and add scrolling within content if needed
