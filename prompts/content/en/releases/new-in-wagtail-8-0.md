---
title: 'New in Wagtail 8.0'
description: 'Discover Wagtail 8.0: the new v3 API to create, edit, and publish content programmatically, plus improvements to the site switcher, workflow details, and image handling.'
last_modified: '2026-08-26'
---

# New in Wagtail 8.0

Page URL: https://guide.wagtail.org/en/releases/new-in-wagtail-8-0/

> Discover Wagtail 8.0: the new v3 API to create, edit, and publish content programmatically, plus improvements to the site switcher, workflow details, and image handling.

Here are highlights from Wagtail 8.0. For full technical details, view the complete [v8.0 release notes](https://docs.wagtail.org/en/stable/releases/8.0.html).

## Manage content with the new v3 API

![Preview of the Wagtail v3 API documentation showing an OpenAPI schema generated from a site's models, with a list of pages endpoints and example request and response](https://guide-media.wagtail.org/images/Wagtail_API_v3_schema_docs_viewer_with_pages_o.width-900.png)

Wagtail now offers new v3 API in preview, that lets applications and integrations create, edit, publish, unpublish, move, copy, and revert content. It covers pages, sites, locales, redirects, images, documents, and snippets, with authentication tied to user accounts and permissions.

This opens up new ways to automate content operations, such as site-wide content improvements, automated imports from external systems, or external LLM feedback on site content. Once enabled by a developer according to the [v3 API developer documentation](https://docs.wagtail.org/en/latest/advanced_topics/api/v3/index.html), integrations can interact with your content through it.

## Permission policies

Wagtail now supports reusing its permissions model in custom code, so projects can more consistently apply permission checks in their customizations. This supports organizations delegating more of their website's content operations across many roles, with strong security guarantees.

## **Guide website improvements**

The [Wagtail user guide](/en/) has been updated to use a new versioning scheme, better search and navigation, and better support for Right-to-Left (RTL) languages.

Thank you to Raghad Dahi for leading this work. For more information, read her project report: [Streamlining content ops with LLMs: Wagtail user guide](https://wagtail.org/blog/streamlining-content-operations-with-llms-wagtail-user-guide/).

## **Automated dependency management**

For organizations wanting to meet strict supply chain management, Wagtail now provides [SBOM exports of its dependency graph](https://github.com/wagtail/wagtail/network/dependencies) in SPDX JSON format.

## Other UI improvements

This release also includes a range of smaller enhancements that improve day-to-day editing:

- The site switcher in the site settings editor now shows each site's name, making it clearer which site you're configuring on multi-site installations.
- Workflow task states are clearer in the workflow details dialog, so it's easier to see where a workflow is stuck or progressing.
- You can now paste several tags at once into tag fields, separated by commas or newlines.
- Modern image formats such as AVIF and WebP are no longer converted to PNG by default, keeping file sizes smaller.
- Multilingual sites are less likely to require the "choose parent" step when creating a page, and moving pages with missing translations no longer causes errors.
- Approving a workflow that has been cancelled in a different session no longer causes an error.
- Blank dropdown values now use clearer, more accessible labels in block-based content and locked page report filters.
- Icons inside buttons no longer capture clicks meant for the button itself.
- Audit log messages stay readable even when a content type is no longer in use.
- Form page field values stay consistent even when autosave runs early.
- The TED embed provider now uses its canonical URL for more reliable embeds.

Many behind-the-scenes fixes and performance improvements are also included.

## Let us know what you think

We thrive with feedback from our community. Here are recent threads that are relevant to Wagtail 8.0:

- Do you want to use the new API on your projects? Let us know about your use cases and any other feedback in the [v3 API feedback discussion](https://github.com/wagtail/wagtail/discussions/14531).
- We just updated our [roadmap for Wagtail 8.1](https://wagtail.org/roadmap/), due in November. Let us know what you think, either on socials, Slack, or directly on roadmap discussion threads.

---

To learn about future enhancements ahead of time 👉️ subscribe to the [Wagtail newsletter](https://wagtail.org/newsletter/), or read [Keeping up with upcoming changes in Wagtail](https://wagtail.org/blog/keeping-up-with-upcoming-changes-in-wagtail/).
