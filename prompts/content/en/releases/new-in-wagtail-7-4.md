# New in Wagtail 7.4

Page URL: https://guide.wagtail.org/en/releases/new-in-wagtail-7-4/

> Explore Wagtail 7.4: refined autosave, draft‑saving incomplete blocks, customizable listings, enhanced search, content checks, UI tweaks, and security fixes.

Here are highlights from Wagtail 7.4. For full technical details, view the complete [v7.4 release notes](https://docs.wagtail.org/en/stable/releases/7.4.html).

## **Autosave refinements**

![Network error message while editing a page in Wagtail CMS](https://guide-media.wagtail.org/images/Autosave_error_message_modal_-_a_network_error.width-900.png)

The autosave and concurrent editing notifications introduced in Wagtail 7.3 have been refined based on user feedback. Race conditions and brief network outages are handled more gracefully, the indicator messaging and alignment have been polished, and you can now distinguish which other users are active or idle while looking at the same page or snippet.

## **Save drafts of blocks without filling every field**

You can now save a draft of a page or snippet that contains incomplete StreamField blocks, even when some required fields inside a block are empty. This makes it easier to capture work in progress without losing your changes. Required fields are still enforced when you publish, schedule, or submit content to a workflow.

## **Customizable page listings**

Once enabled by a developer, the [page explorer](/en/how-to-guides/manage-pages/) and per-page-type listings can now be tailored for individual page types. That means custom columns, custom filters, and other refinements that make it easier to find and manage pages in large sites. Depending on how your site is configured, you may see different listings depending on which section of the site you're browsing.

## **Search improvements**

Wagtail's [built-in search](/en/how-to-guides/manage-pages/) has been upgraded with several enhancements:

-   Fuzzy matching is now supported on PostgreSQL, so small typos still surface relevant results.
-   Searching and filtering can reach deeper into related content, with no nesting limit.

## **Content quality checker enhancements**

![Wagtail page editor with live preview to the side, with a content checker annotation for a heading hierarchy issue](https://guide-media.wagtail.org/images/Content_checker_inline_error_highlight.width-900.png)

The built-in [content checks](/en/reference/content-checks/) get three improvements in this release:

-   Issues found by the checker are now shown as annotations directly inside the preview panel, so you can see exactly which part of the page they relate to.
-   A new SEO check flags pages with an empty meta description, helping search engines and link previews show useful summaries of your pages.
-   Custom checks built by your developers can now retrieve content metrics, opening up more ways to give you feedback as you write.

![Page editor with content checker issue reported for an empty meta description](https://guide-media.wagtail.org/images/Content_checker_meta_description_empty.width-900.png)

## **Other UI improvements**

This release also includes a range of smaller enhancements that improve day-to-day editing:

-   Block-based content now lists block groups in the order developers defined them, making the **Add block** menu more predictable.
-   The **Collapse all** state in the page editor is preserved when you switch between editor tabs.
-   Mailto and anchor links pasted into rich text fields are now preserved, instead of being stripped.
-   The **Submit to workflow** menu now uses the workflow's name when creating a new page.
-   Page descriptions are better aligned in the **Add subpage** view.
-   More embed providers are supported out of the box, including Flourish data visualizations and Heyzine flipbooks.
-   The page type usage view now supports custom listings, and lets you create new pages of that type directly from the view.
-   Image blocks correctly update alt text after you switch to a new image with the **Decorative** option turned off.
-   Long workflow task names are now truncated in admin tables, keeping listings tidy.
-   The **Add child page** button is hidden when limits configured by your developer prevent more children of that type.
-   Choice fields now display their human-friendly label in snippet and content listings, instead of the raw stored value.
-   The Pages menu in the [Sidebar](https://markdownlivepreview.com/en/how-to-guides/find-your-way-around/) now closes correctly when you click the sidebar search.
-   Hover and focus styles for the comment button on the page title have been refined.
-   Users with the right permissions can now reliably cancel a workflow task that's in progress.

## **Security and audit follow-ups**

Wagtail recently underwent an [independent code security audit](https://wagtail.org/blog/independent-security-audit-findings-and-next-steps/) commissioned by the [Interministerial Digital Directorate (DINUM)](https://www.numerique.gouv.fr/) of France. This release ships several follow-ups from that audit, alongside fixes for five disclosed vulnerabilities related to permissions on revisions, page history, form submissions, copying pages, and the Documents and Images API. If you administer a Wagtail site, we recommend upgrading promptly. For full details, see the [v7.4 release notes](https://docs.wagtail.org/en/latest/releases/7.4.html).

Many thanks to the Sites Conformes team at DINUM for sponsoring the audit, and to the security researchers who reported the issues.

## **Feedback requests**

We need feedback from our users!

-   Do you work on multilingual sites? Let us know about pain points in [Improving support for multilingual websites](https://github.com/wagtail/wagtail/discussions/13693).

To learn about future enhancements ahead of time 👉️ check out the [Wagtail roadmap](https://wagtail.org/roadmap/), subscribe to the [Wagtail newsletter](https://wagtail.org/newsletter/), or read [Keeping up with upcoming changes in Wagtail](https://wagtail.org/blog/keeping-up-with-upcoming-changes-in-wagtail/).
