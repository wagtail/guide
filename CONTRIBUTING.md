# Contributing

We welcome all support for this User Guide, whether on bug reports, code, design, reviews, tests, documentation, translations or just feature requests.

For details on how to run this project locally, please read the [contributing section in the README](https://github.com/wagtail/guide#contributing).

## Content contributions

All of the User Guide pages are maintained in Wagtail. We use [GitHub Discussions](https://github.com/wagtail/guide/discussions) to coordinate content improvements, with features requests and bug reports for the site in the [issue tracker](https://github.com/wagtail/guide/issues).

### Writing content

If you want to help with content, reach out to us in [GitHub Discussions](https://github.com/wagtail/guide/discussions) or on the #editor-guide channel of the [Wagtail Slack workspace](https://github.com/wagtail/wagtail/wiki/Slack). We will then create an account for you in Wagtail, making sure you have access to the right parts of the content.

### Translations

We want the guide to ultimately be available in as many languages as Wagtail itself. If you want to help with translations, start a thread in [GitHub Discussions](https://github.com/wagtail/guide/discussions) or join the #editor-guide channel of the [Wagtail Slack workspace](https://github.com/wagtail/wagtail/wiki/Slack). We will then create an account for you in Wagtail, making sure you have access to the right parts of the content.

#### How to translate

We set up a separate translation team for each language, with their own Group able to submit changes to all pages and images in their locale. Translation teams work on the same content as the source language, with version-specific details noted through annotations rather than separate copies.

For example, the _Translators: Icelandic (latest)_ group has access to:

- Translation: Can submit translations
- Can access Wagtail admin: Yes
- Pages: Notendahandbók Wagtail (latest homepage): Add, Edit, Lock, Unlock
- Images: "Icelandic (latest)": Add, Edit, Choose

When working on changes to the source content in English, make sure to avoid unnecessarily removing and adding StreamField blocks, so block references are stable between revisions.

#### RTL support

The guide supports right-to-left languages, like Arabic and Hebrew. All layout and styling changes must work correctly in both LTR and RTL.

If you're unsure whether something should mirror or stay fixed, start a thread in [GitHub Discussions](https://github.com/wagtail/guide/discussions) or the #editor-guide channel of the [Wagtail Slack workspace](https://github.com/wagtail/wagtail/wiki/Slack).

### Versioning

The guide documents the current state of Wagtail, and we keep a single copy of the content per language. Versions are handled inside page content rather than with separate page trees, locales or collections. There is one page per topic per locale, and it describes how Wagtail behaves in the release the guide targets, annotated with the version in which each capability was added, changed or removed.

We track all Wagtail versions in a single content tree rather than maintaining a separate copy per version: annotations carry the version history, so a reader on an older release can still tell what applies to them. We annotate changes chronologically, oldest first, and leave older annotations as they are. Add new annotations for the latest release as its features are documented, rather than rewriting history. See Wagtail’s [release schedule](https://github.com/wagtail/wagtail/wiki/Release-schedule) for the versions currently in support.

#### Page content

Pages use the “Text (annotated)” block for anything that is version-specific: paragraph text, list items, and similar rich text. These blocks have optional _version_ (in `x.y` format, for example `7.4`) and _change type_ (_Added_, _Changed_, _Removed_) settings, which render as a small badge next to the content, such as "Added in Wagtail 7.4".

When writing or reviewing content:

1. Describe the behaviour of the latest Wagtail release. Keep the guidance a Wagtail user needs regardless of the version they run where possible.
2. Use annotated blocks for anything noteworthy that was added, changed or removed in a specific version, so readers on older releases can tell which parts apply to them. Keep annotations for as long as feels relevant, they’re a good record of past changes.

See the [release notes](https://docs.wagtail.org/en/stable/releases/) for changes to cover.

#### When Wagtail has a new release

There is no separate release step that copies content: the guide’s content always reflects the latest release. After a new Wagtail release:

1. Add a “New in Wagtail X.Y” page under Releases, following the existing pages for previous releases.
2. Go through the guide’s content and annotate anything that changed in the new release, using the annotated blocks described above.
3. Review any existing annotations that are no longer accurate, and update the surrounding text without removing the annotation itself.
4. Update screenshots for any pages where the CMS interface has changed (see below).

#### Images

Images are not versioned. There is a single set of images, and pages use the current set. When the CMS interface changes, replace images in place rather than adding new copies for each release.

First, use the "docs-screenshot" suite of [wagtail-tooling](https://github.com/thibaudcolas/wagtail-tooling) to take new screenshots of the CMS with the [bakerydemo](https://github.com/wagtail/bakerydemo) project as the target. Screenshots all use standardized sizes, and a uniform style for highlights on the screen.

Then, upload the new images in the CMS:

1. Upload the replacement images, in the collection matching their language.
2. Replace the existing images on the affected pages. Delete the images that are no longer used.
3. For all pages with changed images, manually sync translations (without publishing), then publish the pages once no translations are missing.

#### Versioned URLs

The guide used to serve a separate copy of the site per Wagtail version, at URLs like `/en-6.0.x/`. These URLs now redirect to the matching unversioned page, with a `target_version` query parameter recording the version, for example `/en-6.0.x/how-to-guides/manage-snippets/` redirects to `/en/how-to-guides/manage-snippets/?target_version=6.0.x`. Developer-docs-style `/en/latest/` URLs redirect to the unversioned page too. This is handled by `VersionedUrlRedirectMiddleware` in `apps/core/middleware.py`, so old links keep working without us maintaining duplicate content.
