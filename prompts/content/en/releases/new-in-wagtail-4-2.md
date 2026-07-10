# New in Wagtail 4.2

Page URL: https://guide.wagtail.org/en-latest/releases/new-in-wagtail-4-2/

> With Wagtail 4.0, 4.1, and now 4.2 – we&#39;ve added many substantial updates to the Wagtail page editor as well as some other tools that support every member of a content team.

Wagtail 4.2 comes with gradual improvements on functionality previous added in [Wagtail 4.1](/en-latest/releases/new-in-wagtail-4-1/) and [4.0](https://wagtail.org/blog/how-you-can-make-content-soar-with-wagtail-40/).

## Supercharged snippets

Continuing the changes introduced in the last release, snippets have two new capabilities matching what is possible with pages:

-   Locking – to prevent other users from editing a snippet.
-   [Workflows](/en-latest/how-to-guides/configure-workflows-for-moderation/) – to structure content review on your site.

### Multiple chooser panel

When configured by developers, site users can now select multiple items at a time in chooser modals. For example, here is a screenshot of a "Person" chooser allowing to select multiple blog post authors in one go:

![Multiple chooser panel for persons, with four items selectable](https://guide-media.wagtail.org/images/Multiple_chooser_panel_for_persons_with_four_i.width-900.png)

## Resizable side panels

To make the most of the space on the page editor, you can now resize side panels by using the "grip" button and dragging the panel to the appropriate size. Here is an example, with the preview panel:

![Page editor for "Bread and Circuses" page. The form to the left, and to the right the Preview side panel is expanded, showing the page as it would appear to users on Mobile devices](https://guide-media.wagtail.org/images/Page_editor_for_Bread_and_Circuses_page_The_fo.width-900.png)

## Built-in accessibility checker

Wagtail includes an accessibility checker built into the user bar. The checker can help authors create more accessible websites in compliance with the Web Content Accessibility Guidelines (WCAG). The checker is based on the [Axe](https://github.com/dequelabs/axe-core) testing engine and scans the loaded page for errors, displaying the results as a list:

![Accessibility checker showing one error with a heading hierarchy issue](https://guide-media.wagtail.org/images/Accessibility_checker_showing_one_error_with_a.width-900.png)

By default, the checker includes the following rules that are among the most common and critical accessibility issues to be violated by editors in Wagtail:

-   `empty-heading`: This rule checks for headings with no text content. Empty headings are confusing to screen readers users and should be avoided.
-   `p-as-heading`: This rule checks for paragraphs that are styled as headings. Paragraphs should not be styled as headings, as this can cause confusion for users who rely on headings to navigate content.
-   `heading-order`: This rule checks for incorrect heading order. Headings should be ordered in a logical and consistent manner, with the main heading (h1) followed by subheadings (h2, h3, etc.).

## Rich text improvements

Following feedback from Wagtail users on [rich text UI improvements in Wagtail 4.0](https://docs.wagtail.org/en/stable/releases/4.0.html#rich-text-improvements-4), we have further refined the behavior of rich text fields to cater for different scenarios:

-   Users can now choose between an “inline” floating toolbar, and a fixed toolbar at the top of the editor. Both toolbars display all formatting options.
-   The ‘/’ command palette and block picker in rich text fields now contain all formatting options except text styles.
-   The ‘/’ command palette and block picker are now always available no matter where the cursor is placed, to support inserting content at any point within text, transforming existing content, and splitting StreamField blocks in the middle of a paragraph when needed.
-   The block picker interface now displays two columns so more options are visible without scrolling.
