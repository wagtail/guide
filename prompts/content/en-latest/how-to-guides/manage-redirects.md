# Manage redirects

Page URL: https://guide.wagtail.org/en-latest/how-to-guides/manage-redirects/

> A redirect ensures that when a page is no longer available (404), the visitor and search engines are sent to a new page.

## **About redirects**

In the course of publishing and unpublishing pages, you eventually need to make redirects. A redirect helps send visitors and search engines to a new page if your web page becomes unavailable (404). This way, visitors won’t end up on a broken journey that results in a _page not found_.

Wagtail considers two kinds of configurations for a redirect, depending on whether Permanent remains checked or not:

-   Permanent redirect (checked by default)
-   Temporary redirect

For both redirect configurations, the visitor won’t notice a difference when visiting a page, but search engines react to these two configurations of redirect differently. In the case of a temporary redirect, a search engine keeps track of your old page and indexes the redirected page. However, with a permanent redirect, a search engine marks the old page as obsolete and considers the new page as a replacement.

Note: As a best practice, Wagtail checks redirects as permanent by default. This is to prevent the undermining of your search engine ranking.

## **Configure redirects**

Go to **Settings > Redirects** from the [Sidebar](/en-latest/how-to-guides/find-your-way-around/) to configure redirects. You can create a new redirect and edit or search for an existing one from the Redirects interface.

![Redirects listing with a search field in the header buttons to add and import redirects and rows of existing underneath](https://guide-media.wagtail.org/images/Redirects_listing_with_a_search_field_in_the_h.width-900_v4iFdpb.png)

Search for existing redirects by entering your search term in the search bar. The results automatically update as you type.

## Add redirects

You can create a new redirect by clicking **Add redirect** in the top-right of the [Redirect interface](/en-latest/concepts/wagtail-interfaces/). Then set **Redirect from** to the URL pattern that's no longer available on your website. If your Wagtail is _multisite_, set the **From site** to the website that has the unavailable URL pattern.

By default, Wagtail sets a redirect to a _permanent_ _redirect_. Configure your redirect as a temporary one by unchecking the **Permanent** checkbox.

**Redirect to a page** allows you to redirect visitors and search engines to a new page within Wagtail, while the **Redirect to any URL** field allows you to redirect to a different domain outside of Wagtail.

## Edit redirects

Edit the details of an existing redirect by clicking the URL path of the redirect you want to configure on the [Redirect interface](/en-latest/concepts/wagtail-interfaces/).

![Editing form for a redirect with from fields Site field permanent checkbox and destination fields for page and URL options](https://guide-media.wagtail.org/images/Editing_form_for_a_redirect_with_from_fields_S.width-900_HxQifuJ.png)

## Delete redirects

This can also be done from the edit interface.

## Import and export redirects

From the Redirects interface, users can also:

-   Import new redirects from a CSV file (by default with "from" and "to" columns for each row)
-   Export existing redirects as CSV or XLSX

Note: Keep in mind that a redirect only initiates if the page is not found. It doesn't apply to existing pages (200), which resolves on your site.
