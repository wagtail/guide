# Page status

Page URL: https://guide.wagtail.org/en-latest/concepts/page-status/

> Page status has to do with the current state of your pages. Your pages can be in one of seven different states.

Page status has to do with the current state of your pages. Your pages can be in one of seven different states. They're as follows:

## Draft

A page is a _Draft_ if it's newly created and saved as a _Draft_. The main takeaway here is that the page is new and you have never published it.

Pages with a _Draft_ status are only available in your [Admin interface](/en-latest/concepts/wagtail-interfaces/) and not on your live website.

## In moderation

A page assumes the status _In moderation_ if you submit a page that you have never published for moderation.

The content of the page becomes available on your website only if a user with the right permissions approves the page. Once another user approves the page, the status changes to Live. By default, [Administrator](/en-latest/how-to-guides/manage-users-and-roles/) and [Moderator](/en-latest/how-to-guides/manage-users-and-roles/) users can approve pages in moderation.

## Scheduled

A page assumes the _Scheduled_ state when you configure it for publication at a later date. The page locks itself until its publication, when it becomes _Live_.

## Expired

The page was Live, and subsequently unpublished because it had an expiry date set that has now passed. See [scheduled publishing](/en-latest/concepts/scheduled-publishing/) for more information.

## Live

A page assumes the _Live_ status if you publish it. This could either be by publishing a newly created page, edits of an existing page, a copied page, or an aliased page.

You can see the content of a _Live_ page on your website.

## Live + Draft

The status of a page becomes _Live + Draft_ if you have previously published it and then save an edit of the page as a draft.

In this instance, the previous version of the page remains available on your website, but the edits made to it won't be available on your website. To make the edits available on your website, the status of the page has to become _Live_. You can achieve this by going to the edit screen of the page and publishing it.

## Live + (another status)

A page could assume the status of _Live + (another status)_ if you have previously published it and then perform another action on the already published page. For instance, a page becomes _Live + In moderation_ if you have published it in the past and then submit an edit of it for moderation.
