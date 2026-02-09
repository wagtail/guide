# New in Wagtail 6.3

Page URL: https://guide.wagtail.org/en-latest/releases/new-in-wagtail-6-3/

> Highlights from the new admin features in Wagtail 6.3

Here are highlights from Wagtail 6.3. For more details 👉️ view the full [v6.3 release notes](https://docs.wagtail.org/en/stable/releases/6.3.html).

## Incremental dashboard enhancements

![Wagtail dashboard with new design released in Wagtail 6.3](https://guide-media.wagtail.org/images/Wagtail_dashboard_with_new_Things_in_Wagtail_4.width-900_MPQXgu4.png)

The Wagtail dashboard design evolves towards providing more information and navigation features. Mobile support is much improved. Upgrade banners are now dismissible.

## Enhanced contrast admin theme

![Wagtail page listing in light theme with enhanced-contrast designs](https://guide-media.wagtail.org/images/Wagtail_page_listing_in_light_theme_with_enhan.width-900.png)

CMS users can now control the level of contrast of UI elements in the admin interface. This new customization is designed for partially sighted users, complementing existing support for a dark theme and Windows Contrast Themes. The new “More contrast” theming can be enabled in account preferences, or will otherwise be derived from operating system preferences.

## Universal design

This release follows through with “universal listings” user experience and design consistency improvements earlier in 2024, with the following features.

-   All create/edit admin forms now use a sticky submit button, for consistency and to speed up edits
-   Secondary form actions such as “Delete” are now in the header actions menu, for consistency and to make the actions more easily reachable for keyboard users
-   Documents and Images views now use universal listings styles
-   Page type usage, workflow usage, and workflow history views views also use universal listings styles
-   The forms pages listing now supports search and filtering

## HEIC / HEIF image upload support

When enabled by a developer, Wagtail now allows users to upload and use [HEIC / HEIF](https://en.wikipedia.org/wiki/High_Efficiency_Image_File_Format) images in Wagtail. By default, these images are automatically converted to JPEG format when rendered. For more details, see [HEIC / HEIF images in the developer docs](https://docs.wagtail.org/en/latest/topics/images.html#heic-heif-images).

### Image description field

![Image editing form for Olivia Ava image To the right of the form is an image preview focal point controls and metadata about the image](https://guide-media.wagtail.org/images/Image_editing_form_for_Olivia_Ava_image_To_the.width-900_VsFI5Yq.png)

To better support alternative text requirements for images, Wagtail now includes a built-in "Description" field for images. This will be used as image alt text within the CMS interface, and can also be configured by developers to be used when displaying images on the site.

## Other UI improvements

-   Snippets editing forms can now detect and flag unsaved edits to encourage saving.
-   The footer actions dropdown has been redesigned with larger text and increased color contrast.
-   Page privacy rules can now be set on pages within a section where the parent page already has its own rules.
-   Pasting text content with URLs within, automatically converts those URLs to links.
-   The admin interface now supports the Uyghur language.

---

To learn about future enhancements ahead of time 👉️ check out the [Wagtail roadmap](https://wagtail.org/roadmap/), our [newsletter](https://wagtail.org/newsletter/), or read [Keeping up with upcoming changes in Wagtail](https://wagtail.org/blog/keeping-up-with-upcoming-changes-in-wagtail/).
