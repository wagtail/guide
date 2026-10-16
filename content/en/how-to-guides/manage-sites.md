---
title: 'Manage sites'
description: 'Learn how to manage Wagtail sites: list, add, edit, copy, and delete the site configurations that map hostnames to your page tree.'
last_modified: '2026-10-14'
---

# Manage sites

Page URL: https://guide.wagtail.org/en/how-to-guides/manage-sites/

> Learn how to manage Wagtail sites: list, add, edit, copy, and delete the site configurations that map hostnames to your page tree.

## **About sites**

A site in Wagtail is a configuration that connects a domain name (like "example.org") to a section of the page tree. When a visitor requests a page, Wagtail looks up the site whose domain name matches the request, then uses that site’s root page as the starting point to serve the right content.

Most projects have a single site, but Wagtail also supports [_multi-site_](https://docs.wagtail.org/en/stable/advanced_topics/multi_site_multi_instance_multi_tenancy.html#multi-site) installations, where one admin interface manages the content of several websites. In a multi-site project, you configure one site entry per hostname and point each one at a different root page. See [Multi-site](/en/reference/multi-site/) for more on how multi-site projects work.

## **List sites**

Go to **Settings > Sites** from the [Sidebar](/en/how-to-guides/find-your-way-around/) to see all of the sites configured for your project. The Sites listing shows the following columns for each site:

- **Site**: the hostname the site responds on.
- **Port**: the port number the site responds on.
- **Site name**: a human-readable name for the site.
- **Root page**: the page served at the site’s root URL.
- **Default?**: whether the site is the default site.

You can sort the listing by clicking the column headings, such as **Site** or **Port**.

## **Add a site**

Click **Add a site** in the top-right of the Sites listing to create a new site. Then fill in the following fields:

- **Hostname**: the hostname the site responds on, excluding the scheme, port, and path. For example, *www.example.com*. This field is required.
- **Port**: the port number the site responds on. Set this to something other than 80 if you need a specific port number to appear in URLs (for example, development on port 8000). Set this to 443 for HTTPS. This does not affect request handling, so port forwarding still works. This field is required.
- **Site name**: a human-readable name for the site. Wagtail does not use this itself, but it is suitable for use on the site front-end, such as in page titles.
- **Root page**: the page served at the site’s root URL. Choose the page that should be the home page for this hostname. This field is required.
- **Is default site**: if checked, this site handles requests for all other hostnames that do not have a site entry of their own. Only one site can be the default.

Click **Save** to create the site.

## **Edit a site**

Click the hostname of a site in the Sites listing to open it for editing. The edit screen uses the same fields as the **Add a site** form. Make your changes and click **Save**.

From the edit screen you can also:

- **Copy** the site, which opens the **Add a site** form pre-filled with the existing site’s values. This is useful when setting up a new hostname that is similar to an existing one.
- **Delete** the site, which takes you to a confirmation page before the site is removed.

Warning: Site operations are dangerous and often limited to "superadmin" users only. Deleting a site is permanent and cannot be undone. It removes the site configuration only; the pages in the site’s root page and below are not deleted. Be careful not to delete the default site or a site that is in use.
