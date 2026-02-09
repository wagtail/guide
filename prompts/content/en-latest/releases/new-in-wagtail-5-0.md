# New in Wagtail 5.0

Page URL: https://guide.wagtail.org/en-latest/releases/new-in-wagtail-5-0/

> Here are highlights from Wagtail 5.0. For more details, view the full v5.0 release notes.

Here are highlights from Wagtail 5.0. For more details, view the full [v5.0 release notes](https://docs.wagtail.org/en/latest/releases/5.0.html).

### **Object usage information on deleting objects**

On deleting a page, image, document or snippet, the confirmation screen now provides a summary of where the object is used, allowing users to see the effect that deletion will have elsewhere on the site.

This usage information is also now available for pages, rather than only images / documents / snippets.

### **SVG image support**

The image library can now be configured to allow uploading SVG images.

### **Accessibility checker improvements**

The [built-in accessibility checker](https://docs.wagtail.org/en/latest/advanced_topics/accessibility_considerations.html#built-in-accessibility-checker) has been updated with:

-   5 more checks enabled by default.
-   Sorting of checker results according to their position on the page.
-   Highlight styles to more easily identify elements with errors.

### **Always-on minimap**

Following its introduction in Wagtail 4.1, we have made a number of improvements to the page editor minimap:

-   It now stays opened until dismissed, so users can keep it expanded if desired.
-   Its "expanded" state is preserved when navigating between different views of the CMS.
-   The minimap and "Collapse all" button now appear next to side panels rather than underneath, so they can be used at any time.
-   Clicking any item reveals the minimap, with appropriate text for screen reader users.
-   Navigating to a collapsed section of the page will reveal this section.

### **Dark mode**

Wagtail’s admin interface now supports dark mode. The new dark theme can be enabled in account preferences, as well as configuring permanent usage of the light theme, or following system preferences.

We hope this new theme will bring accessibility improvements for users who perfer light text on dark backgrounds, and energy usage efficiency improvements for users of OLED monitors.
