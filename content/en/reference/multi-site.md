---
title: 'Multi-site'
description: 'Reference for running multiple websites with Wagtail: how sites map hostnames to pages, and multi-site, multi-instance and multi-tenancy compared.'
last_modified: '2026-10-13'
---

# Multi-site

Page URL: https://guide.wagtail.org/en/reference/multi-site/

> Reference for running multiple websites with Wagtail: how sites map hostnames to pages, and multi-site, multi-instance and multi-tenancy compared.

## **What is multi-site?**

Multi-site is a Wagtail project configuration where you manage the content of several websites from a single admin interface. A multi-site project is a single code repository, on a single server, with a single database and a single media directory. Content can be shared between sites.

Wagtail supports multi-site out of the box. Each site maps a domain name to a separate root page. When a visitor requests a page, Wagtail takes the domain and port from the request, looks up the matching site, and resolves the URL starting from that site’s root page. See [Manage sites](/en/how-to-guides/manage-sites/) for how to configure sites.

## **Multi-site, multi-instance and multi-tenancy**

Wagtail can run in more than one web-hosting arrangement. These terms describe how much is shared or separated between websites.

### **Multi-site**

One instance serves multiple websites, sharing the same database, media, and user accounts. Content can be shared between sites, and permissions can restrict access to specific sites or specific sections of the page tree. This is the arrangement Wagtail supports out of the box, and we recommend considering first, as it is the simplest operationally.

### **Multi-instance**

Here, one set of project files is used by several websites, but each website has its own settings file, database, and media directory, and runs in its own server process. This guarantees total separation of all content, at the cost of running more server processes. This is also supported out of the box. We do not recommend it for most organizations.

#### **Multi-tenancy**

A single instance serves multiple tenants, each with a separate database. This can work with Wagtail but currently requires customizations to.

---

The developer documentation’s [Multi-site, multi-instance and multi-tenancy](https://docs.wagtail.org/en/stable/advanced_topics/multi_site_multi_instance_multi_tenancy.html) provides more information on the trade-offs of each approach.

## **Shared and separated content**

In a multi-site project, the following are shared across all sites:

- User accounts, groups, and permissions.
- The database and media files.
- Snippets, which are global pieces of content.

The following can be separated or restricted per site:

- The page tree, using different root pages and page permissions.
- Images and documents, using collections restricted to specific groups.
- Site settings, which store additional information for a single site, such as social media settings or a logo.

Note: Permission configuration for Sites, site settings, users, and groups is not site-specific. Any user with permission to edit a single entry can edit all of them, so it is usually best to only allow superusers to manage these.
