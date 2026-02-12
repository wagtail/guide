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

We set up a separate translation team for each language, with their own Group able to submit changes to all pages and images in their locale. Translation teams reflect the changes in the “latest” version of the documentation, with legacy versions only being accessible to admin users.

For example, the _Translators: Icelandic (latest)_ group has access to:

-   Translation: Can submit translations
-   Can access Wagtail admin: Yes
-   Pages: Notendahandbók Wagtail (latest homepage): Add, Edit, Lock, Unlock
-   Images: "Icelandic (latest)": Add, Edit, Choose

When working on changes to the "latest" source content in English, make sure to avoid unnecessarily removing and adding StreamField blocks, so block references are stable between revisions.

### Versioning

Our default "latest" version of the guide corresponds to Wagtail’s release currently in development. When Wagtail has a new release, we create a copy of the guide’s "latest" content for that release. Here are the preliminary steps to do this:

1. Make sure the version exists in the Django settings ([`WAGTAIL_GUIDE_VERSIONS`](https://github.com/search?q=repo%3Awagtail%2Fguide%20WAGTAIL_GUIDE_VERSIONS&type=code)).
2. Add the new version in the CMS in [Locales](https://guide.wagtail.org/admin/locales/).
3. Add the new version in the CMS in [Collections](https://guide.wagtail.org/admin/collections/) – with a parent collection matching the version number, and then a child collection for any language with translated images (currently English only).

We then review and update the website’s content in the "Latest" version to match the current capabilities of Wagtail, before proceeding to make a copy of all content for the new release.

#### Page content

Then for every locale:

1. Translate the "latest" homepage of the site (without child pages) to the new locale.
2. Translate all child pages of the "latest" homepage (with child pages) to the new locale.
3. For all pages of the new locale, manually publish changes for published pages only (page by page).
4. Make sure to re-order the pages of the new locale so they show in the correct order in the site’s sidebar.

#### Images

First, use the "docs-screenshot" suite of [wagtail-tooling](https://github.com/thibaudcolas/wagtail-tooling) to take new screenshots of the CMS with the [bakerydemo](https://github.com/wagtail/bakerydemo) project as the target. Screenshots all use standardized sizes, and a uniform style for highlights on the screen.

Then, upload the new images in the CMS:

1. Bulk-move all images in the "English (latest)" collection to the new collection.
2. Create a new copy of every image in the new collection, assigning it to the "English (latest)" collection
3. Go through all "latest" pages of the site and update them to use the new copies of the images
4. For all pages of the "latest" locale, manually sync translations (without publishing).
5. For all "latest" locales, go through the pages and publish the ones that have no translations missing, so they use the latest images.
