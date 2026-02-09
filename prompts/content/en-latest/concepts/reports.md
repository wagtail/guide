# Reports

Page URL: https://guide.wagtail.org/en-latest/concepts/reports/

> Reports are lists of pages that match a specific search. These lists give you an overview of the different actions taken on your website.

Reports are lists of pages that match a specific search. These lists give you an overview of the different actions taken on your website. For instance, a Report could show you the history of all actions related to the creation and publishing of your pages. This means you can see when users of your [Admin interface](/en-latest/concepts/wagtail-interfaces/) added a page as a draft, submitted it for moderation, published it, and deleted it. You also get to see the users that performed these actions.

By default, Wagtail provides you with Reports on your Locked pages, Workflows, Workflow tasks, Site history, and Aging pages. With the right permission, you can access these Reports by clicking **Reports** from the [Sidebar](/en-latest/how-to-guides/find-your-way-around/) in your [Admin interface](/en-latest/how-to-guides/find-your-way-around/). You can further filter what pages are displayed, and also export these reports in spreadsheet format.

It's also possible that features in the **Reports** section of your [Admin interface](/en-latest/concepts/wagtail-interfaces/) are different from the default features. This is because Wagtail is highly customizable. If this is the case, contact your web developer for more information.

## Locked pages report

The Locked pages Report is one of the default Reports in the [Admin interface](/en-latest/concepts/wagtail-interfaces/). This Report consists of a list of your locked pages. You also get to see the time and date when the pages got locked.

Only users with the right permissions, usually an [Administrator](/en-latest/how-to-guides/manage-users-and-roles/) can access this list.

## Workflows report

Another default Report provided by Wagtail in the [Admin interface](/en-latest/concepts/wagtail-interfaces/) is the Workflows Report. This report shows you the history of all your [Workflows](/en-latest/how-to-guides/configure-workflows-for-moderation/). By accessing this Report you get a list of the [Workflows](/en-latest/how-to-guides/configure-workflows-for-moderation/) you have submitted for moderation, approved Workflows, and cancelled Workflows. Also, you get to see the time and date that the users perform each action.

Unlike Locked pages Reports, Workflows Reports don’t require high-level permissions to access.

## Workflow tasks report

The Workflow tasks report is a Report that shows you the history of actions related to your Workflow tasks. By accessing this Report you get a list of the Workflow tasks that are in progress, approved, or cancelled. You also get to see the time and date that the users perform each action.

Similar to the Workflows Report, you don't require high-level permissions to access the Workflow tasks Report.

## Site history report

The Site history Report provides you with the history of all actions performed on your Wagtail website through the Admin interface. These actions include, but are not limited to the following:

-   Creating, publishing, unpublishing, copying, aliasing, and deleting your pages.
-   Saving your pages as drafts.
-   Locking and unlocking of pages.
-   Creating and editing redirects.

## Aging pages report

Aging pages lists all pages on the site from oldest to newest. This helps content teams understand which pages might need updating.

## Page types usage report

This report provides an overview of all page types in use on the site, each with a count of how many pages it has, and a link to a sample page of that type.

## Search terms report

For sites set up to [promote search results](/en-6.4.x/how-to-guides/promote-search-results/), this report displays all recorded search terms and their number of views.
