# New in Wagtail 5.2

Page URL: https://guide.wagtail.org/en-latest/releases/new-in-wagtail-5-2/

Here are highlights from Wagtail 5.2. For more details, view the full [v5.2 release notes](https://docs.wagtail.org/en/v5.2.3/releases/5.2.html).

## **Redesigned page listing view**

The page explorer listing view has been redesigned to allow improved navigation and searching. Here is an example of the new interface:

![v5.2 redesigned pages listing](https://guide-media.wagtail.org/images/page-listing-redesigned.width-900.png)

This supports searching for pages within a specific section of the site, finding matches across all sub-sections:

![v5.2 pages listing with search](https://guide-media.wagtail.org/images/page-listing-search.width-900.png)

## User interface refinements

Several tweaks have been made to the admin user interface which we hope will make it easier to use.

-   Show the full first published at date within a tooltip on the Page status sidebar on the relative date
-   Do not render minimap if there are no panel anchors
-   Use dropdown buttons on listings in dashboard panels
-   Add compare buttons to workflow dashboard panel
-   Implement breadcrumbs design refinements
-   Add support for Shift + Click behaviour in form submissions and simple translations submissions
-   Improve filtering of audit logging based on the user’s permissions

Here is a screenshot of the "compare" buttons in the workflow panel on the dashboard:

![v5.2 compare buttons highlighted in red on dashboard](https://guide-media.wagtail.org/images/compare-buttons.width-900.png)

## **External links in promoted search results**

Promoted search result entries can now use an external URL along with custom link text, instead of linking to a page within Wagtail. This makes it easier to manage promoted content across multiple websites.

![v5.2 promoted search results external links](https://guide-media.wagtail.org/images/external-links.width-900.png)

## Subject and body for email links

In the link chooser, email links now support setting an email subject and body:

![v5.2 email subject body fields in link chooser modal](https://guide-media.wagtail.org/images/email-subject-body.width-900.png)

## Site-specific improvements

The following two highlights require site-specific configuration. While we expect they will improve editors’ workflow, they need to be set up based on the site’s needs, and may not be visible at all on your website.

### **Wagtail user interface extensions with Stimulus**

Wagtail now officially supports [admin UI customisations with Stimulus](https://docs.wagtail.org/en/latest/extending/extending_client_side.html#extending-client-side). We expect this will make it much simpler for site implementers to customize the administration interface for their project’s needs.

### Content management features beyond pages

Following recent improvements to Snippets, the following content management features can now be set up on arbitrary content/data in the CMS, rather than pages / snippets only:

-   Filtering and export on list / index views, as well as customizations via `list_display`, `list_filter`, `list_export`, `list_per_page`, `ordering`.
-   Standalone Usage, Inspect, History views for arbitrary content/data.
-   Breadcrumbs in admin views.
-   Custom buttons in list/index views.

Here is an example of the Usage, History, and Breadcrumbs as available in Snippets – which will be available for arbitrary content once configured:

![v5.2 snippets editing interface](https://guide-media.wagtail.org/images/snippets-features.width-900.png)
