---
title: 'Wagtail API'
description: 'The Wagtail API lets other applications and integrations read, create, edit, and publish your content, with the same permissions and rules as the Admin interface.'
last_modified: '2026-11-10'
---

# Wagtail API

Page URL: https://guide.wagtail.org/en/concepts/wagtail-api/

> The Wagtail API lets other applications and integrations read, create, edit, and publish your content, with the same permissions and rules as the Admin interface.

The Wagtail API lets other applications and integrations work with your site's content without going through the [Admin interface](/en/concepts/wagtail-interfaces/). It can read, create, edit, and publish pages, manage images and documents, and take part in moderation workflows, all while following the same permissions and rules as the Admin interface.

Added in Wagtail 8.0: the v3 API is available as a preview. Developers need to enable it when building the site, so it may not be available on your site. This is because Wagtail is highly customizable. If this is the case, contact your web developer for more information.

## What the API is used for

An API (application programming interface) is a structured way for software to talk to Wagtail. Instead of a person clicking through the Admin interface, a program sends requests to read or change content, and Wagtail responds.

Here are some examples of what your organization might use the API for:

- Displaying your content in a separate website or mobile app.
- Importing content in bulk from another system, such as a previous CMS or a product database.
- Making site-wide content improvements, like fixing outdated links or adding missing image descriptions.
- Getting automated feedback on your content, for example from AI tools.
- Building a custom moderation dashboard for reviewers.

The API comes with built-in documentation that your developers can browse to see everything it supports for your site, based on your site's own page types and fields.

![Preview of the Wagtail v3 API documentation showing an OpenAPI schema generated from a site's models, with a list of pages endpoints and example request and response](https://guide-media.wagtail.org/images/Wagtail_API_v3_schema_docs_viewer_with_pages_o.width-900.png)

## What integrations can do

The API covers most of the content operations available in the Admin interface. Which content and fields are available depends on how developers configured the API for your site.

### Pages

Integrations can find, read, create, edit, and delete pages. They can read either the live version of a page or its latest draft, and browse a page's revisions. They can also carry out the same page actions you have in the Admin interface:

- Publish and unpublish pages, including all child pages when unpublishing.
- Copy pages, with or without their child pages.
- Move pages to a new location in the page tree.
- Revert a page to a previous revision.
- Create aliases, and convert an alias into a regular page.
- Copy a page into another language, on multilingual sites.

Integrations can filter and search pages, for example to list all child pages of a section, or all pages of one type in a given language.

### Workflows

Integrations can take part in [moderation workflows](/en/how-to-guides/configure-workflows-for-moderation/) for pages and snippets. They can submit content for moderation, approve or reject the current task with a comment, resume a workflow after making changes, and cancel a workflow. They can also read the current status of a workflow and its history.

### Images and documents

Integrations can upload, read, and delete [images](/en/how-to-guides/manage-images/) and [documents](/en/how-to-guides/manage-documents/), and update their details, such as their title, collection, or an image's focal point.

Keep in mind that integrations can't replace the file of an existing image or document, and can't change their tags.

### Snippets

Integrations can read, create, edit, and delete [snippets](/en/how-to-guides/manage-snippets/), for the snippet types that developers made available in the API. When a snippet type supports drafts, revisions, translations, or workflows in the Admin interface, the matching actions are available in the API too.

### Redirects, sites, and locales

Integrations can manage [redirects](/en/how-to-guides/manage-redirects/), [sites](/en/how-to-guides/manage-sites/), and the languages (locales) available on multilingual sites.

### Rich text

Integrations can read and write rich text either in HTML or in Markdown, a plain-text formatting syntax that's popular with writing tools and AI models.

When an integration saves rich text, Wagtail removes any formatting that isn't enabled for that field, exactly like when you paste content into the editor.

### Not available yet

Some features aren't supported by the API yet:

- Site settings.
- Locking and unlocking pages or snippets. Locks set in the Admin interface still apply.
- Setting or cancelling a publishing schedule. An integration can publish a revision that already has a _go-live at_ date set, in which case the page is scheduled rather than published right away.
- Keeping translations in sync after the first copy into another language.

## Who can do what

Requests to the API can either be anonymous or be made on behalf of a user account.

### Anonymous requests

Anyone can read the content that's already public on your site, without any credentials. This includes:

- Live pages, without any [privacy restrictions](/en/how-to-guides/manage-pages/).
- Images and documents, except those in collections with a privacy restriction.
- Redirects.

Anonymous requests can't see draft content, and can't make any changes.

Note that only a privacy restriction on a document's own collection hides it from the API. A restriction on a parent collection doesn't hide documents stored in its child collections.

### Requests made with an API token

To do more than read public content, an integration needs an API token. Each token belongs to a user account, and the integration acts as that user. It has exactly the same permissions as the user has in the Admin interface. For example, an integration using the token of an editor who can only edit blog pages can't create pages anywhere else on the site.

With a token, integrations can see the pages the user can edit or publish, including drafts. To learn how to create and revoke tokens, see [Manage API tokens](/en/how-to-guides/manage-api-tokens/).

As in the Admin interface, moderators who can approve or reject the current workflow task can read the workflow status of that content while it awaits their review, even if they don't otherwise have permission to edit it.

## Same rules as the Admin interface

Changes made through the API go through the same checks and processes as changes made in the Admin interface:

- Content is validated with the same rules. For example, a page can't use a slug that's already taken by another page under the same parent, and uploaded files must meet the same file type and size limits.
- Every save creates a revision, recorded under the user the token belongs to. You can review and compare these in the [page history](/en/how-to-guides/manage-pages/), like any other edit.
- Actions are logged, so you can see them in the [Site history report](/en/concepts/reports/).
- Workflow actions send the same notification emails to the same people.
- Publishing content cancels any workflow in progress on it, like in the Admin interface.
- Approving the last task of a workflow publishes the content, so the approver needs permission to publish.

## Things to keep in mind

The API does what it's asked to do, without the confirmation steps you see in the Admin interface. If you're working with developers on an integration, here are some behaviors worth discussing with them:

- **Deleting is permanent.** Deleting a page also deletes all of its child pages, and there's no way to undo it. The same applies to images, documents, and other content.
- **Edits to live pages are saved as drafts unless published.** An integration that edits a live page without publishing it creates a new draft, and the live page stays unchanged until someone publishes it.
- **Reverting creates a draft.** Reverting to a previous revision doesn't publish it. The page needs to be published afterwards for the change to appear on the site.
- **Block-based content is replaced as a whole.** When an integration updates a block-based field (also known as StreamField), or a repeating set of fields such as a list of authors, it replaces the entire field. Any blocks or items it doesn't send are removed.

---

The v3 API replaces the older v2 API, which could only read content. The v2 API is planned for removal in Wagtail 9.0. If your site uses it, your developers will need to update your integrations before then.

Do you want to use the API on your projects? Let us know about your use cases and any other feedback in the [v3 API feedback discussion](https://github.com/wagtail/wagtail/discussions/14531).

For developer documentation, see [Wagtail API v3 in the developer docs](https://docs.wagtail.org/en/latest/advanced_topics/api/v3/index.html).
