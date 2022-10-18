# Test plans

Here are critical parts of the site to test as part of any major event (large new features, infrastructure change, etc).

## Redirects from docs.wagtail.org

The majority of the site’s initial launch content comes from Wagtail’s documentation. We want to make sure all requests to this documentation are correctly redirected to our guide. Here is a script to retrieve all pages we are redirecting to:

```sh
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/intro.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/getting_started.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/finding_your_way_around/index.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/finding_your_way_around/the_dashboard.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/finding_your_way_around/the_explorer_menu.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/finding_your_way_around/using_search.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/finding_your_way_around/the_explorer_page.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/new_pages/index.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/new_pages/selecting_a_page_type.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/new_pages/creating_body_content.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/new_pages/inserting_images.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/new_pages/inserting_links.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/new_pages/inserting_videos.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/new_pages/inserting_documents.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/new_pages/adding_multiple_items.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/new_pages/required_fields.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/new_pages/the_promote_tab.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/new_pages/previewing_and_submitting_for_moderation.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/editing_existing_pages.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/copying_aliasing_existing_pages.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/documents_images_snippets/index.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/documents_images_snippets/documents.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/documents_images_snippets/images.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/documents_images_snippets/snippets.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/documents_images_snippets/collections.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/managing_redirects.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/administrator_tasks/index.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/administrator_tasks/managing_users.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/administrator_tasks/managing_workflows.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/administrator_tasks/promoted_search_results.html | grep location
curl --silent -I https://docs.wagtail.org/en/stable/editor_manual/browser_issues.html | grep location
```

For each URL returned by this script, make sure it resolves with a 200 on the site.

## Site search

1. Go to the homepage.
2. With the keyboard, open the search form by focusing on the header search icon and pressing "Enter".
3. Search for "collections". There should be results.
4. Search for "potato". There should be no results.

## Feedback form

1. Go to the "Browser issues" page.
2. With the keyboard, navigate to the emojis’ feedback form.
3. Press the "happy" emoji.
4. When revealed, add further details in the form field.
5. Submit the form. A success message should appear.
6. In the CMS, note the correct saving of the submitted content.

## Site navigation

1. Go to the homepage
2. With the keyboard, go to the "How-to" page.
3. With the keyboard, go to the first content page within "How-to".
4. With the keyboard, go to the next page.
5. With the keyboard, go back to the previous page.
6. With the keyboard, navigate to the first section under "On this page".

## Content editing and moderation

1. In the CMS, go to the "How-to" page.
2. Edit the first page under "How-to".
3. Preview the page’s contents. The preview should work as expected.
4. Submit the page to the "Moderators’ approval" workflow.
5. Go to the dashboard and "Request changes" on the newly-submitted page.
6. Go to the page editing UI and cancel the workflow.
