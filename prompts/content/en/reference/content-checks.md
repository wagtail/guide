# Content checks

Page URL: https://guide.wagtail.org/en-latest/reference/content-checks/

Content quality checks are present in the CMS. Here are the checks available out of the box. Those checks are based on the content of the page as seen by users of the site, not what is editable in the CMS.

## Content metrics

Wagtail calculates multiple metrics based on the page’s content, live in the page editor.

![Page editor for "Bread and Circuses" page. The form to the left, and to the right the Checks side panel is expanded, showing different metrics about the page](https://guide-media.wagtail.org/images/Page_editor_for_22Bread_and_Circuses22_page._T.width-900.png)

### **Words**

We calculate the number of words present in the "plain text" content, with no formatting counted. This calculation is done differently for all languages, based on language-specific rules.

### **Reading time**

We calculate reading time from word count, using different reading speeds for different languages. Out of the box, Wagtail supports reading speeds for:

-   Arabic
-   Chinese
-   Dutch
-   English
-   Finnish
-   French
-   German
-   Hebrew
-   Italian
-   Korean
-   Spanish
-   Swedish

Other languages default to the "English" reading speed factor.

### **Readability**

We use the [LIX readability formula](<https://en.wikipedia.org/wiki/Lix_(readability_test)>), based on length of words and sentences. Content scores worse when there is a high proportion of long sentences and long words.

To better understand the score for a page, copy the content as it’s displayed to site users into an external tool like the [Hemingway Editor](https://hemingwayapp.com/). This will give you more granular feedback on which parts of the content might need improvements.

## Accessibility checker

To ensure accessibility of content for site users, the **Checks** side panel runs automated accessibility checks on the page content. The checker can help authors create more accessible websites following best practices and accessibility standards like [WCAG](https://www.w3.org/WAI/standards-guidelines/wcag/). The checker is based on the [Axe](https://github.com/dequelabs/axe-core) testing engine and scans the loaded page for errors.

![Accessibility checker showing one error with a heading hierarchy issue](https://guide-media.wagtail.org/images/Accessibility_checker_showing_one_error_with_a.width-900.png)

By default, the checker includes the following rules to find common accessibility issues in authored content:

-   `button-name`: button elements must always have a text label.
-   `empty-heading`: This rule checks for headings with no text content. Empty headings are confusing to screen readers users and should be avoided.
-   `empty-table-header`: Table header text should not be empty
-   `frame-title`: iframe elements must always have a text label.
-   `heading-order`: This rule checks for incorrect heading order. Headings should be ordered in a logical and consistent manner, with the main heading (h1) followed by subheadings (h2, h3, etc.).
-   `input-button-name`: input button elements must always have a text label.
-   `link-name`: link elements must always have a text label.
-   `p-as-heading`: This rule checks for paragraphs that are styled as headings. Paragraphs should not be styled as headings, as they don’t help users who rely on headings to navigate content.
-   `alt-text-quality`: A custom rule ensures that image alt texts don’t contain anti-patterns like file extensions and underscores.
